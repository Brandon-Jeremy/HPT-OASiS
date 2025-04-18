import backtrader as bt

class MaxCashSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy: # isBuy is set to True => Buying
            if data.close[0] * (1+comminfo.p.percents) < cash:
                return cash // data.close[0] * (1+comminfo.p.percents) # Return the number of shares to buy            
        else: #isBuy is set to False => Selling
            return self.broker.positions[data].size # Return the number of shares to sell [Sell Everything]