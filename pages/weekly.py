import streamlit as st 
import pandas as pd
import requests
import json
import datetime
import tabulate
 
st.title("Weekly Analytics")

# Getting Date from the user
from_date = st.date_input("Data starting form: ", datetime.date.today() - datetime.timedelta(days=7))
to_date = st.date_input("To: ", datetime.date.today())

# Fetching data from api and converting it into DF
response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/weekly-stats?start_date={from_date}&end_date={to_date}")
data = json.loads(response.text)
weekly_user_data = pd.DataFrame(data['users'])

st.header(f"Total users per week: {weekly_user_data['id'].value_counts().sum()}")
st.header(f"Total chats: {weekly_user_data['total_chats'].sum()}")
st.header(f"Total queries: {weekly_user_data['total_queries'].sum()}")
st.header(f"Per user avg. chat: {round(weekly_user_data['total_chats'].sum() / weekly_user_data['id'].value_counts().sum(), 1)}")
st.header(f"Per user avg. queries: {round(weekly_user_data['total_queries'].sum() / weekly_user_data['id'].value_counts().sum(), 1)}")

st.header(f"Active days count: ")
df_temp = pd.DataFrame(weekly_user_data['active_days_count'].value_counts())
st.write(df_temp.to_markdown())

st.header(f"Ketla users ae ketly chat kri: ")
df_temp = pd.DataFrame(weekly_user_data['total_chats'].value_counts())
st.write(df_temp.to_markdown())

# Define chat ranges
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, float('inf')]  # Adjust as needed
labels = ["0-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50+"]

# Categorize total_chats into bins
chat_user_range = pd.cut(weekly_user_data["total_chats"], bins=bins, labels=labels, right=False)
st.header(f"Chats range:")

result = chat_user_range.value_counts().sort_index()
result_df = pd.DataFrame(result)
result_df.columns = ['Number of Users']
result_df.index.name = 'Chat Range'

# Print with styling
st.write(result_df.to_markdown())

# Percentage's
st.header(f"Percentage of users who have done atleast 10 chats a week: {round((weekly_user_data[weekly_user_data['total_chats'] >= 10].shape[0] / weekly_user_data['id'].value_counts().sum()) * 100, 1)}")
st.header(f"Percentage of users who used the app for 3 days or more: {round((weekly_user_data[weekly_user_data['active_days_count'] >= 3].shape[0] / weekly_user_data['id'].value_counts().sum()) * 100, 1)}")
st.header(f"Percentage of users who used the app for a single day: {round((weekly_user_data[weekly_user_data['active_days_count'] == 1].shape[0]/ weekly_user_data['id'].value_counts().sum()) * 100, 1)}")
