import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, pandas as pd, io
from gtts import gTTS
from fpdf import FPDF
import streamlit.components.v1 as components

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI | Science & Care", layout="wide", page_icon="🔬")

def validate_config():
    """Checks if all required secrets are present."""
    required = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD", "ADMIN_PASSWORD"]
    for key in required:
        if key not in st.secrets:
            st.warning(f"⚠️ Configuration Missing: '{key}' not found in Secrets.")
            st.stop()
validate_config()

# --- 2. ADVANCED UI STYLING (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none; transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.85; transform: translateY(-2px); }
    .auth-card { padding: 30px; border-radius: 20px; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .impact-stats { 
        text-align: center; padding: 20px; border-radius: 15px; 
        background: white; border-top: 5px solid #004a99; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
    }
    h3 { color: #004a99; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC BANNER SLIDER (10 Alternate Slides: Tech & Charity) ---
def render_nidan_banner():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:380px; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <img id="v" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:380px; object-fit:cover; transition: 1.2s;">
        <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.75); color:white; width:100%; padding:20px; text-align:center;">
            <h2 id="t" style="margin:0; font-family: Arial;">PROF. NIDAN</h2>
            <p id="d" style="font-size:18px; color:#ddd;">Leading with Science, Driven by Care</p>
        </div>
    </div>
    <script>
        const s = [
            {i: "https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200", t: "Clinical AI Engine 🧬", d: "High-precision diagnostic report analysis"},
            {i: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200", t: "Our Social Mission ❤️", d: "Funding treatment for underprivileged children"},
            {i: "https://images.unsplash.com/photo-1532187863486-abf9d39d6618?q=80&w=1200", t: "Forensic Intelligence 🔬", d: "Scientific identification of medical specimens"},
            {i: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1200", t: "Charity & Trust 🕊️", d: "Providing free healthcare support to those in need"},
            {i: "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=1200", t: "Advanced Lab Tech 💻", d: "Empowering healthcare with AI-driven insights"},
            {i: "https://images.unsplash.com/photo-1593113598332-cd288d649433?q=80&w=1200", t: "Transparency & Trust", d: "Every analysis contributes to our social health mission"},
            {i: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1200", t: "Global Research Data", d: "Analyzing clinical cases across 10,000+ databases"},
            {i: "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1200", t: "Community Outreach", d: "Bringing medical kits to remote rural areas"},
            {i: "https://images.unsplash.com/photo-1518152006812-edab29b069ac?q=80&w=1200", t: "Secure Digital Lab", d: "Encrypted and private environment for clinical data"},
            {i: "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?q=80&w=1200", t: "United For Humanity", d: "Bridging the gap between Technology and Charity"}
        ];
        let c = 0;
        setInterval(() => {
            c = (c + 1) % s.length;
            const img = document.getElementById('v');
            img.style.opacity = 0.5;
            setTimeout(() => {
                img.src = s[c].i;
                document.getElementById('t').innerText = s[c].t;
                document.getElementById('d').innerText = s[c].d;
                img.style.opacity = 1;
            }, 600);
        }, 5000);
    </script>
    """
    components.html(slider_html, height=400)

# --- 4. DATA & MAILING TOOLS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Database Offline: {e}")

def send_security_mail(receiver, otp):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart(); msg['From'] = f"PROF. NIDAN Support <{sender}>"; msg['To'] = receiver; msg['Subject'] = f"Verification Code: {otp}"
        msg.attach(MIMEText(f"Your clinical access verification code is: {otp}\nDo not share this code.", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False
        
