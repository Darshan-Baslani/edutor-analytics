import streamlit as st 
import pandas as pd
import requests
import json
import datetime
import subprocess
import matplotlib.pyplot as plt
from datetime import time, timedelta

subprocess.run("pip install tabulate", shell=True)

 
st.title("Weekly Analytics")

# Getting Date from the user
with st.form(key='date_form'):
    from_date = st.date_input("Data starting form: ", datetime.date.today() - datetime.timedelta(days=7))
    to_date = st.date_input("To: ", datetime.date.today())
    
    submit_button = st.form_submit_button(label='Go!')

# Fetching data from api and converting it into DF
response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/weekly-stats?start_date={from_date}&end_date={to_date}")
data = json.loads(response.text)
weekly_user_data = pd.DataFrame(data['users'])

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/data?start_date={from_date}&end_date={to_date}")
data = json.loads(response.text)
weekly_chat_data = pd.DataFrame(data)

# Download daily_data
weekly_chat_data_csv = weekly_chat_data.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=weekly_chat_data_csv,  # Convert string to bytes
    file_name=f"data_{from_date}_{to_date}.csv",
    mime="text/csv",
)

# New Users
weekly_user_data['created_at'] = pd.to_datetime(weekly_user_data['created_at']).dt.date
def get_date_range(start_date, end_date):
    # Calculate the number of days between the two dates
    delta = end_date - start_date  
    # Generate list of dates from start_date to end_date (inclusive)
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

date_list = get_date_range(from_date, to_date)

length = 0
for date in date_list:
    length += len(weekly_user_data[weekly_user_data['created_at'] == date])
    
st.header(f"New Users: {length}")
st.header(f"Total users: {weekly_user_data['id'].value_counts().sum()}")
st.header(f"Total chats: {weekly_user_data['total_chats'].sum()}")
st.header(f"Total queries: {weekly_user_data['total_queries'].sum()}")
st.header(f"Per user avg. chat: {round(weekly_user_data['total_chats'].sum() / weekly_user_data['id'].value_counts().sum(), 1)}")
st.header(f"Per user avg. queries: {round(weekly_user_data['total_queries'].sum() / weekly_user_data['id'].value_counts().sum(), 1)}")

st.header(f"Active days count: ")
df_temp = pd.DataFrame(weekly_user_data['active_days_count'].value_counts(ascending=True))
st.write(df_temp.to_markdown())

# Define chat ranges
bins = [1, 2, 5, 15, float('inf')] 
labels = ["1", "2-5", "6-15", "15+"]

# Categorize total_chats into bins
chat_user_range = pd.cut(weekly_user_data["total_chats"], bins=bins, labels=labels, right=False)
st.header(f"Chats range:")

result = chat_user_range.value_counts().sort_index(ascending=False)
result_df = pd.DataFrame(result)
result_df.columns = ['Number of Users']
result_df.index.name = 'Chat Range'

# Print with styling
st.write(result_df.to_markdown())

# Percentage's
st.header(f"Percentage of users who have done atleast 10 chats a week: {round((weekly_user_data[weekly_user_data['total_chats'] >= 10].shape[0] / weekly_user_data['id'].value_counts().sum()) * 100)}%")
st.header(f"Percentage of users who used the app for 3 days or more: {round((weekly_user_data[weekly_user_data['active_days_count'] >= 3].shape[0] / weekly_user_data['id'].value_counts().sum()) * 100)}%")
st.header(f"Percentage of users who used the app for a single day: {round((weekly_user_data[weekly_user_data['active_days_count'] == 1].shape[0]/ weekly_user_data['id'].value_counts().sum()) * 100)}%")
