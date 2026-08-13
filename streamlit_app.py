import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='AI Interview Analytics', layout='wide')

st.title('AI Interview Score Trends Dashboard')
st.caption('Data / ML / NLP / Visualization using Python and Plotly')

sample_df = pd.read_csv('data/sample_scores.csv')

st.subheader('Recent score performance')
fig = px.line(
    sample_df,
    x='session_date',
    y='score',
    color='category',
    markers=True,
    title='Interview Score Trends',
)
st.plotly_chart(fig, use_container_width=True)

st.subheader('Score summary')
summary = sample_df.groupby('category')['score'].mean().reset_index()
st.dataframe(summary, use_container_width=True)

st.subheader('Candidate comparison')
bar_chart = px.bar(summary, x='category', y='score', color='category', title='Average Score by Category')
st.plotly_chart(bar_chart, use_container_width=True)
