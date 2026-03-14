import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# Initialize Connection
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.sidebar.error("📡 Database connection failed.")

# --- 2. HEADER ---
st.title("🔬 PROF. NIDAN AI TERMINAL")
st.markdown("---")

# --- 3. LOGIN LOGIC ---
authorized = False

if conn is not None:
    with st.container():
        st.subheader("🔐 Secure Login")
        email = st.text_input("User Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Unlock Dashboard"):
            try:
                df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                user = df[df['Email'] == email]
                if not user.empty and str(user.iloc[0]['Password']) == password:
                    authorized = True
                    st.success(f"Access Granted! Welcome {email}")
                else:
                    st.error("Invalid Email or Password.")
            except:
                st.error("Sheet error: Please check if 'Users' sheet exists.")
else:
    st.info("⚠️ Guest Mode: Database is currently offline.")
    authorized = True # Let you use the AI even if DB is down

# --- 4. MAIN FEATURE (AI ANALYSIS) ---
if authorized:
    st.subheader("📋 Specimen Analysis Engine")
    uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Specimen Preview", width=400)
        
        # Analyze Button
        if st.button("Start AI Analysis"):
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("Secret Key Missing: Please add GEMINI_API_KEY in Streamlit Secrets.")
            else:
                with st.spinner("AI is analyzing the specimen..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(["Analyze this medical image scientifically", img])
                        st.markdown("### 🔬 Analysis Report")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI Engine Error: {e}")
