import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf

weights = pd.read_excel("holdings.xlsx", index_col = 0)
tickers = list(weights.index)
allocation = weights['share_count']

start = dt.datetime(2019,2,19)
end = dt.datetime.today()

'''
daily_prices = yf.download(tickers, start, end)['Close']
monthly_prices = yf.download(tickers, start, end, interval = "1mo")['Close'].dropna()

#we want to make a monthly_portfolio that is empty but with the same index and column as our monthly prices
monthly_portfolio = pd.DataFrame(columns = tickers, index = monthly_prices.index)

#we want to through each stock
for i in tickers:
    
    #we want to get our allocation size
    share_count = allocation[i]
    
    #we want to loop through the prices of the stock
    for j in monthly_prices.index:
        
        #get the price
        price = monthly_prices[i][j]
        
        #multiply prices by number of shares
        monthly_portfolio[i][j] = share_count * price
'''

#get the monthly price
daily_prices = yf.download(tickers, start, end)['Close'].dropna()

#we want to make a monthly_portfolio that is empty but with the same index and column as our monthly prices
daily_portfolio = pd.DataFrame(columns = tickers, index = daily_prices.index)

#we want to through each stock
for i in tickers:
    
    #we want to get our allocation size
    share_count = allocation[i]
    
    #we want to loop through the prices of the stock
    for j in daily_prices.index:
        
        #get the price
        price = daily_prices[i][j]
        
        #multiply prices by number of shares
        daily_portfolio[i][j] = share_count * price
 
#this is going to make the portfolio value for each day
daily_portfolio["value"] = daily_portfolio.sum(axis=1)

pie = weights.reset_index().drop(columns = ["share_count", "start_date"])
pie.columns = ["ticker"]

final_val = daily_portfolio["value"][len(daily_portfolio) - 1] 

for counter, i in enumerate(daily_portfolio.columns[:-1]):
    
    weight = daily_portfolio[i][len(daily_portfolio) - 1] / final_val
    
    print(weight)
    
    #pie['weight'][counter] = round(weight ,2)
    
