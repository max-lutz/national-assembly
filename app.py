import streamlit as st
from multiapp import MultiApp
from apps import home, parties_comparator, vote_summary, deputies # import your app modules here

#configuration of the page
st.set_page_config(layout="wide")

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Comparator", parties_comparator.app)
app.add_app("Votes", vote_summary.app)
app.add_app("Deputies", deputies.app)

# The main app
app.run()