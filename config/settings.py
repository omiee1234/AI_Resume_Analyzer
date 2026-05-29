import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API")
if not API:
    API = st.secrets["API"]
