import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd

# --- 1. BASIC SETTINGS ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# --- 2. DATABASE CONNECTION ---
conn = None
try:
    # Trying to connect with Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Connection Status: {e}")

# --- 3. UI DASHBOARD ---
st.title("🔬 PROF. NIDAN AI")

if conn is not None:
    st.success("Successfully Connected to Database!")
    email = st.text_input("Enter Email to Log In")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Log In"):
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
            user = df[df['Email'] == email]
            if not user.empty and str(user.iloc[0]['Password']) == password:
                st.balloons()
                st.write(f"Welcome back, {email}!")
                # AI Feature
                file = st.file_uploader("Upload Report", type=["jpg", "png"])
                if file:
                    img = Image.open(file)
                    st.image(img)
                    if st.button("Analyze"):
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(["Analyze this report", img])
                        st.write(res.text)
            else:
                st.error("Invalid Credentials")
        except Exception as e:
            st.error(f"Error reading data: {e}")
else:
    st.warning("⚠️ Waiting for Database to wake up...")
