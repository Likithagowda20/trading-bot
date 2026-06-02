# Binance Futures Testnet Trading Bot

A simplified Python trading bot for Binance Futures Testnet (USDT-M). It supports placing MARKET and LIMIT orders via a CLI, with structured code, logging, and validation.

## Project Structure

- `bot/`
  - `client.py` - Binance Futures REST client wrapper
  - `orders.py` - order validation and placement logic
  - `validators.py` - user input validation
  - `logging_config.py` - logging setup to file and console
- `cli.py` - command-line entry point
- `requirements.txt` - runtime dependencies
- `logs/` - sample order logs and runtime log file

## Setup

1. Create and activate a Python 3 environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Provide your Binance Futures Testnet credentials.

Option A: use environment variables

Windows PowerShell:

```powershell
$env:BINANCE_API_KEY = 'your_testnet_api_key'
$env:BINANCE_API_SECRET = 'your_testnet_api_secret'
```

Linux / macOS:

```bash
export BINANCE_API_KEY='your_testnet_api_key'
export BINANCE_API_SECRET='your_testnet_api_secret'
```

Option B: use a `.env` file

Copy `.env.example` to `.env` in the project root, then replace the placeholders with your testnet credentials:

```text
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

The CLI will automatically load `.env` from the project root.

## Run Examples

Place a MARKET order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

The default endpoint is now the Binance Futures Testnet endpoint:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

If you want to override it, add `--base-url`.

Place a LIMIT order:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 31000
```

You can also pass credentials explicitly:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --api-key YOUR_KEY --api-secret YOUR_SECRET
```

## Assumptions

- The application uses Binance Futures Testnet endpoint: `https://testnet.binancefuture.com`.
- LIMIT orders require a price and will use `GTC` time in force.
- Authentication is provided via CLI or environment variables.

## Logging

- Logs are written to `logs/trading_bot.log`.
- Sample order logs are included in `logs/market_order.log` and `logs/limit_order.log`.

## Notes

- The bot uses direct REST calls and HMAC SHA256 signing.
- Error handling covers invalid input, missing credentials, and request failures.
