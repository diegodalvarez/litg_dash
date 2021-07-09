import time
import requests
import numpy as np
import pandas as pd
import pkg_resources
import yfinance as yf
import datetime as dt
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

import statsmodels.api as sm
from statsmodels import regression

from dash_tools import DashTools

def diagnostics():

    #make a list of the required packages
    required = {'numpy', 'pandas', 'yfinance', 'streamlit', 'plotly', 'statsmodels', 'matplotlib'}
    
    #then make a list of the installed packages
    installed = {pkg.key for pkg in pkg_resources.working_set}
    
    #then get the packages that are not installed
    missing = required - installed
    
    #if the missing packages is greater than 0 meaning there is a package not installed
    if len(missing) > 0:
        
        #output that there was a problem
        st.write("there was a problem")
        
        #then loop through the missing packages
        for i in missing:
            
            #output the name of the package
            st.subheader("Packages: could not find {} package try pip installing it".format(i))
            
    #the scenario when all of the packages are installed
    else:
        
        #output that they have ben installed
        st.subheader("Packages: all packages installed")
        
    url = "http://colorado.edu?"
    timeout = 5
    
    #we want to tset internet connection
    try:
        
        #we want to get a request page
        request = requests.get(url, timeout=timeout)
        
        #we want to output
        st.subheader("Internet: Connected to the internet")
    
    #when we don't have an internet connection
    except (requests.ConnectionError, requests.Timeout) as exception:
        
        #then output that out
        st.subheader("No internet Connection")
        
    try:
        
        df = pd.read_excel("holdings.xls", index_col = 0)

        if len(df.columns) > 1:
            st.subheader("expected only 2 columns in excel file but received more")
        
        if df.columns[0] != "share_count":
            st.subheader("expected 2nd coumn to be named share_count")
        
        try:
            
            tickers = df.index.to_list()
            yf.download(tickers)
            st.subheader("tickers checked out")
            
        except:
            st.subheader("possibly incorrect ticker")
            
        try:
            share_count = df['share_count']
            
            for i in share_count:
                if i < 1:
                    st.subheader("problem with share value being 0 or negative or inputted incorrectly")
            
        except:
            st.subheader("Excel file seems fine can't find problem")
        
    except:
        st.subheader("Couldn't find file, please read documentation for excel file")
        
        try:
            
            #we want to test to see if it is an xlsx file
            test = pd.read_csv("holdings.xls")
            st.subheader("file is an xls, due to the file output from the brokerage service we can only accept xls")
        
        except:
            st.subheader("tried finding xls please read documentation for excel file")
            
st.set_page_config(layout="wide")

#this makes the portfolio pie diversification
def portfolio_pie(dashtools):
    
    #import the daily portfolio which keeps track of each value of the stock and the portfolio value
    daily_portfolio = dashtools.daily_portfolio
    
    #get the value of the portfolio into a list
    final_val = daily_portfolio['value'][len(daily_portfolio) - 1]
    
    #this is going to make our output dataframe
    pie = dashtools.weights.reset_index().drop(columns = ["share_count"])
    
    #then this is going to rename the column
    pie.columns = ["ticker"]
    
    #sort alphabetically
    pie['ticker'] = sorted(pie['ticker'])
    
    #then initialize a new column to be empty for the percetnage value
    pie['weight'] = ""
    
    #now we want to go through all of the columns except for the last one which is portfoli ovalue
    for counter, i in enumerate(daily_portfolio.columns[:-1]):
        
        #the [i][len(daily_portfolio) - 1] will get the last value of the stock in the fund then divide by the final value
        weight = daily_portfolio[i][len(daily_portfolio) - 1] / final_val
        
        #add that weight to the dataframe
        pie['weight'][counter] = round(weight, 4)
        
    #in this case we want to make the plotly object
    diversification_pie = px.pie(dashtools.weights, values = pie['weight'], names = pie['ticker'])
    
    st.subheader("Portfolio Diversification")
    st.plotly_chart(diversification_pie)

#this gets the daily returns
def daily_returns(dashtools):
    
    #this makes the header
    st.subheader("Distribution of Portfolio's Daily Returns")
    
    #this gets the percent change
    port_rets = dashtools.daily_portfolio['value'].pct_change().dropna()
    
    #this makes the distplot
    dist_plot = px.histogram(port_rets, height = 400, width = 700, nbins = 200)
    
    #this just puts titles on it
    dist_plot.update_layout(showlegend = False, xaxis_title = "Return (%)", yaxis_title = "frequency", font = dict(size = 15))
    
    #output the px object to streamlit
    st.plotly_chart(dist_plot)

