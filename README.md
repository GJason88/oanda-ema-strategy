# Oanda-EMA-Strategy
A simple EMA Crossover Strategy trading algorithm made with Oanda's Rest v20 API. This was made primarily as a learning tool and to be used on a paper trading account.

## Installation
Simply clone or download the zip for the project to save to your device.

## Usage
Put in your API Key and Account ID into configs.py and change any settings regarding the strategy as you see fit. All parameters must be in quotes (e.g. UNITS='10000').
INSTRUMENT - the instruments you want to trade seperated with an underscore (e.g. 'EUR_USD', 'USD_JPY', etc)
GRANULARITY - The timeframe of the candlesticks you want to trade at (e.g. 'M1' for 1 minute, 'D' for 1 day, etc). 
              For all granularity options: https://developer.oanda.com/rest-live-v20/instrument-df/
FAST and SLOW - the EMA periods you want to use
UNITS - the number of units to buy or sell per trade
TIME_IN_FORCE - instructions for the active period of an order before executed or expired; default='FOK' (Fill or Killed). 
                For Time in Force all options: https://developer.oanda.com/rest-live-v20/order-df/

## Contributing
Feel free to send a pull request.

## License
[MIT](https://choosealicense.com/licenses/mit/)
