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
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df['departement'] = df['dep'].astype(str) + ' ('+ df['num_dep'] + ')'
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_polpar.csv'))
    df = df.drop(columns=['code'])
    return df


@st.cache
def get_data_vote_total():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_total.csv'),
    dtype={
        'pour': bool,
        'contre': bool,
        'non votants' : bool,
        'abstentions' : bool,
        'par delegation' : bool
            })
    #df['scrutin'] = df['scrutin'].map(lambda x: x.lstrip('VTANR5L15V'))
    df['cause'] = df['cause'].fillna('none')
    df['cause'] = df['cause'].astype("category")
    df['deputy code'] = df['deputy code'].astype("category")
    df['scrutin'] = df['scrutin'].astype("category")
    return df

#def app():
    #configuration of the page
    #st.set_page_config(layout="wide")
matplotlib.use("agg")
_lock = RendererAgg.lock

SPACER = .2
ROW = 1


df_dep = get_data_deputies()
votes = get_data_votes()
df_polpar = get_data_political_parties()
df_vote_total = get_data_vote_total()

# Sidebar 
#selection box for the different features
st.sidebar.header('Select what to display')
departement_selected = st.sidebar.selectbox('Select departement', df_dep.sort_values(by=['num_dep'])['departement'].unique())
#nb_voters = st.sidebar.slider("Voters", int(votes['nb votants'].min()), int(votes['nb votants'].max()), (int(votes['nb votants'].min()), int(votes['nb votants'].max())), 1)

#creates masks from the sidebar selection widgets
mask_departement = df_dep['departement'].isin([departement_selected])

display_df = df_dep[mask_departement]


title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))

with title:
    st.title('Deputy information')

st.header('Data include votes and commissions')
#st.write(df_vote_total.sample(20))
st.write(df_vote_total.describe())
st.write(df_vote_total.info())

st.write(display_df)