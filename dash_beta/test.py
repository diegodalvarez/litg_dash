import time
import pandas as pd
import datetime as dt
import streamlit as st
import yfinance as yf
import plotly.express as px

from dash_tools import DashTools

st.set_page_config(layout="wide")

dashtools = DashTools()

def twod_contour(dashtools):

    dashtools = DashTools().daily_portfolio['value'].to_frame().pct_change().dropna()    

    #get start and end  from 
    start = dashtools.index[0]
    end = dashtools.index[len(dashtools) - 1]
    
    spx_close = yf.download("^GSPC", start, end)['Close'].to_frame().pct_change().dropna()
    
    #if there is an index mismatch because sometimes we need to cuttoff the end
    
    #when the portfolio value is has more dates than spx_close
    if len(dashtools) > len(spx_close):
        
        #find cutoff value
        cutoff = len(dashtools) - len(spx_close)
        
        #cutt if off
        dashtools = dashtools[:-1]
        
    #when there are more spx_close dates than portfolio value    
    if len(dashtools) < len(spx_close):
        
        #find the difference
        cutoff = len(spx_close) - len(dashtools)
        
        #then cutoff from there
        spx_close = spx_close[:-1]
        
    #make a new dataframe
    output_df = pd.DataFrame(columns = ["portfolio", "spx_close", "dates"])
    
    #load in dates
    output_df["dates"] = dashtools.index
    
    #put in values
    output_df['portfolio'] = dashtools.values
    output_df['spx_close'] = spx_close.values
    
    #reset index to index to dates and get percent change and drop non-numbers
    output_df = output_df.set_index("dates").pct_change().dropna()
    
    fig = px.density_contour(output_df, x = "portfolio", y = "spx_close", marginal_x = "histogram", marginal_y = "histogram", 
                             nbinsx = 100, nbinsy = 100, width = 1000, height = 1000,
                             range_x = (min(output_df['portfolio']) * 0.65, max(output_df['portfolio']) * 0.65),
                             range_y = (min(output_df["spx_close"]) * 0.65, max(output_df["spx_close"]) * 0.65))
    st.plotly_chart(fig)

def twod_contour_flipped(dashtools):

    dashtools = DashTools().daily_portfolio['value'].to_frame().pct_change().dropna()

    #get start and end  from 
    start = dashtools.index[0]
    end = dashtools.index[len(dashtools) - 1]
    
    spx_close = yf.download("^GSPC", start, end)['Close'].to_frame().pct_change().dropna()
    
    spx_close_flipped = []
    
    for i in spx_close['Close']:
        
        spx_close_flipped.append(-i)
        
    spx_close["flipped"] = spx_close_flipped
    
    #if there is an index mismatch because sometimes we need to cuttoff the end
    
    #when the portfolio value is has more dates than spx_close
    if len(dashtools) > len(spx_close):
        
        #find cutoff value
        cutoff = len(dashtools) - len(spx_close)
        
        #cutt if off
        dashtools = dashtools[:-1]
        
    #when there are more spx_close dates than portfolio value    
    if len(dashtools) < len(spx_close):
        
        #find the difference
        cutoff = len(spx_close) - len(dashtools)
        
        #then cutoff from there
        spx_close = spx_close[:-1]
        
    #make a new dataframe
    output_df = pd.DataFrame(columns = ["portfolio", "flipped", "dates"])
    
    #load in dates
    output_df["dates"] = dashtools.index
    
    #put in values
    output_df['portfolio'] = dashtools.values
    output_df['flipped'] = spx_close['flipped'].values
    
    #reset index to index to dates and get percent change and drop non-numbers
    output_df = output_df.set_index("dates").pct_change().dropna()
    
    fig = px.density_contour(output_df, x = "portfolio", y = "flipped", marginal_x = "histogram", marginal_y = "histogram", 
                             nbinsx = 100, nbinsy = 100, width = 1000, height = 1000,
                             range_x = (min(output_df['portfolio']) * 0.65, max(output_df['portfolio']) * 0.65),
                             range_y = (min(output_df["flipped"]) * 0.65, max(output_df["flipped"]) * 0.65))
    st.plotly_chart(fig)
    
    return spx_close
    
twod_contour(dashtools)
test = twod_contour_flipped(dashtools)
