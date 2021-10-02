import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.backends.backend_agg import RendererAgg

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


def app():
    #configuration of the page
    #st.set_page_config(layout="wide")
    matplotlib.use("agg")
    _lock = RendererAgg.lock

    SPACER = .2
    ROW = 1

    df_votes = get_data_votes()
    df_polpar = get_data_political_parties()

    # Sidebar 
    #selection box for the different features
    st.sidebar.header('Select what to display')
    nb_voters = st.sidebar.slider("Number of voters", int(df_votes['nb votants'].min()), int(df_votes['nb votants'].max()), (int(df_votes['nb votants'].min()), int(df_votes['nb votants'].max())), 1)

    #creates masks from the sidebar selection widgets
    mask_nb_voters = df_votes['nb votants'].between(nb_voters[0], nb_voters[1])

    df_votes_selected = df_votes[mask_nb_voters]


    title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))

    with title:
        st.title('Vote vizualisation tool')

    row0_spacer1, row0_1, row0_spacer2 = st.beta_columns((SPACER/2,ROW, SPACER/2))
    with row0_1:
        st.header('Data (all the votes from June 2017 to mid March 2021)')
    #st.write(df_votes_selected)
        
    ### Vote repartition
    row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row1_1, _lock:
        st.header('Repartition of vote presence')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=df_votes_selected, x="nb votants", hue="accepted", bins=40)
        ax.set_xlabel('Number of deputies voting')
        st.pyplot(fig)

    with row1_2, _lock:
        st.header('Repartition of votes in favor')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=df_votes_selected, x="percentage of votes in favor", bins=40)
        #ax = sns.scatterplot(data=df_votes_selected, x="nb votants", y="percentage of votes in favor")
        st.pyplot(fig)

    #heatmap (12;31) with a year selector and a data selector (nb of votes or presence)
    title_spacer2, title_2, title_spacer_2 = st.beta_columns((.1,ROW,.1))

    with title_2:
        st.header('Heatmap of the votes during the year')

    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))
    with row2_1, _lock:
        year_selected = st.selectbox('Select year', ['2017','2018','2019', '2020', '2021'], key='1')

    with row2_2, _lock:
        data_selected = st.selectbox('Select data', ['Nb of votes','Deputy presence'], key='2')

    df_heatmap = df_votes_selected.drop(columns=['code', 'type', 'titre', 'demandeur', 'requis', 'pour', 'contre', 'abstentions', 'datetime'])
    df_heatmap = df_heatmap.loc[df_heatmap['year'] == year_selected]
    df_heatmap['count'] = 1
    df_heatmap['nb votants'] = df_heatmap['nb votants']/574
    df_heatmap['nb votants'] = (df_heatmap['nb votants']*100).astype(int)

    df_heatmap = df_heatmap.groupby(['year','month','day']).agg({'nb votants':'mean','count':'sum'})

    if(data_selected == 'Nb of votes'):
        df_heatmap = df_heatmap.reset_index().pivot(index='month', columns='day', values='count')
        heatmap_title = 'Number of votes at the national assembly on a particular day'
    elif(data_selected == 'Deputy presence'):
        df_heatmap = df_heatmap.reset_index().pivot(index='month', columns='day', values='nb votants').astype(float)
        heatmap_title = 'Percentage of deputy presence at the national assembly on a particular day'

    df_heatmap.fillna(0, inplace=True)
    df_heatmap.columns = df_heatmap.columns.astype(int)
    df_heatmap.index = df_heatmap.index.astype(int)
    # Ensure all month in table
    df_heatmap = df_heatmap.reindex(range(1,13), axis=0, fill_value=0)
    # Ensure all days in table
    df_heatmap = df_heatmap.reindex(range(1,32), axis=1, fill_value=0).astype(int) 


    row3_spacer1, row3_1, row3_spacer2   = st.beta_columns((SPACER, ROW, SPACER))

    palette = sns.color_palette("Greens",12)
    palette[0] = (1,1,1)

    with row3_1, _lock:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax = sns.heatmap(df_heatmap,
                    cmap=palette,  # Choose a squential colormap
                    annot_kws={'fontsize':11},  # Reduce size of label to fit
                    fmt='',          # Interpret labels as strings
                    square=True,     # Force square cells
                    linewidth=0.01,  # Add gridlines
                    linecolor="#222", # Adjust gridline color
                    robust = True
                )
        ax.set_title(heatmap_title)
        ax.set_ylabel('Month of the year')
        ax.set_xlabel('Days of the month')
        plt.tight_layout()
        st.pyplot(fig)

    row4_spacer1, row4_1, row4_spacer2, row4_2, row4_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    #get the total number of demand from each party
    df_demandeur = df_votes_selected.drop(df_votes_selected.columns[0:10], axis=1)
    df_demandeur = df_demandeur.drop(df_demandeur.columns[-7:-1], axis=1)
    df_demandeur = df_demandeur.sum(axis=0) 
    df_demandeur = df_demandeur.drop(labels=['ND', 'GOV', 'EELV', 'MODEM', 'CDP'])

    #merge the dataframe with the number of demand with the polpar df to get colors and nb of members
    df = df_polpar.set_index('abreviated_name').merge(pd.DataFrame(data = [df_demandeur.values], columns = df_demandeur.index).T, left_index=True, right_index=True)
    df.columns = ['name', 'members', 'color', 'demand']
    df['demand per deputy'] = df['demand']/df['members']

    with row4_1, _lock:
        st.header('Number of law propositions')
        st.text('')
        st.text('')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df['demand'], labels=(df.index + ' (' + df['demand'].map(str) + ')'), 
                wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white'}, colors=df['color'].to_list())
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row4_2, _lock:
        st.header('Average number of law propositions per deputy')
        st.text('')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df['demand per deputy'], labels=(df.index + ' (' + round(df['demand per deputy'].map(float)).map(str) + ')'), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white'}, colors=df['color'].to_list())
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)
