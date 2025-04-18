import backtrader as bt
import yfinance as yf

class RubberBandStrategy(bt.Strategy):
    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(self.data.close, period=60, devfactor=1.5)
        self.stoplossband = bt.indicators.BollingerBands(self.data.close, period=60, devfactor=2)
        """     self.setsizer(bt.sizers.AllInSizer)     """
        
    def notify_status(self, order):
        if (order.status in bt.Order.Completed):
            print(f"Order Completed: {order.executed.price} for number of shares: {order.executed.size}")

    # Strategy
    def next(self):
        # When should we buy the stock?
        if self.data.close[0] <= self.bollinger.lines.bot[0] and not self.position:
            """
            If the closing price of the stock is lower than the bottom bollinger band,
            We should purchase the stock.
            """
            self.buy(exectype=bt.Order.Market)
            print(f"Buy order created for price: ~{self.data.close[0]} on date: {self.data.datetime.date()}")
            print(f"Real price {self.data.close[1]}")
            # if the stock drops, when should we sell the stock? Stop loss
            self.stoploss = self.stoplossband.lines.bot[0]
        # When should we sell the stock?
        else:
            """
            If the closing price of the stock is higher than the middle bollinger band,
            We should sell the stock. 
            """
            if self.data.close[0] > self.bollinger.lines.mid[0]:
                """
                At this point, there's 2 possibilities:
                    1. We have a position and the middle bollinger band is higher than the original buy price. [Gain]
                    2. We have a position and the middle bollinger band is lower  than the original buy price. [Loss]
                """
                # 1st Case: We should sell here and lock in our gain. Instead, we will update our stop loss.
                # Result could lower our gain if the stock price drops. But we can also ride the wave if the stock price increases.
                if self.position:
                    if self.data.close[0] > self.stoploss:
                        # Update trailing stop loss
                        self.stoploss = max((self.data.close[0] - self.position.price)*0.75 + self.position.price, self.stoploss)
                        print(f"Stop Loss Updated: {self.stoploss}")
                    else: # 2nd Case: We've lost money. Sell before it drop anymore.
                        print(f"Stop Loss Triggered: {self.stoploss}")
                        self.sell(exectype=bt.Order.Market)
                        print(f"Sell order created for price: ~{self.data.close[0]} on date: {self.data.datetime.date()}")

            # Added for when close is larger than purchase price but less than middle bollinger band

            # elif (self.data.close[0] > self.position.price) and (self.data.close[0] < self.bollinger.lines.mid[0]):
            #     self.stoploss = max((self.data.close[0] - self.position.price)*0.75 + self.position.price, self.stoploss)
            #     if self.data.close[0] > self.stoploss:
            #         # Update trailing stop loss
            #         self.stoploss = max((self.data.close[0] - self.position.price)*0.75 + self.position.price, self.stoploss)
            #         print(f"Stop Loss Updated: {self.stoploss}")
            #     else:
            #         print(f"Stop Loss Triggered: {self.stoploss}")
            #         self.sell(exectype=bt.Order.Market)
            #         print(f"Sell order created for price: ~{self.data.close[0]} on date: {self.data.datetime.date()}")


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(RubberBandStrategy)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=90) # 90% of cash for tests
    data = yf.download('goog', start='2024-01-01', period='1d')
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.broker.setcash(5000)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    results = cerebro.run()

    # Get the Sharpe Ratio
    sharpe_ratio = results[0].analyzers.sharpe.get_analysis()
    print(f"Sharpe Ratio: {sharpe_ratio['sharperatio']}")

    print(f"Start Cash {cerebro.broker.startingcash}")
    print(f"End Cash {cerebro.broker.getvalue()}")
    cerebro.plot()