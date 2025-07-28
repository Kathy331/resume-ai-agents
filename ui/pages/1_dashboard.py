# ui/pages/1_dashboard.py
import streamlit as st
from components.dashboard import show_dashboard
from components.sidebar import show_sidebar

show_sidebar()
show_dashboard()