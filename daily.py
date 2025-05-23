import streamlit as st
import pandas as pd
import datetime
import requests
import json
import ast
from io import StringIO

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/weekly.py", label="Weekly Analytics")
st.sidebar.page_link("pages/graphs.py", label="Graphs")

st.title("Daily Data")

date = st.date_input("Data for date: ", datetime.date.today() - datetime.timedelta(days=1))

st.markdown(f"# ChapterAI {date} Data 📈")

# Fetching data from api and converting it into DF
response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/weekly-stats?start_date={date}&end_date={date}")
data = json.loads(response.text)
weekly_user_data = pd.DataFrame(data['users'])

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/data?start_date={date}&end_date={date}")
data = json.loads(response.text)
daily_data = pd.DataFrame(data)

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/users?date={date}")
data = json.loads(response.text)

# Download daily_data
daily_data_csv = daily_data.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=daily_data_csv,  # Convert string to bytes
    file_name=f"data_{date}.csv",
    mime="text/csv",
)

st.markdown(f"- Queries: {data['total_queries']}")
st.markdown(f"- Users: {data['total_users']}")
st.markdown(f"- Chats: {data['total_chats']}")
st.markdown(f"- Avg Query/user: {data['avg_user_query']}")
st.markdown(f"- New Users: {data['firsttime_user_count']}")
st.markdown(f"- New Students: {data['first_time_role0_count']}")
st.markdown(f"- New Teachers: {data['first_time_role1_count']}")


date = str(date)
payload = {"query": f'SELECT u.id, u.name, u.whatsapp, u.role, 13 - MAX(ud.standard_id) AS standard, ai.feature_id, ai.created_at FROM ai_analysis ai INNER JOIN users u ON u.id = ai.user_id LEFT JOIN user_defaults ud ON ud.user_id = u.id WHERE DATE(ai.created_at) = "{date}" GROUP BY u.id, u.slug, u.name, u.whatsapp, u.role, u.created_at, ai.feature_id, ai.created_at;'}

queries = requests.post("https://newapi.edutorapp.com/api/download-query-data", json=payload)

queries = pd.read_csv(StringIO(queries.text))

total = queries['feature_id'].value_counts()[4.4] + queries['feature_id'].value_counts()[4.5] + queries['feature_id'].value_counts()[4.6]

st.markdown(f"# Total Queries Hit: ")
st.markdown(f"- Total Queries - {len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])])}")
st.markdown(f"- Text - {queries['feature_id'].value_counts()[4.6]} - ({round(queries['feature_id'].value_counts()[4.6] / total * 100)})%")
st.markdown(f"- Voice - {queries['feature_id'].value_counts()[4.4]} - ({round(queries['feature_id'].value_counts()[4.4] / total * 100)})%")
st.markdown(f"- Image - {queries['feature_id'].value_counts()[4.5]} - ({round(queries['feature_id'].value_counts()[4.5] / total * 100)})%")
teacher = len(queries[(queries['role'] == 1) & (queries['feature_id'].isin([4.4, 4.5, 4.6]))]['id'].unique())
student = len(queries[(queries['role'] == 0) & (queries['feature_id'].isin([4.4, 4.5, 4.6]))]['id'].unique())
st.markdown(f"- Teacher - {teacher} - {round((teacher / (student + teacher)) * 100)}%")
st.markdown(f"- Student - {student} - {round((student / (student + teacher)) * 100)}%")
st.markdown(f"# Failed Queries:")
st.markdown(f"- {(len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]) - data['total_queries'])} - {round((len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]) - data['total_queries']) / len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]) * 100)}%")
st.markdown(f"# User Loss:")
st.markdown(f"- {len(daily_data['user_id'].value_counts()) - len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]['id'].unique())} - {round((len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]['id'].unique()) - len(daily_data['user_id'].value_counts())) / len(queries[queries['feature_id'].isin([4.4, 4.5, 4.6])]['id'].unique())* 100)}%")