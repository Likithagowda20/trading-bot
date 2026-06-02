import argparse
import os
import sys

from dotenv import load_dotenv
from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.logging_config import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description='Binance Futures Testnet trading bot CLI.'
    )
    parser.add_argument('--symbol', required=True, help='Trading symbol, e.g. BTCUSDT')
    parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side: BUY or SELL')
    parser.add_argument('--type', required=True, choices=['MARKET', 'LIMIT'], help='Order type: MARKET or LIMIT')
    parser.add_argument('--quantity', required=True, help='Order quantity')
    parser.add_argument('--price', help='Limit order price (required for LIMIT)')
    parser.add_argument('--api-key', help='Binance Futures testnet API key')
    parser.add_argument('--api-secret', help='Binance Futures testnet API secret')
    parser.add_argument('--base-url', default='https://testnet.binancefuture.com', help='Binance Futures testnet base URL')
    return parser.parse_args()


def load_api_credentials(args):
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    if not api_key or not api_secret:
        raise ValueError(
            'API credentials are required. Provide --api-key and --api-secret, set BINANCE_API_KEY and BINANCE_API_SECRET, or add them to a .env file.'
        )
    return api_key, api_secret


def main():
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path=dotenv_path)
        args = parse_args()
        api_key, api_secret = load_api_credentials(args)

        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret, base_url=args.base_url)
        place_order(client, args.symbol, args.side, args.type, args.quantity, args.price)
    except Exception as exc:
        logger.error('Execution failed: %s', exc)
        print(f'Error: {exc}')
        sys.exit(1)


if __name__ == '__main__':
    main()
