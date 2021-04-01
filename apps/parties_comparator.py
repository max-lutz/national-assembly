import streamlit as st
import pandas as pd
import base64
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
  
st.set_page_config(layout="wide")

SPACER = .2
ROW = 1

#Loading the data
@st.cache
def get_data_deputies():
    df = pd.read_csv('df_dep.csv')
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df

@st.cache
def get_data_political_parties():
    df = pd.read_csv('df_polpar.csv')
    df = df.drop(columns=['code'])
    df.rename(columns={"abreviated_name": "pol party"})
    return df

#def app():
    #configuration of the page
    #st.set_page_config(layout="wide")
matplotlib.use("agg")
_lock = RendererAgg.lock

deputies = get_data_deputies()
df_pol_parties = get_data_political_parties()

title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))

with title:
    st.title('Compare groups of deputies depending on their political party')

st.sidebar.write("test")
    

# display_df = deputies[]
# display_df = display_df.sort_values(by=['pol party'])

#st.write(display_df)


### Political parties
#create the color list for the plot
# df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(pol_party_selected)].sort_values(by=['members'], ascending=False)
# colors = df_with_selected_pol_parties['color'].tolist()

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

with row0_1, _lock:
    party_1 = st.selectbox('Select political party', deputies['pol party'].unique(), key='1')
    deputies_group_1 = deputies[deputies['pol party'] == party_1]
    df = df_pol_parties.sort_values(by=['members'], ascending=False)
    df.loc[df['abreviated_name'] != party_1, 'color'] = 'lightgrey'
    colors = df['color'].tolist()
    df = df[df['abreviated_name'] == party_1]
    color_1 = df['color'].to_list()

    st.header("Number of members")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(deputies['pol party'].value_counts(), labels=(deputies['pol party'].value_counts().index), 
           wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
    p = plt.gcf()
    c2 = plt.Circle( (0,0), 0.7, color='white')
    text = str(deputies_group_1['pol party'].value_counts().map(str))
    label = ax.annotate('text', xy=(0,0), fontsize=30, ha='center')
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)

with row0_2, _lock:
    party_2 = st.selectbox('Select political party', deputies['pol party'].unique(), key='2')
    deputies_group_2 = deputies[deputies['pol party'] == party_2]
    df = df_pol_parties.sort_values(by=['members'], ascending=False)
    df.loc[df['abreviated_name'] != party_2, 'color'] = 'lightgrey'
    colors = df['color'].tolist()
    df = df[df['abreviated_name'] == party_2]
    color_2 = df['color'].to_list()

    st.header("Number of members")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(deputies['pol party'].value_counts(), labels=(deputies['pol party'].value_counts().index), 
           wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
    p = plt.gcf()
    c2 = plt.Circle( (0,0), 0.7, color='white')
    text = str(deputies_group_2['pol party'].value_counts().map(str))
    label = ax.annotate('text', xy=(0,0), fontsize=30, ha='center')
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)


### Age repartition
row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

with row1_1, _lock:
    st.header('Age repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax = sns.histplot(data=deputies_group_1, x="age", bins=12, stat="probability", palette = color_1)
    st.pyplot(fig)

with row1_2, _lock:
    st.header('Age repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax = sns.histplot(data=deputies_group_2, x="age", bins=12, stat="probability", palette = color_2)
    st.pyplot(fig)

# ### Percentage of women per parties
# row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

# #caluculate the proportion of women per parties
# df_sex = pd.concat([deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age']),pd.get_dummies(deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
# df_sex = df_sex.groupby(['pol party']).agg({'sex_female':'sum','sex_male':'sum'})
# df_sex['pol party'] = df_sex.index
# df_sex['total'] = df_sex['sex_female'].astype(int) + df_sex['sex_male'].astype(int)
# df_sex['sex_female'] = df_sex['sex_female'].astype(int)/df_sex['total']

# #select colors
# df_sex = df_sex.reset_index(drop=True)
# df_sex = df_sex.sort_values(by=['pol party'])

# df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(df_sex['pol party'].unique().tolist())].sort_values(by=['abreviated_name'])
# df_sex['color'] = df_with_selected_pol_parties['color'].tolist()

# df_sex = df_sex.sort_values(by=['sex_female'], ascending=False)
# colors = df_sex['color'].tolist()

# with row2_1, _lock:
#     st.header('Percentage of women per political parties')
#     fig, ax = plt.subplots(figsize=(5, 5))
#     sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=colors)

#     i = 0
#     text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()
#     for rect in ax.patches:
#         height = rect.get_height()
#         ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
#                 str(text[i])+'%', ha='center', va='bottom', rotation=0, color='white', fontsize=12)
#         i = i + 1

#     #autolabel(ax, (df_sex['sex_female'].round(2)*100).astype(int).to_list())
#     st.pyplot(fig)


### Job repartition
row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

with row3_1, _lock:
    st.header('Previous job repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(deputies_group_1['activity'].value_counts(), labels=(deputies_group_1['activity'].value_counts().index + ' (' + deputies_group_1['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
    p = plt.gcf()
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)

with row3_2, _lock:
    st.header('Previous job repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(deputies_group_2['activity'].value_counts(), labels=(deputies_group_2['activity'].value_counts().index + ' (' + deputies_group_2['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
    p = plt.gcf()
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)