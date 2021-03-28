import streamlit as st
from multiapp import MultiApp
from apps import home, parties_comparator # import your app modules here

#configuration of the page
#st.set_page_config(layout="wide")

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Comparator", parties_comparator.app)

# The main app
app.run()