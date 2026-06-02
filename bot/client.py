import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from bot.logging_config import logger


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://testnet.binancefuture.com'):
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        self.time_offset_ms = 0
        self._sync_server_time()

    def _get_server_time(self) -> int:
        url = f'{self.base_url}/fapi/v1/time'
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return int(data['serverTime'])

    def _sync_server_time(self):
        try:
            server_time = self._get_server_time()
            local_time = int(time.time() * 1000)
            self.time_offset_ms = server_time - local_time
            logger.info('Synchronized time offset: %sms', self.time_offset_ms)
        except requests.exceptions.RequestException as exc:
            logger.warning('Failed to sync server time: %s', exc)
            self.time_offset_ms = 0

    def _sign_payload(self, payload: dict) -> str:
        query_string = urlencode(payload, doseq=True)
        signature = hmac.new(self.api_secret, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return f'{query_string}&signature={signature}'

    def place_order(self, symbol: str, side: str, order_type: str, quantity: str, price: str = None) -> dict:
        path = '/fapi/v1/order'
        url = f'{self.base_url}{path}'

        payload = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'timestamp': int(time.time() * 1000) + self.time_offset_ms,
            'recvWindow': 5000,
        }

        if order_type == 'LIMIT':
            payload['price'] = price
            payload['timeInForce'] = 'GTC'

        signed_payload = self._sign_payload(payload)
        logger.info('Sending order request: %s', payload)

        response = None
        try:
            response = self.session.post(url, data=signed_payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.info('Order response: %s', data)
            return data
        except requests.exceptions.HTTPError as exc:
            body = response.text if response is not None else 'no response body'
            logger.error('Binance HTTP error %s: %s', exc, body)
            raise RuntimeError(f'Binance API error: {exc} - {body}') from exc
        except requests.exceptions.RequestException as exc:
            message = f'Network/API error while placing order: {exc}'
            logger.error(message)
            raise
        except ValueError:
            logger.error('Received invalid JSON response from Binance.')
            raise

    def get_order(self, symbol: str, orderId: int) -> dict:
        """Fetch a single order status by orderId for the given symbol."""
        path = '/fapi/v1/order'
        url = f'{self.base_url}{path}'

        payload = {
            'symbol': symbol,
            'orderId': orderId,
            'timestamp': int(time.time() * 1000) + getattr(self, 'time_offset_ms', 0),
            'recvWindow': 5000,
        }

        signed = self._sign_payload(payload)
        full_url = f'{url}?{signed}'
        response = None
        try:
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info('Get order response: %s', data)
            return data
        except requests.exceptions.HTTPError as exc:
            body = response.text if response is not None else 'no response body'
            logger.error('Binance HTTP error on get_order %s: %s', exc, body)
            raise RuntimeError(f'Binance API error: {exc} - {body}') from exc
        except requests.exceptions.RequestException as exc:
            logger.error('Network error on get_order: %s', exc)
            raise
