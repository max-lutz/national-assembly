import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('French national assembly vizualisation tool')

st.markdown("""
This app performs simple vizualisation from the open data from the french national assembly!
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [national assembly open data](https://data.assemblee-nationale.fr/).
""")

st.sidebar.header('User Input Features')

deputies = pd.read_csv('df_dep.csv')

@st.cache
def get_data():
    return pd.read_csv('df_dep.csv')
deputies = get_data()

pol_parties = deputies["pol party"].unique().tolist()
pol_party_selected = st.sidebar.multiselect('Political parties', pol_parties, pol_parties)
sex = deputies["sex"].unique().tolist()
sex_selected = st.sidebar.multiselect('Sex', sex, sex) 
jobs = deputies["activity"].unique().tolist()
jobs_selected = st.sidebar.multiselect('Political parties', jobs, jobs) 
#jobs = df['activity'].drop_duplicates()
#job_choice = st.sidebar.selectbox('Jobs:', jobs)

mask_pol_parties = deputies['pol party'].isin(pol_party_selected)
mask_sex = deputies['sex'].isin(sex_selected)
mask_jobs = deputies['activity'].isin(jobs_selected)

display_df = deputies[mask_pol_parties & mask_sex & mask_jobs]
display_df = display_df.sort_values(by=['pol party'])
# Displays the user input features
st.subheader('User Input features')

st.subheader('Dataframe')
st.write(display_df)

st.write(display_df['pol party'].unique().tolist())
st.write(display_df['pol party'].value_counts(sort=False))

plt.pie(display_df['pol party'].value_counts(sort=False), labels=display_df['pol party'].unique().tolist())
st.pyplot()