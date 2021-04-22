import streamlit as st
import pandas as pd
import base64
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
  
#st.set_page_config(layout="wide")

#Loading the data
@st.cache
def get_data_votes():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_descr.csv'))
    df['year'] = df['date'].astype(str).str[0:4]
    df['month'] = df['date'].astype(str).str[5:7]
    df['day'] = df['date'].astype(str).str[8:10]
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']], errors = 'coerce')
    df['percentage of votes in favor'] = 100*df['pour']/df['nb votants']
    df['accepted'] = 'no'
    df.loc[df['pour'] >= df['requis'], 'accepted'] = 'yes'
    df = df.drop(columns=['date'])
    df.columns = df.columns.str.replace('demandeur ', '')
    return df

#Loading the data
@st.cache
def get_data_deputies():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_dep.csv'))
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_polpar.csv'))
    df = df.drop(columns=['code'])
    return df


@st.cache
def get_data_vote_total():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_total.csv'))
    return df

#def app():
    #configuration of the page
st.set_page_config(layout="wide")
matplotlib.use("agg")
_lock = RendererAgg.lock

SPACER = .2
ROW = 1

votes = get_data_votes()
df_polpar = get_data_political_parties()
df_vote_total = get_data_vote_total()

# Sidebar 
#selection box for the different features
st.sidebar.header('Select what to display')
#nb_voters = st.sidebar.slider("Voters", int(votes['nb votants'].min()), int(votes['nb votants'].max()), (int(votes['nb votants'].min()), int(votes['nb votants'].max())), 1)

#creates masks from the sidebar selection widgets
#mask_nb_voters = votes['nb votants'].between(nb_voters[0], nb_voters[1])

#display_df = votes[mask_nb_voters]


title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))

with title:
    st.title('Deputy information')

st.header('Data include votes and commissions')
st.write(df_vote_total)