import pandas as pd
import datetime as dt
import yfinance as yf
import streamlit as st

class DashTools():
    
    def __init__(self):
        
        #we have to make dataframe by hand becuase everything will run from github so no directory    
        self.weights = pd.read_excel("holdings.xls", index_col = 0)
            
        #get tickers
        self.tickers = sorted(list(self.weights.index))
        
        #turns this into a pd.series with tickers as index and number of shares as value
        self.share_count = self.weights['share_count']
            
        #grab todays date
        self.end_date = dt.datetime.today()
        
        #the cost basis day provided from LITG
        self.start_date = dt.datetime(2019,2,19)
        
        #get update time
        self.update_date = self.end_date.strftime("%a %D %I:%M %p") 
        
        #get daily_prices
        self.daily_prices = yf.download(self.tickers, self.start_date, self.end_date)['Close'].dropna()
        
        #this will make a dataframe with all of the columns being the value of the stock and the last columnn will be the value of the fund
        #becasue it takes a lot of work to make this dataframe create a function for defining the variable
        self.daily_portfolio = self.make_daily_portfolio()
    
    #this function will make the portfolio
    def make_daily_portfolio(self):
        
        #iniitalize a dataframe 
        daily_portfolio = pd.DataFrame(columns = self.tickers, index = self.daily_prices.index)
        
        #the goal here is to multiply all of the cells which are prices by the number of shares
        
        #we are going to go through each column at a time
        for i in self.tickers:
            
            #grab the number of shares
            share_count = self.share_count[i]
            
            #now go through the price of the stock for each day
            for j in range(len(self.daily_prices[i])):
                
                #get the price of the stock
                price = self.daily_prices[i][j]
                
                #multiply the price of the stock by the number of shares and put that into the daily_portfolio
                daily_portfolio[i][j] = round(price * share_count,2)
        
        #this will sum of the value of each stock to get a final portfolio value
        daily_portfolio["value"] = daily_portfolio.sum(axis = 1)
        
        #now output that back out 
        return daily_portfolio
    
    def make_monthly_portfolio(self):
        
        #get monthly prices
        monthly_prices = yf.download(self.tickers, self.start_date, self.end_date, interval = "1mo")['Close'].dropna()
        
        #we want to make a monthly_portfolio that is empty but with the same index and column as our monthly prices
        monthly_portfolio = pd.DataFrame(columns = self.tickers, index = monthly_prices.index)
        
        #we want to through each stock
        for i in self.tickers:
            
            #we want to get our allocation size
            share_count = self.share_count[i]
            
            #we want to loop through the prices of the stock
            for j in monthly_prices.index:
                
                #get the price
                price = monthly_prices[i][j]
                
                #multiply prices by number of shares
                monthly_portfolio[i][j] = share_count * price
            
        return monthly_portfolio
            
        
        
        