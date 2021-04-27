import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.backends.backend_agg import RendererAgg
from datetime import date
  
# Home page of the website
# Displays general information about political parties at the national assembly

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
    df.rename(columns={"abreviated_name": "pol party"})
    return df

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

    # Sidebar 
    #selection box for the different features
    st.sidebar.header('Select what to display')
    pol_parties = df_deputies['pol party'].unique().tolist()
    pol_party_selected = st.sidebar.multiselect('Political parties', pol_parties, pol_parties)
    sex_selected = st.sidebar.selectbox('Select sex', ['both','female','male'])
    sex_selected = [sex_selected]
    if sex_selected == ['both']:
        sex_selected = ['female', 'male']
    age_selected = st.sidebar.slider("Age", int(df_deputies['age'].min()), int(df_deputies['age'].max()), (int(df_deputies['age'].min()), int(df_deputies['age'].max())), 1)
    nb_members_selected = st.sidebar.slider("Number of members", int(df_deputies['pol party'].value_counts().min()), int(df_deputies['pol party'].value_counts().max()), (int(df_deputies['pol party'].value_counts().min()), int(df_deputies['pol party'].value_counts().max())), 1)

    #creates masks from the sidebar selection widgets
    mask_pol_parties = df_deputies['pol party'].isin(pol_party_selected)
    mask_sex = df_deputies['sex'].isin(sex_selected)
    mask_age = df_deputies['age'].between(age_selected[0], age_selected[1])
    mask_nb_members = df_deputies['pol party'].value_counts().between(nb_members_selected[0], nb_members_selected[1]).to_frame()
    mask_nb_members = mask_nb_members[mask_nb_members['pol party'] == 1].index.to_list()
    mask_nb_members = df_deputies['pol party'].isin(mask_nb_members)

    title_spacer1, title, title_spacer_2 = st.beta_columns((.1,ROW,.1))

    with title:
        st.title('French national assembly vizualisation tool')
        st.markdown("""
            This app performs simple vizualisation from the open data from the french national assembly!
            The data used are for the period June 2017 to March 2021 (XVth legislature of the Fifth French Republic, President Macron)
            * Use the menu on the left to select the data or the page you want to access
            * Your plots will appear below
            * Data source (accessed mid march 2021): [national assembly open data](https://data.assemblee-nationale.fr/).
            * The code can be accessed at [code](https://github.com/max-lutz/open-data-french-national-assembly).
            """)

    df_deputies_selected = df_deputies[mask_pol_parties & mask_sex & mask_age & mask_nb_members]
    df_deputies_selected = df_deputies_selected.sort_values(by=['pol party'])
    pol_party_selected = df_deputies_selected['pol party'].unique()

    ### Political parties
    #create the color list for the plot

    # merge the political parties dataframe with the selected deputies
    df_with_selected_pol_parties = pd.merge(pd.DataFrame(df_deputies_selected['pol party'].value_counts()), df_pol_parties, left_index=True, right_on='abreviated_name')
    colors = df_with_selected_pol_parties['color'].tolist()

    row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

    with row0_1, _lock:
        st.header("Political parties")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies_selected['pol party'].value_counts(), labels=(df_deputies_selected['pol party'].value_counts().index + ' (' + df_deputies_selected['pol party'].value_counts().map(str) + ')'), 
            wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' }, colors=colors)
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row0_2:
        df_with_selected_pol_parties = df_with_selected_pol_parties.reset_index(drop=True)
        text = ''
        for i in range(len(df_with_selected_pol_parties)):
            text = text + df_with_selected_pol_parties.loc[i,'abreviated_name'] + ' : ' + df_with_selected_pol_parties.loc[i,'name'] + '  \n'
        for i in range(5):
            st.write("")
        st.write(text)
        
    ### Age repartition
    row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row1_1, _lock:
        st.header('Age repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax = sns.histplot(data=df_deputies_selected, x="age", bins=12, stat="probability")
        st.pyplot(fig)

    ### Percentage of women per parties
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns((SPACER,ROW,SPACER,ROW, SPACER))

    #calculate the proportion of women per parties
    df_sex = pd.concat([df_deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age']),
                        pd.get_dummies(df_deputies[mask_pol_parties & mask_nb_members].drop(columns=['code', 'activity', 'age'])['sex'], 
                        prefix='sex')],axis=1)
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
        st.header('Percentage of women per political parties')
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x="sex_female", y="pol party", data=df_sex, ax=ax, palette=colors)

        i = 0
        text = (df_sex['sex_female'].round(2)*100).astype(int).to_list()
        for rect in ax.patches:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., rect.get_y() + height * 3 / 4.,
                    str(text[i])+'%', ha='center', va='bottom', rotation=0, color='white', fontsize=12)
            i = i + 1
        st.pyplot(fig)


    ### Job repartition

    job_description = {
        'Cadres' : 'Executives, engineers and professors',
        'Entrepreneurs' : 'Craftsmen and business owners',
        'Prof. inter.' : 'Intermediate Professions',
        'Retraités' : 'Retired',
        'Employés' : 'Employees',
        'Non déclaré' : 'Not declared',
        'Ouvriers' : 'Worker',
        'Agriculteurs' : 'Farmer'
    }

    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((SPACER,ROW, SPACER,ROW, SPACER))

    with row3_1, _lock:
        st.header('Previous job repartition')
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df_deputies_selected['activity'].value_counts(), labels=(df_deputies_selected['activity'].value_counts().index + ' (' + df_deputies_selected['activity'].value_counts().map(str) + ')'), wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(plt.Circle( (0,0), 0.7, color='white'))
        st.pyplot(fig)

    with row3_2:
        job_list = df_deputies_selected['activity'].value_counts().index
        text = ''
        for i in range(len(job_list)):
            text = text + job_list[i] + ' : ' + job_description[job_list[i]] + '  \n'
        for i in range(5):
            st.write("")
        st.write(text)
