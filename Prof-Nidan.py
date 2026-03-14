import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd

# --- 1. SETTINGS ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# --- 2. DATABASE CONNECTION ---
conn = None
try:
    # This tries to connect to your Google Sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Connection Failed: {e}")

# --- 3. UI ---
st.title("🔬 PROF. NIDAN AI DASHBOARD")

if conn is not None:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            try:
                df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                user = df[df['Email'] == email]
                if not user.empty and str(user.iloc[0]['Password']) == password:
                    st.success(f"Welcome {email}!")
                    st.balloons()
                else:
                    st.error("Invalid Email or Password")
            except Exception as e:
                st.error(f"Database Error: {e}")
                
    with tab2:
        st.info("Registration is currently handled by Admin.")
else:
    st.warning("Please check your Streamlit Secrets for Google Sheets configuration.")
