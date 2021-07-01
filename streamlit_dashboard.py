import time
import pandas as pd
import yfinance as yf
import datetime as dt
import plotly.express as px
import matplotlib.pyplot as plt

import streamlit as st

st.set_page_config(layout="wide")


while True:
    
    #we have to make dataframe by hand becuase everything will run from github so no directory
    
    #adding in tickers
    index_col = ["ABMD", "MO", "BERY", "BLK", "AVGO", "CTVA", "DOW", "DD", "HCA", "JCI", "MPC",
                 "MKC", "MCD", "MSFT", "OKE", "O", "SRE", "TJX", "UNH", "URI", "VZ", "QQQ", "IJT", "REZ"]
    
    #adding in share cout
    share_count = [18, 14, 18, 20, 410, 3, 5, 3, 52, 79, 8, 18, 119, 313, 11, 35, 25, 25, 
                   19, 85, 94, 6, 14, 26]
    
    weights = pd.DataFrame(index = index_col)
    weights['share_count'] = share_count

    #get tickers
    tickers = list(weights.index)
    
    #get number of shares
    allocation = weights['share_count']
        
    #grab todays date
    end_date = dt.datetime.today()
    
    #the cost basis day provided from LITG
    start_date = dt.datetime(2019,2,19)
    
    #get update time
    update_date = end_date.strftime("%a %D %I:%M %p")
    
    #show last time we updted
    st.title("Leed's Investment Trading Group Fund (last updated: {})".format(update_date))
    
    #make top columns
    top_col1, top_col2, top_col3 = st.beta_columns(3)
    
    #the portfolio value
    with top_col1:
        
        #output header
        st.subheader("Portfolio Value")
        
        #get the monthly price
        monthly_prices = yf.download(tickers, start_date, end_date, interval = "1mo")['Close'].dropna()
        
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
        
        #plot the data
        st.bar_chart(monthly_portfolio)
        
    #the diversification pie chart
    with top_col2:
        
        #output header
        st.subheader("Portfolio Diversification")
        
        #get the monthly price
        daily_prices = yf.download(tickers, start_date, end_date)['Close'].dropna()
        
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
                daily_portfolio[i][j] = daily_prices * price
    
        #make a new dataframe for the pie chart
        pie = weights.reset_index()
        
        #rename columns
        pie.columns = ["ticker", "weight"]
        
        #set up the pie chart
        diversification_pie = px.pie(weights, values = pie["weight"], names = pie["ticker"])
        st.plotly_chart(diversification_pie)
    
    #the returns
    with top_col3:
        
        st.write(daily_portfolio)
        
        '''
        daily_change = daily_portfolio['value'].pct_change()
        st.write(daily_change[len(daily_change - 1)])
        '''
        '''
        #output header
        st.markdown("<h1 style='text-align: center; color: white;'>Daily Returns: {}%</h1>".format(0.1), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Weekly Returns</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Yearly Returns</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>YTD Returns:</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Since Conception</h1>", unsafe_allow_html=True)
        '''
    
    #make top columns
    bottom_col1, bottom_col2, bottom_col3 = st.beta_columns(3)
    
    #the portfolio value
    with bottom_col1:
        
        #output header
        st.subheader("Portfolio Value")
    
        #get the monthly price
        monthly_prices = yf.download(tickers, start_date, end_date, interval = "1mo")['Close'].dropna()
        
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
        
        #plot the data
        st.bar_chart(monthly_portfolio)
        
    #the returns
    with bottom_col2:
        
        daily_returns = 0.32
        
        #output header
        st.markdown("<h1 style='text-align: center; color: white;'>Yearly Volatility</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'> Yearly VaR<sup>*</sup>:</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Alpha</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Beta</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Sharpe</h1>", unsafe_allow_html=True)
    
        
    #the diversification pie chart
    with bottom_col3:
        
        #output header
        st.subheader("Portfolio Diversification")
        
        #get the monthly price
        daily_prices = yf.download(tickers, start_date, end_date)['Close'].dropna()
        
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
                daily_portfolio[i][j] = daily_prices * price
    
        #make a new dataframe for the pie chart
        pie = weights.reset_index()
        
        #rename columns
        pie.columns = ["ticker", "weight"]
        
        #set up the pie chart
        diversification_pie = px.pie(weights, values = pie["weight"], names = pie["ticker"])
        st.plotly_chart(diversification_pie)

    st.write("$^*$ using 95% confidence interval")
    st.write("The information provided does not constitute as investment advice")
    st.write("Created by Diego Alvarez, not associated with Leeds Investment Trading Group Fund")
    #wait 30 minutes
    time.sleep(60 * 10)
    
    #then rerun the app
    st.experimental_rerun()
