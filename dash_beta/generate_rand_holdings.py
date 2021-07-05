import numpy as np
import pandas as pd

#this will be a list of random integers used to reference stocks out of S&P 500 and used for number of shares
rand_list = list(np.random.randint(0, 500, 35))

#make shares list necessary for line below
shares = [] 

#this deletes duplicates
[shares.append(x) for x in rand_list if x not in shares]


#we want to pull the S&P 500 tickers
sp = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]['Symbol']

#make a list to hold the random tickers
tickers = []

#go through the shares list
for i in shares:
    
    #get the random ticker and add it our list
    tickers.append(sp[i])

#now we want make out dataframe the way that streamlit

#index column: tickers
#next column: number of shares
#next column: start date (not added yet)

#put everything into the dataframe
output = pd.DataFrame({"share_count": shares}, index = tickers)

#then output the file as xls (picked that format because file given from LITG came as xls)
output.to_excel("holdings.xls")