import pandas as pd
import streamlit as st

st.write("test")

df = pd.read_excel("holdings.xlsx")
st.write(df)
