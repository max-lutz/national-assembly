import streamlit as st
import pandas as pd
import base64
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
  
#configuration of the page
st.set_page_config(layout="wide")

matplotlib.use("agg")
_lock = RendererAgg.lock

#Loading the data
@st.cache
def get_data_deputies():
    df = pd.read_csv('df_dep.csv')
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df
deputies = get_data_deputies()

@st.cache
def get_data_political_parties():
    df = pd.read_csv('df_polpar.csv')
    df = df.drop(columns=['code'])
    df.rename(columns={"abreviated_name": "pol party"})
    return df
df_pol_parties = get_data_political_parties()

# Sidebar 
st.sidebar.header('User Input Features')

#selection box for the different features
pol_parties = deputies['pol party'].unique().tolist()
pol_party_selected = st.sidebar.multiselect('Political parties', pol_parties, pol_parties)
sex_selected = st.sidebar.selectbox('Select sex', ['both','female','male'])
sex_selected = [sex_selected]
if sex_selected == ['both']:
    sex_selected = ['female', 'male']
age_selected = st.sidebar.slider("Age", deputies['age'].min(), deputies['age'].max(), (deputies['age'].min(), deputies['age'].max()), 1)
nb_members_selected = st.sidebar.slider("Number of members", deputies['pol party'].value_counts().min(), deputies['pol party'].value_counts().max(), (25, deputies['pol party'].value_counts().max()), 1)
jobs = deputies["activity"].unique().tolist()
jobs_selected = st.sidebar.multiselect('Political parties', jobs, jobs)

#creates masks from the sidebar selection widgets
mask_pol_parties = deputies['pol party'].isin(pol_party_selected)
mask_sex = deputies['sex'].isin(sex_selected)
mask_jobs = deputies['activity'].isin(jobs_selected)
mask_age = deputies['age'].between(age_selected[0], age_selected[1])
mask_nb_members = deputies['pol party'].value_counts().between(nb_members_selected[0], nb_members_selected[1]).to_frame()
mask_nb_members = mask_nb_members[mask_nb_members['pol party'] == 1].index.to_list()
mask_nb_members = deputies['pol party'].isin(mask_nb_members)

st.title('French national assembly vizualisation tool')

st.markdown("""
This app performs simple vizualisation from the open data from the french national assembly!
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [national assembly open data](https://data.assemblee-nationale.fr/).
""")

st.write("")

display_df = deputies[mask_pol_parties & mask_sex & mask_jobs & mask_age & mask_nb_members]
display_df = display_df.sort_values(by=['pol party'])

st.write(display_df)

#create the color list for the plot
df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(pol_party_selected)].sort_values(by=['members'], ascending=False)
colors = df_with_selected_pol_parties['color'].tolist()

#row0_1, row0_2 = st.beta_columns(2)
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

with row0_1, _lock:
    st.header("Political parties")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(display_df['pol party'].value_counts(), labels=display_df['pol party'].value_counts().index, 
           wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
    p = plt.gcf()
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)


row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

#select colors
df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(display_df['pol party'].unique().tolist())].sort_values(by=['abreviated_name'])
colors = df_with_selected_pol_parties['color'].tolist()

with row1_1, _lock:
    st.header('Age repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax = sns.histplot(data=display_df, x="age", hue="pol party", multiple="stack", bins=12, 
                      stat="probability", palette=colors)
    st.pyplot(fig)


row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

#caluculate the proportion of women per parties

df_sex = pd.concat([deputies[mask_pol_parties & mask_jobs & mask_age & mask_nb_members].drop(columns=['code', 'activity', 'age']),pd.get_dummies(deputies[mask_pol_parties & mask_jobs & mask_age & mask_nb_members].drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
df_sex = df_sex.groupby(['pol party']).agg({'sex_female':'sum','sex_male':'sum'})
df_sex['pol party'] = df_sex.index
df_sex['total'] = df_sex['sex_female'].astype(int) + df_sex['sex_male'].astype(int)
df_sex['sex_female'] = df_sex['sex_female'].astype(int)/df_sex['total']

#select colors
df_sex = df_sex.reset_index(drop=True)
df_sex = df_sex.sort_values(by=['pol party'])

df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(df_sex['pol party'].unique().tolist())].sort_values(by=['abreviated_name'])
df_sex['color'] = df_with_selected_pol_parties['color'].tolist()

df_sex = df_sex.sort_values(by=['sex_female'], ascending=False)
colors = df_sex['color'].tolist()


with row2_1, _lock:
    row0_1.header('Percentage of women per political parties')
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=colors)
    row0_1.pyplot(fig)

row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

with row3_1, _lock:
    st.header('Previous job repartition')
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(display_df['activity'].value_counts(), labels=display_df['activity'].value_counts().index, wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
    p = plt.gcf()
    p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
    st.pyplot(fig)