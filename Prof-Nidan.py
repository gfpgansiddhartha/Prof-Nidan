import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import pandas as pd

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# Initialize Connection variable as None
conn = None

# --- 2. TRY DATABASE CONNECTION ---
try:
    # This tries to connect only if Secrets are formatted correctly
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.sidebar.error(f"📡 Database Offline: Check your Secrets")

# --- 3. UI LAYOUT ---
st.title("🔬 PROF. NIDAN AI TERMINAL")

# --- 4. LOGIN / BYPASS LOGIC ---
# If database fails, we show a simplified version so you can still use AI
if conn is None:
    st.warning("⚠️ Database connection failed. Running in 'Guest Mode'.")
    authorized = True # Let you in for now so you can see it working!
else:
    authorized = False
    with st.expander("🔐 Log In to Secure Terminal", expanded=True):
        email = st.text_input("User Email")
        password = st.text_input("Password", type="password")
        if st.button("Unlock Dashboard"):
            try:
                df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                user = df[df['Email'] == email]
                if not user.empty and str(user.iloc[0]['Password']) == password:
                    authorized = True
                    st.success(f"Welcome back, {email}!")
                else:
                    st.error("Invalid Credentials.")
            except:
                st.error("Error reading Users sheet. Check sheet names.")

# --- 5. MAIN AI FEATURE ---
if authorized:
    st.divider()
    st.subheader("📋 AI Specimen Analysis")
    uploaded_file = st.file_uploader("Upload Medical Image (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Specimen", width=400)
        
        if st.button("Analyze with Gemini AI"):
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("Missing Gemini API Key in Streamlit Secrets!")
            else:
                with st.spinner("AI is thinking..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(["Provide a scientific summary of this medical report", img])
                        st.markdown("### Analysis Report:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI Engine Error: {e}")                    if st.button("Analyze with Gemini"):
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(["Describe this clinical specimen", img])
                        st.write(res.text)
            else:
                st.error("Invalid Login Details.")
        except Exception as e:
            st.error(f"Database Error: {e}")
else:
    # কানেকশন না হলে এটি দেখাবে
    st.warning("⚠️ Waiting for Database connection... Please check Secrets.")
