import json

# Your API Key
API_KEY = 'Bearer YOUR_KEY_HERE'

ACCOUNT_ID = 'YOUR_ACCOUNT_ID_HERE'

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': API_KEY
    }

# format: 'Currency1_Currency2'
INSTRUMENT = 'EUR_USD'

# Candlestick timeframe - https://developer.oanda.com/rest-live-v20/instrument-df/ for options
GRANULARITY = 'M1'

# EMA Periods
FAST = 1
SLOW = 2

# Order Settings - https://developer.oanda.com/rest-live-v20/order-df/ for options
UNITS = '1'
TIME_IN_FORCE = 'FOK'


BUY = json.dumps({
  "order": {
    "timeInForce": TIME_IN_FORCE,
    "instrument": INSTRUMENT,
    "units": UNITS,
    "type": "MARKET",
    "positionFill": "DEFAULT"
  }
})
SELL = json.dumps({
  "order": {
    "timeInForce": TIME_IN_FORCE,
    "instrument": INSTRUMENT,
    "units": '-' + UNITS,
    "type": "MARKET",
    "positionFill": "DEFAULT"
  }
})