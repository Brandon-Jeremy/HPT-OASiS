import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt

class RubberBandStrategy(bt.Strategy):
    def __init__(self):
        self.funds = cerebro.broker.getvalue()
        self.bollinger = bt.indicators.BollingerBands(self.data.close, period=60, devfactor=2)
        self.stoplossband = bt.indicators.BollingerBands(self.data.close, period=60, devfactor=2.5)
        self.dataclose = self.data.close

    def buyLog(self, price, shares):
        print(f"Buy order Created for price: {price} and shares: {shares} on date: {self.data.datetime.date()}")
    
    def sellLog(self, price, shares):
        print(f"Sell order Created for price: {price} and shares: {shares} on date: {self.data.datetime.date()}")

    def next(self):        
        # Defines region fo purchasing the stock. 
        # If stock closing price is lower than bottom bollinger band, create a buy order at that price.
        if self.data.close[0] < self.bollinger.lines.bot[0]:
            if self.funds > 0 and self.position.size == 0:
                self.num_shares = self.funds // self.data.close[0] 
                self.buyLog(self.data.close[0], self.num_shares)
                self.buy(size=self.num_shares, price=self.data.close[0])
                self.funds = cerebro.broker.getvalue()
                # After purchasing the stock, we need to set the stop loss
                self.sell_stop = self.stoplossband.lines.bot[0]

        elif self.data.close[0] > self.bollinger.lines.mid[0]:
            # If we hold a position
            if self.position.size > 0:
                if(self.data.close[0] > self.sell_stop): # Not time to sell. I'm still over stop loss.
                    if(self.data.close[0] > self.position.price): # Profit has been made
                        # Updated Stop Loss
                        self.sell_stop = max((self.data.close[0] - self.position.price)/1.1 + self.position.price, self.sell_stop)
                        print(f"Stop Loss Updated: {self.sell_stop}")
                else: # self.data.close[0] < self.sell_stop:
                    print(f"Stop Loss Triggered: {self.sell_stop}")
                    self.sellLog(self.data.close[0], self.position.size)
                    self.sell(size=self.position.size, price=self.data.close[0])
                    self.funds = cerebro.broker.getvalue()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(RubberBandStrategy)

    data = yf.download('BBAI', start='2024-04-01')
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.broker.setcash(5000)
    cerebro.run()
    print(f"End Cash {cerebro.broker.getvalue()}")
    cerebro.plot()