import streamlit as st
import pandas as pd
import datetime
import requests
import json
import ast

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/weekly.py", label="Weekly Analytics")

st.title("Daily Analytics")

date = st.date_input("Data for date: ", datetime.date.today() - datetime.timedelta(days=1))
# Fetching data from api and converting it into DF
response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/weekly-stats?start_date={date}&end_date={date}")
data = json.loads(response.text)
weekly_user_data = pd.DataFrame(data['users'])

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/data?start_date={date}&end_date={date}")
data = json.loads(response.text)
daily_data = pd.DataFrame(data)

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/users?date={date}")
data = json.loads(response.text)
new_user_day_wise = pd.DataFrame(data['users'])

# Download daily_data
daily_data_csv = daily_data.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=daily_data_csv,  # Convert string to bytes
    file_name=f"data_{date}.csv",
    mime="text/csv",
)

def safe_literal_eval(val):
    # If it's already a list or dict, return it as is
    if not isinstance(val, str):
        return val
    try:
        return ast.literal_eval(val)
    except Exception as e:
        print("Error converting:", val, "\nError:", e)
        # Return the original value or an empty list if conversion fails
        return []

# Suppose daily_data is your DataFrame and 'chats' is the column with chat data.
daily_data['chats'] = daily_data['chats'].apply(safe_literal_eval)

# Now you can count the total number of individual messages across all sessions:
total_messages = daily_data['chats'].apply(len).sum()

st.header(f"Total Queries: {total_messages}")
st.header(f"Total users: {len(daily_data['user_id'].value_counts())}")
st.header(f"New Users: {data['total_users']}")
st.header(f"Total chats: {weekly_user_data['total_chats'].sum()}")