#portfolio statistics function
def port_stats(dashtools):
    
    ##############################################################################
    #this is for daily returns
    ##############################################################################
    
    #lets get the last 3 days then calculate the percent change then drop values then get the last value
    daily_return = dashtools.daily_portfolio.tail(3)['value'].pct_change().dropna().tail(1)
    
    #then multiply that to get the percentage return
    daily_return = round(float(daily_return.values) *100, 2)
    
    ##############################################################################
    #this is for weekly returns
    ##############################################################################
    
    #this gest the number of days that we are looking back it is used for making a dataframe to calculate over a range
    lookback = {0:5, 1:5, 2:2, 3:3, 4:4, 5:5, 6:5}
    
    #how many days we want to go back
    cutoff = lookback[dashtools.end_date.weekday()]
    
    #then get the data and cutoff the length we want
    port_val = dashtools.daily_portfolio['value'].iloc[-cutoff:]
    
    #get first entry
    first_day = port_val.head(1).values
    
    #get last entry
    last_day = port_val.tail(1).values
    
    #do the percent change
    weekly_return = round(float(((last_day - first_day) / first_day) * 100), 2)
    
    ##############################################################################
    #ytd return
    ##############################################################################
    ytd_date = dt.datetime(dashtools.end_date.year, 1, 1)
    ytd_days = int((dashtools.end_date - ytd_date).days / 7 *5)
    ytd_return = dashtools.daily_portfolio.tail(ytd_days)['value'].iloc[[0, -1]].pct_change().dropna()
    ytd_return = round(float(ytd_return.values) * 100, 2)
    
    ##############################################################################
    #yearly returns
    ##############################################################################
    yearly_return = dashtools.daily_portfolio.tail(252).iloc[[0, -1]]['value'].pct_change().dropna()
    yearly_return = round(float(yearly_return.values) * 100, 2)
    
    ##############################################################################
    #inception
    ##############################################################################
    inception_return = dashtools.daily_portfolio['value'].iloc[[0, -1]].pct_change().dropna()
    inception_return = round(float(inception_return.values) * 100, 2)
    
    #output header and make sure font color is right
    st.markdown("<h1 style='text-align: center; color: white;'>Today's Returns: {}%</h1>".format(daily_return), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>This week's Returns: {}%</h1>".format(weekly_return), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>365 day Return: {}%</h1>".format(yearly_return), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>YTD Returns: {}%</h1>".format(ytd_return), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Since Inception: {}%</h1>".format(inception_return), unsafe_allow_html=True)

#makes the portfolio market statistics
def port_market(dashtools):

    #365 day volatility
    vol = dashtools.daily_portfolio["value"].tail(252)
    vol = round(np.log(vol / vol.shift(1)).std() * 252 ** .5, 2)
    
    #get the performance of the fund
    perf = dashtools.daily_portfolio['value']
    
    #then get the benchmark
    spx = yf.download("^GSPC", perf.index[0], perf.index[-1])['Close']
    
    #get alpha and beta
    y = dashtools.daily_portfolio['value'].pct_change().dropna().iloc[:-1]
    X = spx.pct_change().dropna()
    
    #run the model
    X = sm.add_constant(X)
    model = regression.linear_model.OLS(y,X).fit()
    
    #then find alpha and beta
    alpha = round(model.params[0], 5)
    beta = round(model.params[1], 2)
    
    #now get the sharpe 
    sharpe_df = dashtools.daily_portfolio['value'].pct_change().dropna()
    ret = sharpe_df.mean()
    stdev = sharpe_df.std()
    sharpe = round(ret / stdev, 2)
    
    #output the header and check the font color
    st.markdown("<h1 style='text-align: center; color: white;'>365 day Volatility: {}</h1>".format(vol), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Alpha: {}</h1>".format(alpha), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Beta: {}</h1>".format(beta), unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>Portfolio Sharpe: {}</h1>".format(sharpe), unsafe_allow_html=True)

#portfolio composition tool
def port_comp(dashtools):

    #then you get the monthly portfolio price
    monthly_portfolio = dashtools.make_monthly_portfolio()
    
    #put title
    st.subheader("Portfolio Value by Composition")
    
    #output it to streamlit 
    st.bar_chart(monthly_portfolio)

#this makes the performance of the fund vs SPX
def spx_perf(dashtools):

    #get the value of the fund
    perf = dashtools.daily_portfolio['value']
    
    #get spx values
    spx = yf.download("^GSPC", dashtools.start_date, dashtools.end_date)['Close']
    
    #get the number of (shares) for our SPX comparison
    sp_shares = int(perf[0] / spx[0])
    
    #multiply shares to our spx to get equivalent value
    bench = spx * sp_shares
    
    #merge for output
    output_df = pd.concat([perf, bench], axis = 1)
    
    #rename columns for chart
    output_df.columns = ["Port", "SPX"]
    
    st.subheader("Portfolio vs S&P 500")
    st.line_chart(output_df, width = 500, height = 300)

def make_top_row(dashtools):
    
    top_col1, top_col2, top_col3 = st.beta_columns((2,2,1))
    
    with top_col1:
        portfolio_pie(dashtools)
        
    with top_col2:
        daily_returns(dashtools)
        
    with top_col3:
        port_stats(dashtools)

def make_bottom_row(dashtools):
    
    bottom_col1, bottom_col2, bottom_col3 = st.beta_columns((1,2,2))
    
    with bottom_col1:
        port_market(dashtools)
        
    with bottom_col2:
        port_comp(dashtools)
        
    with bottom_col3:
        spx_perf(dashtools)

while True:
    
    try:
    
        #we make the dashtools here to pass through all of the functions
        dashtools = DashTools()
        
    except:
        
        st.title("Oh no a problem has occured")
        
        diagnostics()
        st.subheader("Excel file loaded:")
        break
    
    #make update date
    update_date = dt.datetime.today().strftime("%a %D %I:%M %p")
    
    #show last time we updted
    st.title("Leed's Investment Trading Group Fund (last updated: {})".format(update_date))
    
    make_top_row(dashtools)
    make_bottom_row(dashtools)
    
    st.write("The information provided does not constitute as investment advice")
    st.write("Created by Diego Alvarez, not associated with Leeds Investment Trading Group Fund, Values may not be up-to-date or approximations, updates don't occur until trading day ends")
    
    #the cost basis day provided from LITG
    next_update = dt.datetime.today() + dt.timedelta(seconds = 60 * 60 * 4)
    
    #get update time
    next_update_time = next_update.strftime("%a %D %I:%M %p")
    
    #output it
    st.write("next update is scheduled for {}".format(next_update_time))
    
    #wait 30 minutes
    time.sleep(60 * 60 * 4)
    
    #then rerun the app
    st.experimental_rerun()
        