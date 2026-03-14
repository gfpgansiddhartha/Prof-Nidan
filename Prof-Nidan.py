import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# Initialize Connection with Error Handling
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Connection Failed: {e}")

# --- 2. UI DASHBOARD ---
st.title("🔬 PROF. NIDAN AI")

if conn is not None:
    # ডাটাবেস সচল থাকলে এটি দেখাবে
    email = st.text_input("Email", key="login_em")
    password = st.text_input("Password", type="password", key="login_pw")
    
    if st.button("Access Dashboard"):
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
            user_match = df[df['Email'] == email]
            if not user_match.empty and str(user_match.iloc[0]['Password']) == password:
                st.success(f"Welcome, {email}!")
                st.balloons()
                # --- AI PART ---
                file = st.file_uploader("Upload Medical Image", type=["jpg", "png"])
                if file:
                    img = Image.open(file)
                    st.image(img)
                    if st.button("Analyze with Gemini"):
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
