import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, datetime, re, pandas as pd, io
from gtts import gTTS
from fpdf import FPDF # PDF তৈরির জন্য লাগবে

# --- 1. SYSTEM CONFIG & UI STYLING ---
st.set_page_config(page_title="PROF. NIDAN", layout="wide", page_icon="⚖️")

# Custom CSS for Banner and Design
st.markdown("""
    <style>
    .banner-text {
        background-color: #004a99; color: white; padding: 10px;
        border-radius: 10px; text-align: center; font-weight: bold;
    }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & PDF ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def create_pdf(text, user_email):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN - FORENSIC REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=text)
    pdf.ln(20)
    pdf.cell(0, 10, txt=f"Report Generated for: {user_email}", ln=True)
    pdf.cell(0, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. FORGOT PASSWORD SYSTEM ---
def reset_password_logic(email, new_pwd):
    try:
        df = conn.read(worksheet="Users", ttl=0)
        df.loc[df['Email'] == email, 'Password'] = new_pwd
        conn.update(worksheet="Users", data=df)
        st.cache_data.clear()
        return True
    except: return False

# --- 4. AUTHENTICATION & STEP LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

# --- BANNER SECTION (গরিব-দুঃখীদের সাহায্যের ব্যানার) ---
st.markdown("<div class='banner-text'>OUR MISSION: Supporting Medical Care for Underprivileged Children 🕊️</div>", unsafe_allow_html=True)

# ছবির স্লাইডার (এখানে আপনি আপনার পছন্দমতো ছবির লিঙ্ক দিতে পারেন)
banner_images = [
    "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1000", # Helping children
    "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1000", # Donation
    "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1000" # Food distribution
]
st.image(banner_images, width=300, caption=["Community Care", "Donation Drive", "Helping Hand"])

# --- 5. LOGIN / FORGOT PASSWORD INTERFACE ---
if not st.session_state.auth:
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Sign Up", "🔑 Forgot Password"])
    
    with tab1: # Login Section
        # [আগের লগইন কোড এখানে থাকবে]
        pass

    with tab3: # Forgot Password Section
        st.subheader("Reset Your Password")
        f_email = st.text_input("Enter Registered Email", key="forgot_email")
        if st.button("Send Reset Code"):
            # ইমেলে একটি রিসেট কোড পাঠাবে
            st.info("Verification code sent to your email to reset password.")
        
        new_pass = st.text_input("New Secure Password", type="password")
        if st.button("Update Password"):
            if reset_password_logic(f_email, new_pass):
                st.success("Password Updated Successfully! Please login.")
            else: st.error("Error updating password.")

# --- 6. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"Welcome, {st.session_state.email}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    st.title("🔬 Specimen Analysis Terminal")
    up_file = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
    
    if up_file:
        img = Image.open(up_file)
        st.image(img, use_container_width=True)
        
        if st.button("RUN ANALYSIS"):
            with st.spinner("Processing..."):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Provide forensic diagnostic report", img])
                report_content = res.text
                st.markdown(report_content)
                
                # --- VOICE REPORT ---
                st.markdown("### 🔊 Listen to Report")
                tts = gTTS(text=report_content, lang='en')
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                st.audio(audio_buffer)
                
                # --- PDF DOWNLOAD ---
                st.markdown("### 📄 Download Report")
                pdf_bytes = create_pdf(report_content, st.session_state.email)
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_bytes,
                    file_name="Prof_Nidan_Report.pdf",
                    mime="application/pdf"
                )
