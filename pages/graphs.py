import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import datetime
from datetime import date, timedelta
import requests
from io import StringIO
import json
import ast


st.title("Graphs")

from_date = st.date_input("Data starting form: ", datetime.date.today() - datetime.timedelta(days=7))
to_date = st.date_input("To: ", datetime.date.today())

payload = {
    "query": f'''
        SELECT 
            u.id, 
            u.name, 
            u.whatsapp, 
            u.role, 
            13 - MAX(ud.standard_id) AS standard, 
            ai.feature_id, 
            ai.created_at 
        FROM ai_analysis ai 
        INNER JOIN users u ON u.id = ai.user_id 
        LEFT JOIN user_defaults ud ON ud.user_id = u.id 
        WHERE DATE(ai.created_at) BETWEEN "{from_date}" AND "{to_date}" 
        GROUP BY 
            u.id, u.slug, u.name, u.whatsapp, u.role, u.created_at, 
            ai.feature_id, ai.created_at;
    '''
}

graphs_data = requests.post("https://newapi.edutorapp.com/api/download-query-data", json=payload)

graphs_data = pd.read_csv(StringIO(graphs_data.text))

graphs_data['created_at'] = pd.to_datetime(graphs_data['created_at']).dt.date

def queries(dataset, date):
    return len(dataset[dataset['feature_id'].isin([4.4, 4.5, 4.6]) & (dataset['created_at'] == date)])

def voice(date):
    return graphs_data[graphs_data['created_at'] == date]['feature_id'].value_counts().get(4.4, 0)

def image(date):
    return graphs_data[graphs_data['created_at'] == date]['feature_id'].value_counts().get(4.5, 0)

def text(date):
    return graphs_data[graphs_data['created_at'] == date]['feature_id'].value_counts().get(4.6, 0)

def get_date_range(start_date, end_date):
    # Calculate the number of days between the two dates
    delta = end_date - start_date  
    # Generate list of dates from start_date to end_date (inclusive)
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


start_date = graphs_data.iloc[0]['created_at']
end_date = graphs_data.iloc[-1]['created_at']
date_list = get_date_range(start_date, end_date)

queries_list = [queries(graphs_data, date) for date in date_list]
voice_list = [voice(date) for date in date_list]
image_list = [image(date) for date in date_list]
text_list = [text(date) for date in date_list]

    

df = pd.DataFrame({
    "Date": np.concatenate([date_list, date_list, date_list, date_list]),
    "Count": np.concatenate([queries_list, voice_list, image_list, text_list]),
    "Type": ["Total Queries"] * len(date_list) +
            ["Voice"] * len(date_list) +
            ["Image"] * len(date_list) +
            ["Text"] * len(date_list)
})

# Plot using Plotly
fig = px.line(df, x="Date", y="Count", color="Type", title="Total Data")
st.plotly_chart(fig)


# Daily Data Graph

response = requests.get(f"https://newapi.edutorapp.com/api/admin/chapter-ai/data?start_date={from_date}&end_date={to_date}")
data = json.loads(response.text)
daily_data = pd.DataFrame(data)

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