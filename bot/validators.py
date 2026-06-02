from enum import Enum

class OrderSide(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderType(str, Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.isalnum():
        raise ValueError('Symbol must be an alphanumeric string, e.g. BTCUSDT.')
    return symbol.upper()


def validate_side(side: str) -> str:
    try:
        return OrderSide[side.upper()].value
    except KeyError:
        raise ValueError('Side must be BUY or SELL.')


def validate_order_type(order_type: str) -> str:
    try:
        return OrderType[order_type.upper()].value
    except KeyError:
        raise ValueError('Order type must be MARKET or LIMIT.')


def validate_quantity(quantity: str) -> str:
    try:
        q = float(quantity)
    except ValueError:
        raise ValueError('Quantity must be a numeric value.')
    if q <= 0:
        raise ValueError('Quantity must be greater than zero.')
    return str(q)


def validate_price(price: str) -> str:
    try:
        p = float(price)
    except ValueError:
        raise ValueError('Price must be a numeric value.')
    if p <= 0:
        raise ValueError('Price must be greater than zero.')
    return str(p)
