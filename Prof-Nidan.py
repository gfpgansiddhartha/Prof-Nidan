import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, pandas as pd, io
from gtts import gTTS
import streamlit.components.v1 as components

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI | Science & Care", layout="wide", page_icon="🔬")

# DIRECT GOOGLE SHEET URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# Initialize Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Connection Offline: {e}")

# --- EMAIL FUNCTION ---
def send_security_mail(receiver, otp):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart(); msg['From'] = f"PROF. NIDAN Support <{sender}>"; msg['To'] = receiver; msg['Subject'] = f"Code: {otp}"
        msg.attach(MIMEText(f"Your code is: {otp}", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False

# --- AUTHENTICATION & UI ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

if not st.session_state.auth:
    t_log, t_reg = st.tabs(["🔐 Login", "📝 Register"])
    with t_log:
        em = st.text_input("Email", key="l_em")
        pw = st.text_input("Password", type="password", key="l_pw")
        if st.button("LOGIN"):
            try:
                df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                if not df[df['Email'] == em].empty:
                    st.session_state.auth = True; st.rerun()
                else: st.error("User not found.")
            except Exception as e: st.error(f"Error: {e}")
else:
    st.success("Welcome to PROF. NIDAN!")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()
