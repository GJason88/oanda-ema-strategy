import requests
import pandas as pd
import json
from configs import API_KEY, ACCOUNT_ID, HEADERS, INSTRUMENT, GRANULARITY, FAST, SLOW, BUY, SELL
import btalib
import logging
import json

class Strategy:
    '''Class for EMA Crossover Strategy'''

    def __init__(self):
        '''Init function to initialize logger, variables for trading, and previous EMA for continuing data'''
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p', level=logging.CRITICAL, handlers=[
            logging.FileHandler("LOG.log"),
            logging.StreamHandler()
            ])
        
        self.last_completed_candle = requests.get("https://api-fxpractice.oanda.com/v3/instruments/{}/candles?count=2&price=M&granularity={}".format(INSTRUMENT, GRANULARITY), headers=HEADERS).json()['candles'][0]
        self.in_long = False
        self.in_short = False
        self.begin_trading = False
        self.fast = 0
        self.slow = 0

        # initialize prev EMAs with last 5000 candlesticks of data to use for live price EMA calculations
        prev_data = requests.get("https://api-fxpractice.oanda.com/v3/instruments/{}/candles?count=5000&price=M&granularity={}".format(INSTRUMENT, GRANULARITY), headers=HEADERS).json()['candles'][:-2]
        prev_data_df = pd.DataFrame([float(candle['mid']['c']) for candle in prev_data], columns=['close'])
        self.prev_fast = btalib.ema(prev_data_df, period=FAST, _seed=prev_data_df['close'].iloc[0]).df['ema'].iloc[-1]
        self.prev_slow = btalib.ema(prev_data_df, period=SLOW, _seed=prev_data_df['close'].iloc[0]).df['ema'].iloc[-1]


    def calc_ema(self, period, prev_ema, last_close_price):
        '''Calculates the current EMA given a close price and the previous EMA'''
        return (last_close_price - prev_ema) * (2 / (period + 1)) + prev_ema


    def get_last_x_closes(self, num):
        '''Gets a dictionary of the last X candlestick data from Oanda'''
        return requests.get("https://api-fxpractice.oanda.com/v3/instruments/{}/candles?count={}&price=M&granularity={}".format(INSTRUMENT, num, GRANULARITY), headers=HEADERS).json()


    def calc_emas(self):
        '''Calculates the fast and slow EMAs for trading'''
        last_close = float(self.get_last_x_closes(2)['candles'][0]['mid']['c'])

        # Calculate EMAs of last closed candlestick
        self.fast = self.calc_ema(FAST, self.prev_fast, last_close)
        self.slow = self.calc_ema(SLOW, self.prev_slow, last_close)

        # print(str(self.fast) + ' ' + str(self.slow) + ' ' + str(self.prev_fast) + ' ' + str(self.prev_slow))

        # check if first cross has occurred to begin trading
        if (not self.begin_trading):
            if ((self.prev_fast > self.prev_slow and self.fast < self.slow) or (self.prev_fast < self.prev_slow and self.fast > self.slow)):
                self.begin_trading = True

        # set prev EMAs to current EMAs for next candlestick's calculation
        self.prev_fast = self.fast
        self.prev_slow = self.slow


    def get_current_ask(self):
        '''Gets the current ask price of the instrument'''
        return float(requests.get("https://api-fxpractice.oanda.com/v3/instruments/{}/candles?count=1&price=A&granularity={}".format(INSTRUMENT, GRANULARITY), headers=HEADERS).json()['candles'][0]['ask']['c'])


    def get_current_bid(self):
        '''Gets the current bid price of the instrument'''
        return float(requests.get("https://api-fxpractice.oanda.com/v3/instruments/{}/candles?count=1&price=B&granularity={}".format(INSTRUMENT, GRANULARITY), headers=HEADERS).json()['candles'][0]['bid']['c'])


    def make_trades(self):
        '''Handles trading when the conditions apply'''
        # if fast is greater than slow
        if self.fast > self.slow:
            if self.in_short:
                r = requests.put("https://api-fxpractice.oanda.com/v3/accounts/{}/positions/{}/close".format(ACCOUNT_ID, INSTRUMENT), headers=HEADERS, data=json.dumps({'shortUnits':'ALL'})).json()
                self.in_short = False
                mid = (float(r['shortOrderFillTransaction']['fullPrice']['bids'][0]['price']) + float(r['shortOrderFillTransaction']['fullPrice']['asks'][0]['price']))/2
                logging.critical('CLOSE ' + INSTRUMENT + ' ' + json.loads(BUY)['order']['units'] + ' units at ask: ' + r['shortOrderFillTransaction']['price'] + ' mid: ' + str(mid))
                logging.critical('P/L ' + r['shortOrderFillTransaction']['pl'])
            if not self.in_long:
                r = requests.post("https://api-fxpractice.oanda.com/v3/accounts/{}/orders".format(ACCOUNT_ID), headers=HEADERS, data=BUY).json()           
                self.in_long = True
                mid = (float(r['orderFillTransaction']['fullPrice']['bids'][0]['price']) + float(r['orderFillTransaction']['fullPrice']['asks'][0]['price']))/2
                logging.critical('BUY ' + INSTRUMENT + ' ' + json.loads(BUY)['order']['units'] + ' units at ask: ' + r['orderFillTransaction']['price'] + ' mid: ' + str(mid))

        # if fast is less than slow and in trade
        if self.fast < self.slow:
            if self.in_long:
                r = requests.put("https://api-fxpractice.oanda.com/v3/accounts/{}/positions/{}/close".format(ACCOUNT_ID, INSTRUMENT), headers=HEADERS, data=json.dumps({'longUnits':'ALL'})).json()
                self.in_long = False
                mid = (float(r['longOrderFillTransaction']['fullPrice']['bids'][0]['price']) + float(r['longOrderFillTransaction']['fullPrice']['asks'][0]['price']))/2
                logging.critical('CLOSE ' + INSTRUMENT + ' ' + json.loads(SELL)['order']['units'] + ' units at bid: ' + r['longOrderFillTransaction']['price'] + ' mid: ' + str(mid))
                logging.critical('P/L ' + r['longOrderFillTransaction']['pl'])
            if not self.in_short:
                r = requests.post("https://api-fxpractice.oanda.com/v3/accounts/{}/orders".format(ACCOUNT_ID), headers=HEADERS, data=SELL).json()
                self.in_short = True
                mid = (float(r['orderFillTransaction']['fullPrice']['bids'][0]['price']) + float(r['orderFillTransaction']['fullPrice']['asks'][0]['price']))/2
                logging.critical('SELL ' + INSTRUMENT + ' ' + json.loads(SELL)['order']['units'] + ' units at bid: ' + r['orderFillTransaction']['price'] + ' mid: ' + str(mid))                       


    def on_candle_close(self, last):
        '''Handles functions for every next candle closed'''
        # check if the current candle has ended, if so, assign it to last_completed_candle
        if last != self.last_completed_candle:
            self.last_completed_candle = last
            self.calc_emas()
            if (self.begin_trading):
                self.make_trades()
    

if __name__ == '__main__':
    strategy = Strategy()
    
    # get streaming prices, every time a price is updated or heartbeat occurs (every 5 seconds)
    response = requests.get("https://stream-fxpractice.oanda.com/v3/accounts/{}/pricing/stream?instruments={}".format(ACCOUNT_ID, INSTRUMENT), headers={'Authorization': API_KEY}, stream=True)

    for line in response.iter_lines():
        # filter out keep-alive new lines
        if line:
            latest = requests.get("https://api-fxpractice.oanda.com/v3/accounts/{}/candles/latest?candleSpecifications={}:{}:M".format(ACCOUNT_ID, INSTRUMENT, GRANULARITY), headers={
            'Content-Type': 'application/json',
            'Authorization': API_KEY}).json()
            strategy.on_candle_close(latest['latestCandles'][0]['candles'][0])
            