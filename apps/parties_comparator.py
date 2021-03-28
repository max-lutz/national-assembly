import streamlit as st
import pandas as pd
import base64
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
  
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

def autolabel(rects, text_list):
    i = 0
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                str(text_list[i])+'%', ha='center', va='bottom', rotation=0, color='white', fontsize=12)
        i = i + 1

def app():
    #configuration of the page
    matplotlib.use("agg")
    lock = RendererAgg.lock

    deputies = get_data_deputies()
    df_pol_parties = get_data_political_parties()

    # Sidebar 
    #selection box for the different features
    st.sidebar.header('Select what to display')
    pol_parties = deputies['pol party'].unique().tolist()
    pol_party_selected = st.sidebar.multiselect('Political parties', pol_parties, pol_parties)
    sex_selected = st.sidebar.selectbox('Select sex', ['both','female','male'])
    sex_selected = [sex_selected]
    if sex_selected == ['both']:
        sex_selected = ['female', 'male']
    age_selected = st.sidebar.slider("Age", deputies['age'].min(), deputies['age'].max(), (deputies['age'].min(), deputies['age'].max()), 1)
    nb_members_selected = st.sidebar.slider("Number of members", deputies['pol party'].value_counts().min(), deputies['pol party'].value_counts().max(), (deputies['pol party'].value_counts().min(), deputies['pol party'].value_counts().max()), 1)

    #creates masks from the sidebar selection widgets
    mask_pol_parties = deputies['pol party'].isin(pol_party_selected)
    mask_sex = deputies['sex'].isin(sex_selected)
    mask_age = deputies['age'].between(age_selected[0], age_selected[1])
    mask_nb_members = deputies['pol party'].value_counts().between(nb_members_selected[0], nb_members_selected[1]).to_frame()
    mask_nb_members = mask_nb_members[mask_nb_members['pol party'] == 1].index.to_list()
    mask_nb_members = deputies['pol party'].isin(mask_nb_members)



    st.title('Comparator')
    st.markdown("""
        This app performs simple vizualisation from the open data from the french national assembly!
        * **Python libraries:** base64, pandas, streamlit
        * **Data source:** [national assembly open data](https://data.assemblee-nationale.fr/).
        """)

    display_df = deputies[mask_pol_parties & mask_sex & mask_age & mask_nb_members]
    display_df = display_df.sort_values(by=['pol party'])

    #st.write(display_df)


    ### Political parties
    #create the color list for the plot
    df_with_selected_pol_parties = df_pol_parties[df_pol_parties['abreviated_name'].isin(pol_party_selected)].sort_values(by=['members'], ascending=False)
    colors = df_with_selected_pol_parties['color'].tolist()

    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

    with row0_1, _lock:
        st.header("Political parties")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(display_df['pol party'].value_counts(), labels=(display_df['pol party'].value_counts().index + ' (' + display_df['pol party'].value_counts().map(str) + ')'), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row0_2:
        st.write("")
        st.write(display_df['pol party'].value_counts())


    ### Age repartition
    row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

    with row1_1, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=display_df, x="age", bins=12, stat="probability")
        st.pyplot(fig)


    ### Percentage of women per parties
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

    #caluculate the proportion of women per parties
    df_sex = pd.concat([deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age']),pd.get_dummies(deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age'])['sex'], prefix='sex')],axis=1)
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

        autolabel(ax.patches, (df_sex['sex_female'].round(2)*100).astype(int).to_list())
        row0_1.pyplot(fig)


    ### Job repartition
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.1, 1, .1, 1, .1))

    with row3_1, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(display_df['activity'].value_counts(), labels=(display_df['activity'].value_counts().index + ' (' + display_df['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)