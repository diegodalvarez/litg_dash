import time
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

import statsmodels.api as sm
from statsmodels import regression

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
    update_date = end_date - dt.timedelta(seconds = 7 * 60 * 60)
    update_date = update_date.strftime("%a %D %I:%M %p") 
    
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
        
        print("")
        
        #output header
        st.subheader("Portfolio Diversification")
        
        #get the monthly price the dropna will negate the cost basis stuff
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
                daily_portfolio[i][j] = share_count * price
         
        #this is going to make the portfolio value for each day
        daily_portfolio["value"] = daily_portfolio.sum(axis=1)
        
        pie = weights.reset_index().drop(columns = ["share_count"])
        pie.columns = ["ticker"]
        pie["weight"] = ""
        
        final_val = daily_portfolio["value"][len(daily_portfolio) - 1] 
        
        for counter, i in enumerate(daily_portfolio.columns[:-1]):
            
            weight = daily_portfolio[i][len(daily_portfolio) - 1] / final_val
            pie['weight'][counter] = round(weight ,2)
        
        diversification_pie = px.pie(weights, values = pie["weight"], names = pie["ticker"])
        st.plotly_chart(diversification_pie)
    
    #the returns
    with top_col3:
        
        #this gets daily returns
        daily_return = daily_portfolio.tail(3)['value'].pct_change().dropna().tail(1)
        daily_return = round(float(daily_return.values) * 100, 2)
        
        #this gets weekly returns (probably needs a double check)
        weekly_return = daily_portfolio.tail(end_date.weekday()).iloc[[0, -1]]['value'].pct_change().dropna()
        weekly_return = round(float(weekly_return.values) * 100, 2)
        
        #this gets yearly returns (probably needs to be fixed)
        yearly_return = daily_portfolio.tail(252).iloc[[0, -1]]['value'].pct_change().dropna()
        yearly_return = round(float(yearly_return.values) * 100, 2)
        
        #ytd returns
        ytd_date = dt.datetime(end_date.year, 1, 1)
        ytd_days = int((end_date - ytd_date).days / 7 * 5)
        ytd_return = daily_portfolio.tail(ytd_days)['value'].iloc[[0, -1]].pct_change().dropna()
        ytd_return = round(float(ytd_return.values) * 100, 2)
        
        #inception returns
        inception_return = daily_portfolio['value'].iloc[[0, -1]].pct_change().dropna()
        inception_return = round(float(inception_return.values) * 100, 2)
        
        
        #output header
        st.markdown("<h1 style='text-align: center; color: white;'>Today's Returns: {}%</h1>".format(daily_return), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>This week's Returns: {}%</h1>".format(weekly_return), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>365 day Return: {}%</h1>".format(yearly_return), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>YTD Returns: {}%</h1>".format(ytd_return), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Since Inception: {}%</h1>".format(inception_return), unsafe_allow_html=True)
    
    #make top columns
    bottom_col1, bottom_col2, bottom_col3 = st.beta_columns(3)
    
    #the portfolio value
    with bottom_col1:
        
        st.subheader("Performance vs Benchmark")
        
        #get the performance of the fund
        perf = daily_portfolio['value']
        
        #get benchmark for same period
        spx = yf.download("^GSPC", perf.index[0], perf.index[-1])['Close']
        
        #need to account for trading day
        perf = daily_portfolio['value'].head(-1)
        
        #get number of s&p shares to compare
        sp_shares = perf[0] / spx[0]
        
        #multiply to get fund value
        bench = spx * sp_shares
        
        #merge for output
        output_df = pd.concat([perf, bench], axis = 1)
        
        #rename columns for chart
        output_df.columns = ["Portfolio Value", "Benchmark"]
        
        st.line_chart(output_df)
        
    #the returns
    with bottom_col2:
        
        #365 day volatility
        vol = daily_portfolio['value'].tail(252)
        vol = round(np.log(vol / vol.shift(1)).std()*252**.5,2)
        
        #alpha and beta
        y = daily_portfolio['value'].pct_change().dropna().iloc[:-1]
        X = spx.pct_change().dropna()
        
        X = sm.add_constant(X)
        model = regression.linear_model.OLS(y,X).fit()
        
        alpha = round(model.params[0], 5)
        beta = round(model.params[1], 2)
        
        #sharpe 
        sharpe_df = daily_portfolio['value'].pct_change().dropna()
        ret = sharpe_df.mean()
        stdev = sharpe_df.std()
        sharpe = round(ret / stdev, 2)
        
        #output header
        st.markdown("<h1 style='text-align: center; color: white;'>365 day Volatility: {}</h1>".format(vol), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Alpha: {}</h1>".format(alpha), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Beta: {}</h1>".format(beta), unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Sharpe: {}</h1>".format(sharpe), unsafe_allow_html=True)
    
        
    #the diversification pie chart
    with bottom_col3:
        
        st.subheader("Distribution of Portfolio's Daily Returns")
        
        port_rets = daily_portfolio['value'].pct_change().dropna()
        dist_plot = px.histogram(port_rets, height=500, width=900, nbins = 200)
        dist_plot.update_layout(showlegend=False, xaxis_title="Return (%)", yaxis_title = "frequency", font = dict(size = 15))
        st.plotly_chart(dist_plot)

    st.write("The information provided does not constitute as investment advice")
    st.write("Created by Diego Alvarez, not associated with Leeds Investment Trading Group Fund, Values may not be up-to-date or approximations, updates don't occur until trading day ends")
    
    #the cost basis day provided from LITG
    next_update = dt.datetime.today() + dt.timedelta(seconds = 60 * 60)
    
    #get update time
    next_update_time = next_update.strftime("%a %D %I:%M %p")
    
    #output it
    st.write("next update is scheduled for {}".format(next_update_time))
    
    #wait 30 minutes
    time.sleep(60 * 60)
    
    #then rerun the app
    st.experimental_rerun()
