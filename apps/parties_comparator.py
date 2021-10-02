import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
 
#Loading the data
@st.cache
def get_data_deputies():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_dep.csv'))
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_polpar.csv'))
    df = df.drop(columns=['code'])
    df = df.rename(columns={"abreviated_name": "pol party"})
    return df

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
def get_data_vote_total():
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'df_vote_total.csv'),
    dtype={
        'pour': bool,
        'contre': bool,
        'abstentions' : bool,
        'par delegation' : bool
            })
    df['deputy code'] = df['deputy code'].astype("category")
    df['scrutin'] = df['scrutin'].astype("category")
    return df

###
# This function allows to plot graphs while highlighting one political party.
# The color of all other parties are changed to lightgrey (which would be the default color)
def apply_grey_filter(df, party):
    df_2 = df.copy(deep=True)
    df_2.loc[df_2['pol party'] != party, 'color'] = 'lightgrey'
    return df_2['color'].tolist()

###
# Returns a small description of all parties
# The source used to write these description is wikipedia.
def get_party_description(party):
    parties = {
        'LAREM': 'La République En Marche! (translatable as "The Republic...On the Move). It is a centrist and liberal political party in France. The party was founded on 6 April 2016 by Emmanuel Macron. Presented as a pro-European party, Macron considers LREM to be a progressive movement, uniting both the left and the right',
        'PS' : 'The Socialist Party (PS) is a French political party historically classified on the left and more recently on the center left of the political spectrum. Launched in 1969, it has its origins in the socialist school of thought.',
        'REP' : 'Les Républicains (LR) is a French Gaullist and liberal-conservative political party, classified on the right and center right of the political spectrum. It emerged from the change of name and statutes of the Union for a Popular Movement (UMP) in 2015. It is in line with the major conservative parties.',
        'MODEM' : 'The Democratic Movement (MODEM) is a French political party of the center created by François Bayrou (then president of the UDF) following the presidential election of 2007. The MODEM aims to bring together democrats concerned with an independent and central position on the political scene.',
        'FI' : 'La France insoumise (FI) is a French political party founded on February 10, 2016 by Jean Luc Mélanchon. Its political positioning is mainly considered radical left, but also sometimes far left.',
        'ND' : 'Not declared. This category represents all the people not affiliated to a political party or affiliated to a political party but with less than 7 deputies at the national assembly.',
        'RPS' : 'Régions et peuples solidaires (RPS) is a political party that federates regionalist or autonomist political organizations in France. The political currents represented range from centrism to democratic socialism with a strong environmentalist sensibility.',
        'UDRL' : 'The Union of Democrats and Independents (UDI, also called Union des Démocrates Radicaux et Libéraux; UDRL) is a French center-right political party, founded by Jean-Louis Borloo on October 21, 2012. Until 2018, the UDI is composed of different parties that retain their existence, forming a federation of parties.',
        'PCF' : "The French Communist Party (French: Parti communiste français, PCF) is a communist party in France. Founded in 1920 by the majority faction of the socialist French Section of the Workers' International (SFIO).",
        'EELV' : 'Europe Écologie Les Verts (abbreviated to EELV) is a French environmentalist political party that succeeded the party Les Verts on November 13, 2010, following a change of statutes to bring together the activists who came as part of the lists Europe Écologie in the European elections of 2009 and regional elections of 2010.'    
    }
    return parties[party]

def get_label_plot_political_parties(df_dep, deputies_count):
    text = df_dep['pol party'].value_counts().index[0] + ' : ' 
    text = text + df_dep['pol party'].value_counts().map(str).to_list()[0] + '\n('
    return text + str(round(100*df_dep['pol party'].value_counts().to_list()[0]/deputies_count,2)) + '%)'

###
# Main application of parties comparator
# This function allows the user to compare two different parties
# The page is organized in two columns and two selectbox are used for selection

