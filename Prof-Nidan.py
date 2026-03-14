import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, datetime, re, pandas as pd, io
from gtts import gTTS
from fpdf import FPDF
import streamlit.components.v1 as components

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide", page_icon="⚖️")

def check_env():
    # সিক্রেটস চেক করার লজিক (Traceback রোধে)
    keys = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD", "ADMIN_PASSWORD"]
    for k in keys:
        if k not in st.secrets:
            st.warning(f"⚠️ Configuration Missing: {k} in Secrets Box.")
            st.stop()
check_env()

# --- 2. ADVANCED CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none;
    }
    .auth-card { padding: 30px; border-radius: 20px; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .impact-stats { text-align: center; padding: 20px; border-radius: 15px; background: white; border-top: 5px solid #004a99; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC ALTERNATING SLIDER ---
def render_master_slider():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:400px; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <img id="view" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:400px; object-fit:cover; transition: 1.2s;">
        <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.7); color:white; width:100%; padding:25px; text-align:center;">
            <h2 id="t">PROF. NIDAN</h2><p id="d">Leading with Science, Driven by
