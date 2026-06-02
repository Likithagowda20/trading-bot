from bot.logging_config import logger
from bot.validators import validate_order_type, validate_price, validate_quantity, validate_side, validate_symbol


def format_response(response: dict) -> str:
    order_id = response.get('orderId')
    status = response.get('status')
    executed_qty = response.get('executedQty')
    avg_price = response.get('avgPrice', 'N/A')

    lines = [
        f'orderId: {order_id}',
        f'status: {status}',
        f'executedQty: {executed_qty}',
        f'avgPrice: {avg_price}',
    ]
    return '\n'.join(lines)


def place_order(client, symbol: str, side: str, order_type: str, quantity: str, price: str = None) -> dict:
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)

    if order_type == 'LIMIT':
        if price is None:
            raise ValueError('Price is required for LIMIT orders.')
        price = validate_price(price)

    request_summary = (
        f'Order request summary:\n'
        f'  symbol: {symbol}\n'
        f'  side: {side}\n'
        f'  type: {order_type}\n'
        f'  quantity: {quantity}\n'
        + (f'  price: {price}\n' if price is not None else '')
    )
    logger.info(request_summary)
    print(request_summary)
    response = client.place_order(symbol, side, order_type, quantity, price)

    # If the exchange returns an orderId, attempt to fetch the authoritative order status
    order_id = response.get('orderId')
    if order_id:
        try:
            updated = client.get_order(symbol, order_id)
            response = updated
        except Exception as exc:
            logger.warning('Could not fetch updated order status: %s', exc)

    # If avgPrice is missing or zero, try to compute from fills
    avg_price = response.get('avgPrice')
    executed_qty = response.get('executedQty')
    if (not avg_price or str(avg_price).startswith('0')) and response.get('fills'):
        fills = response.get('fills')
        try:
            total_qty = sum(float(f.get('qty', 0)) for f in fills)
            if total_qty > 0:
                weighted = sum(float(f.get('price', 0)) * float(f.get('qty', 0)) for f in fills)
                avg_price = str(weighted / total_qty)
                executed_qty = str(total_qty)
                response['avgPrice'] = avg_price
                response['executedQty'] = executed_qty
        except Exception:
            logger.debug('Failed to compute avgPrice from fills', exc_info=True)

    output = format_response(response)
    print('Order response details:')
    print(output)
    print('Order placed successfully.' if response.get('orderId') else 'Order placement failed.')
    return response