def app():
    #configuration of the page
    #st.set_page_config(layout="wide")
    matplotlib.use("agg")
    _lock = RendererAgg.lock

    SPACER = .2
    ROW = 1

    #load dataframes
    df_deputies = get_data_deputies()
    df_pol_parties = get_data_political_parties()
    df_votes = get_data_votes()
    df_vote_total = get_data_vote_total()

    title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))
    with title:
        st.title('Compare political party at the national assembly')

    ### Select box and description
    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))
    with row0_1, _lock:
        party_1 = st.selectbox('Select political party', df_deputies['pol party'].unique(), index=6, key='1')
        st.write(get_party_description(party_1))
        deputies_group_1 = df_deputies[df_deputies['pol party'] == party_1]

    with row0_2, _lock:
        party_2 = st.selectbox('Select political party', df_deputies['pol party'].unique(), index=1, key='2')
        st.write(get_party_description(party_2))
        deputies_group_2 = df_deputies[df_deputies['pol party'] == party_2]

    ### Political parties
    row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))
    with row1_1, _lock:
        df_display_pol_parties = df_pol_parties.sort_values(by=['members'], ascending=False)

        st.header("Number of members")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies['pol party'].value_counts(), labels=(df_deputies['pol party'].value_counts().index), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=apply_grey_filter(df_display_pol_parties, party_1))
        label = ax.annotate(get_label_plot_political_parties(deputies_group_1, len(df_deputies.index)), xy=(0,-0.15), fontsize=22, ha='center')
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row1_2, _lock:
        df_display_pol_parties = df_pol_parties.sort_values(by=['members'], ascending=False)

        st.header("Number of members")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies['pol party'].value_counts(), labels=(df_deputies['pol party'].value_counts().index), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=apply_grey_filter(df_display_pol_parties, party_2))
        label = ax.annotate(get_label_plot_political_parties(deputies_group_2, len(df_deputies.index)), xy=(0,-0.15), fontsize=22, ha='center')
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    ### Age repartition
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))
    with row2_1, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=deputies_group_1, x="age", bins=12, stat="probability", palette = df_pol_parties.loc[df_pol_parties['pol party']==party_1]['color'])
        st.pyplot(fig)

    with row2_2, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=deputies_group_2, x="age", bins=12, stat="probability", palette = df_pol_parties.loc[df_pol_parties['pol party']==party_2]['color'])
        st.pyplot(fig)

    ### Percentage of women per parties
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

    #caluculate the proportion of women per parties
    df_sex = pd.concat([df_deputies.drop(columns=['code', 'activity', 'age']),pd.get_dummies(df_deputies.drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
    df_sex = df_sex.groupby(['pol party']).agg({'sex_female':'sum','sex_male':'sum'})
    df_sex['pol party'] = df_sex.index
    df_sex['total'] = df_sex['sex_female'].astype(int) + df_sex['sex_male'].astype(int)
    df_sex['sex_female'] = df_sex['sex_female'].astype(int)/df_sex['total']

    #prepare df_sex for color selection
    df_sex = df_sex.reset_index(drop=True)
    df_sex = df_sex.sort_values(by=['pol party'])
    df_with_selected_pol_parties = df_pol_parties[df_pol_parties['pol party'].isin(df_sex['pol party'].unique().tolist())].sort_values(by=['pol party'])
    df_sex['color'] = df_with_selected_pol_parties['color'].tolist()
    df_sex = df_sex.sort_values(by=['sex_female'], ascending=False).reset_index(drop=True)

    with row3_1, _lock:
        st.header('Percentage of women deputies')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=apply_grey_filter(df_sex, party_1))
        #write the percentage value in the rectangle of party 1 in the barplot
        text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()[int(np.where(df_sex['pol party']==party_1)[0])]
        rect = ax.patches[int(np.where(df_sex['pol party']==party_1)[0])]
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + rect.get_height() * 3 / 4.,
                str(text)+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
        ax.set(xlabel=None, ylabel=None, xticklabels=[])
        st.pyplot(fig)

    with row3_2, _lock:
        st.header('Percentage of women deputies')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=apply_grey_filter(df_sex, party_2))
        #write the percentage value in the rectangle of party 2 in the barplot
        text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()[int(np.where(df_sex['pol party']==party_2)[0])]
        rect = ax.patches[int(np.where(df_sex['pol party']==party_2)[0])]
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + rect.get_height() * 3 / 4.,
                str(text)+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
        ax.set(xlabel=None, ylabel=None, xticklabels=[])
        st.pyplot(fig)


    ### Job repartition
    row4_spacer1, row4_1, row4_spacer2, row4_2, row4_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row4_1, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(deputies_group_1['activity'].value_counts(), labels=(deputies_group_1['activity'].value_counts().index + ' (' + deputies_group_1['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row4_2, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(deputies_group_2['activity'].value_counts(), labels=(deputies_group_2['activity'].value_counts().index + ' (' + deputies_group_2['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    ### Average presence / average vote (for, against, absent)

    #get the average presence to the votes and average position of each party
    nb_votes = len(df_vote_total['scrutin'].unique())
    df_vote_total = pd.merge(df_vote_total, df_deputies.drop(columns=['sex', 'activity','age']), left_on='deputy code', right_on='code')
    df_vote_total['vote'] = 1
    for column in ['pour', 'contre', 'abstentions', 'par delegation']:
        df_vote_total[column] = df_vote_total[column].astype(int)

    #Sum all votes of deputies per party
    df_vote_total = df_vote_total.drop(columns=['scrutin', 'deputy code']).groupby(['pol party']).agg({'pour':'sum','contre':'sum', 'abstentions':'sum', 'non votants':'sum', 'par delegation':'sum', 'vote':'sum'})
    df_vote_total = pd.merge(df_vote_total, df_pol_parties.drop(columns=['name']), left_on='pol party', right_on='pol party')

    #calculate the average presence to the votes and average position of each party
    for column in ['vote', 'pour', 'contre', 'abstentions', 'par delegation']:
        df_vote_total[column] = df_vote_total[column]/(df_vote_total['members']*nb_votes)
    df_vote_total = df_vote_total.sort_values(by=['vote'], ascending=False).reset_index(drop=True)

    row5_spacer1, row5_1, row4_spacer2, row5_2, row5_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))
    with row5_1, _lock:
        st.header("Presence to the votes")
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="vote", y="pol party", data=df_vote_total, ax=ax, palette=apply_grey_filter(df_vote_total, party_1))
        text = (df_vote_total['vote'].round(4)*100).astype(float).round(4).to_list()[int(np.where(df_sex['pol party']==party_1)[0])]
        rect = ax.patches[int(np.where(df_vote_total['pol party']==party_1)[0])]
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + rect.get_height() * 3 / 4.,
                str(text)+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
        ax.set(xlabel='Average percentage of deputies at each vote', ylabel=None, xticklabels=[])
        st.pyplot(fig)
        
    with row5_2, _lock:
        st.header("Presence to the votes")
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="vote", y="pol party", data=df_vote_total, ax=ax, palette=apply_grey_filter(df_vote_total, party_2))
        text = (df_vote_total['vote'].round(4)*100).astype(float).round(4).to_list()[int(np.where(df_sex['pol party']==party_2)[0])]
        rect = ax.patches[int(np.where(df_vote_total['pol party']==party_2)[0])]
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + rect.get_height() * 3 / 4.,
                str(text)+'%', ha='center', va='bottom', rotation=0, color='black', fontsize=12)
        ax.set(xlabel='Average percentage of deputies at each vote', ylabel=None, xticklabels=[])
        st.pyplot(fig)
        
    ### Vote repartition
    row6_spacer1, row6_1, row6_spacer2, row6_2, row6_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    df_vote_total = df_vote_total.set_index('pol party')
    vote_repartition = df_vote_total.loc[party_1, ['pour', 'contre', 'abstentions']].to_list()
    vote_repartition_n = vote_repartition/(sum(vote_repartition)/100)
    vote_repartition_n = vote_repartition_n.round(1)

    with row6_1, _lock:
        st.header('Vote repartition for '+party_1)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(vote_repartition_n, labels=['pour ('+str(vote_repartition_n[0])+'%)', 
                                        'contre ('+str(vote_repartition_n[1])+'%)',
                                        'abstentions ('+str(vote_repartition_n[2])+'%)'], 
                                        wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white'},
                                        colors=['green', 'red', 'grey'])
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    vote_repartition = df_vote_total.loc[party_2, ['pour', 'contre', 'abstentions']].to_list()
    vote_repartition_n = vote_repartition/(sum(vote_repartition)/100)
    vote_repartition_n = vote_repartition_n.round(1)

    with row6_2, _lock:
        st.header('Vote repartition for '+party_2)
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(vote_repartition_n, labels=['pour ('+str(vote_repartition_n[0])+'%)', 
                                        'contre ('+str(vote_repartition_n[1])+'%)',
                                        'abstentions ('+str(vote_repartition_n[2])+'%)'], 
                                        wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white'},
                                        colors=['green', 'red', 'grey'])
        plt.gcf().gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)