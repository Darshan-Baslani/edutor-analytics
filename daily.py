import streamlit as st

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/weekly.py", label="Weekly Analytics")

st.title("Main Page")
st.write("Welcome to the main page!")