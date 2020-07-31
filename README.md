# Oanda-EMA-Strategy
A simple EMA Crossover Strategy trading algorithm made with Oanda's Rest v20 API. This was made primarily as a learning tool and to be used on a paper trading account.<br/>

Begins trading once first crossover occurs after program has been started. When the fast period EMA crosses above the long period EMA, any short positions are closed and a long order is executed; vice versa when crossing below.

## Installation
Simply clone or download the zip for the source code to save to your device.

## Usage
Put in your API Key and Account ID into configs.py and change any settings regarding the strategy as you see fit. All parameters must be in quotes (e.g. UNITS='10000').

- INSTRUMENT - the instruments you want to trade seperated with an underscore (e.g. 'EUR_USD', 'USD_JPY', etc)

- GRANULARITY - The timeframe of the candlesticks you want to trade at (e.g. 'M1' for 1 minute, 'D' for 1 day, etc).<br/>
              For all granularity options: https://developer.oanda.com/rest-live-v20/instrument-df/
              
- FAST and SLOW - the EMA periods you want to use

- UNITS - the number of units to buy or sell per trade

- TIME_IN_FORCE - instructions for the active period of an order before executed or expired; default='FOK' (Filled or Killed).<br/>
                For Time in Force all options: https://developer.oanda.com/rest-live-v20/order-df/
                
Run in your desired terminal. When a trade is made, it will be logged in the terminal as well as to a file named LOG.log.<br/>
Logs will contain the datetime, bid/ask price, and the mid price (for spread info) for all orders. In addition, P/L will be logged once a trade is closed. For example:<br/>
07/31/2020 09:03:02 AM: SELL -10000 units at bid: 1.18406 mid: 1.18412<br/>
07/31/2020 10:08:03 AM: CLOSE 10000 units at ask: 1.18319 mid: 1.183125<br/>
07/31/2020 10:08:03 AM: P/L 8.7000

## Contributing
Feel free to send a pull request.

## License
[MIT](https://choosealicense.com/licenses/mit/)
