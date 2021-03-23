import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date
  
#st.title('French national assembly vizualisation tool')

# st.markdown("""
# This app performs simple vizualisation from the open data from the french national assembly!
# * **Python libraries:** base64, pandas, streamlit
# * **Data source:** [national assembly open data](https://data.assemblee-nationale.fr/).
# """)

st.sidebar.header('User Input Features')




@st.cache
def get_data():
    df = pd.read_csv('df_dep.csv')
    #create the value age from the date of birth of the deputies
    df['age']  = df['date of birth'].astype(str).str[0:4]
    df['age']  = date.today().year - df['age'].astype(int)
    df = df.drop(columns=['family name', 'first name', 'date of birth'])
    return df
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

col1, col2 = st.beta_columns(2)

col1.header("Political parties")

# Create a circle at the center of the plot
c1 = plt.Circle( (0,0), 0.7, color='white')

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(display_df['pol party'].value_counts(), labels=display_df['pol party'].value_counts().index, wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
p = plt.gcf()
p.gca().add_artist(c1)
col1.pyplot(fig)

col2.header('Age repartition')
fig, ax = plt.subplots(figsize=(5, 5))
ax = sns.histplot(data=display_df, x="age", hue="pol party", multiple="stack", binwidth=5, stat="probability")
col2.pyplot(fig)

#st.write(display_df.drop(columns=['code', 'activity', 'age']))
df_sex = pd.concat([display_df.drop(columns=['code', 'activity', 'age']),pd.get_dummies(display_df.drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
df_sex = df_sex.drop(columns=['sex'])
df_sex = df_sex.groupby(['pol party']).agg({'sex_female':'sum','sex_male':'sum'})
df_sex['pol party'] = df_sex.index
df_sex['sex_female'] = df_sex['sex_female'].astype(int)
df_sex['sex_male'] = df_sex['sex_male'].astype(int)
df_sex['total'] = df_sex['sex_female']+df_sex['sex_male']
df_sex['sex_male'] = df_sex['sex_male']/df_sex['total']
df_sex['sex_female'] = df_sex['sex_female']/df_sex['total']
df_sex = df_sex.drop(columns=['total'])
df_sex = df_sex.sort_values(by=['sex_female'])
results = df_sex.set_index('pol party').T.to_dict('list')
category_names = ['Female', 'Male']

def hbarplot(results, category_names):
    """
    https://matplotlib.org/stable/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py
    Parameters
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname) in enumerate(zip(category_names)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname)
        xcenters = starts + widths / 2

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax

col1.header('Sex repartition')
fig, ax = hbarplot(results, category_names)
col1.pyplot(fig)

col2.header('Previous job repartition')
c2 = plt.Circle( (0,0), 0.7, color='white')
fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(display_df['activity'].value_counts(), labels=display_df['activity'].value_counts().index, wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
p = plt.gcf()
p.gca().add_artist(c2)
col2.pyplot(fig)