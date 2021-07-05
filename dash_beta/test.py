import pandas as pd
import yfinance as yf

df = pd.read_excel("holdings.xls", index_col = 0)

if len(df.columns) > 1:
    print("expected only 2 columns in excel file but received more")

if df.columns[0] != "share_count":
    print("expected 2nd coumn to be named share_count")

try:
    
    tickers = df.index.to_list()
    yf.download(tickers)
    print("tickers checked out")
    
except:
    print("possibly incorrect ticker")
    
try:
    share_count = df['share_count']
    
    for i in share_count:
        if i < 1:
            print("problem with share value being 0 or negative or inputted incorrectly")
    
except:
    print("test")