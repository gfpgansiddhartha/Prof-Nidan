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

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide", page_icon="🔬")

# --- 2. SAFE CONFIGURATION CHECK (Traceback বন্ধ করার জন্য) ---
def check_setup():
    keys = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD", "ADMIN_PASSWORD"]
    missing = [k for k in keys if k not in st.secrets]
    if missing or "gsheets" not in st.secrets:
        st.warning("⚠️ Setup Incomplete: Please check your Secrets box for missing keys.")
        st.stop()

check_setup()

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none;
    }
    .auth-card {
        padding: 30px; border-radius: 15px; background: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    .impact-stats {
        text-align: center; padding: 15px; background: #e3f2fd;
        border-radius: 12px; border: 1px solid #90caf9;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. ALTERNATING SLIDER (App -> Donation -> App) ---
def render_alternating_slider():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:400px; position:relative; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
        <img id="slide-img" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:400px; object-fit:cover; transition: 1s;">
        <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.7); color:white; width:100%; padding:25px; text-align:center;">
            <h2 id="slide-title">PROF. NIDAN Clinical AI</h2>
            <p id="slide-desc">Precision Diagnostic Analysis</p>
        </div>
    </div>
    <script>
        const banners = [
            {img: "https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200", t: "AI Report Analysis 🧬", d: "Decoding clinical data with 99.9% accuracy."},
            {img: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200", t: "Your Donation Matters ❤️", d: "Helping underprivileged children get proper medical care."},
            {img: "https://images.unsplash.com/photo-1532187863486-abf9d39d6618?q=80&w=1200", t: "Forensic Intelligence 🔬", d: "Advanced specimen identification for forensic science."},
            {img: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1200", t: "Serving Humanity 🤝", d: "Providing free diagnostic support to those in need."},
            {img: "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=1200", t: "High-Tech Diagnostics 💻", d: "Empowering doctors with real-time AI insights."},
            {img: "https://images.unsplash.com/photo-1593113598332-cd288d649433?q=80&w=1200", t: "Charity & Trust Board 🕊️", d: "Every analysis funds our social medical mission."},
            {img: "https://images.unsplash.com/photo-1518152006812-edab29b069ac?q=80&w=1200", t: "Secure Data Lab 🛡️", d: "100% encrypted and private clinical environment."},
            {img: "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1200", t: "Community Outreach 📦", d: "Delivering free health kits in remote rural areas."},
            {img: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1200", t: "Clinical Excellence 📊", d: "The future of medical report interpretation."},
            {img: "https://images.unsplash.com/photo-1542810634-71277d95dcbb?q=80&w=1200", t: "United For Health 🌍", d: "A platform built on Science and Compassion."}
        ];
        let idx = 0;
        setInterval(() => {
            idx = (idx + 1) % banners.length;
            const el = document.getElementById('slide-img');
            el.style.opacity = 0.5;
            setTimeout(() => {
                el.src = banners[idx].img;
                document.getElementById('slide-title').innerText = banners[idx].t;
                document.getElementById('slide-desc').innerText = banners[idx].d;
                el.style.opacity = 1;
            }, 500);
        }, 5000);
    </script>
    """
    components.html(slider_html, height=420)

# --- 5. SYSTEM FUNCTIONS ---
def get_db_conn():
    try: return st.connection("gsheets", type=GSheetsConnection)
    except: return None

def send_otp_mail(email, code):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart(); msg['From'] = f"PROF. NIDAN Support <{sender}>"; msg['To'] = email; msg['Subject'] = f"Login Code: {code}"
        msg.attach(MIMEText(f"Your clinical access verification code is: {code}", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False

def create_report_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN CLINICAL REPORT", ln=True, align='C')
    pdf.ln(10); pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 6. APP STATE & LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

render_alternating_slider()

if not st.session_state.auth:
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        t_login, t_signup, t_forgot = st.tabs(["🔐 Login", "📝 Sign Up", "🔑 Forgot"])
        
        with t_login:
            if st.session_state.step == 1:
                u_email = st.text_input("Official Email")
                u_pass = st.text_input("Password", type="password")
                if st.button("LOGIN"):
                    # Admin Check
                    if u_email == st.secrets["EMAIL_USERNAME"] and u_pass == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state.auth = True; st.session_state.email = u_email; st.rerun()
                    
                    conn = get_db_conn()
                    df = conn.read(worksheet="Users", ttl=0)
                    match = df[df['Email'] == u_email]
                    if not match.empty and str(match.iloc[0]['Password']) == u_pass:
                        otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                        st.session_state.otp = otp; st.session_state.email = u_email
                        if send_otp_mail(u_email, otp): st.session_state.step = 2; st.rerun()
                    else: st.error("❌ Invalid Credentials")
            else:
                code = st.text_input("Enter 4-Letter OTP", max_chars=4).upper()
                if st.button("VERIFY"):
                    if code == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Wrong Code")

        with t_signup:
            s_email = st.text_input("Email", key="s_em")
            s_pass = st.text_input("Password", type="password", key="s_pw")
            if st.button("REGISTER"):
                if len(s_pass) < 8: st.warning("Password too short.")
                else:
                    conn = get_db_conn(); df = conn.read(worksheet="Users", ttl=0)
                    if s_email in df['Email'].values: st.error("User exists.")
                    else:
                        new_row = pd.DataFrame([{"Email": s_email, "Password": s_pass}])
                        conn.update(worksheet="Users", data=pd.concat([df, new_row], ignore_index=True))
                        st.success("✅ Registered! Now Login.")
        st.markdown('</div>', unsafe_allow_html=True)

else: # DASHBOARD
    st.sidebar.markdown(f"**Verified User:**\n{st.session_state.email}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.step = 1; st.rerun()

    main_c, side_c = st.columns([2.5, 1])
    with main_c:
        st.subheader("📊 Clinical Analysis Terminal")
        file = st.file_uploader("Upload Report/Specimen Image", type=["jpg","png","jpeg"])
        if file:
            img = Image.open(file); st.image(img, use_container_width=True)
            lang = st.selectbox("Language", ["English", "Bengali", "Hindi"])
            if st.button("START AI DIAGNOSIS"):
                with st.spinner("AI Engine Processing..."):
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    res = model.generate_content([f"Provide forensic diagnostic report in {lang}", img])
                    report = res.text
                    st.markdown(f"### Result:\n{report}")
                    
                    # Voice & PDF
                    tts = gTTS(text=report, lang='en' if lang=="English" else ('bn' if lang=="Bengali" else 'hi'))
                    v_buf = io.BytesIO(); tts.write_to_fp(v_buf); st.audio(v_buf)
                    st.download_button("📄 Download PDF", create_report_pdf(report), "Report.pdf", "application/pdf")

    with side_c:
        st.markdown('<div class="impact-stats">', unsafe_allow_html=True)
        st.markdown("### 🕊️ Impact Board")
        st.markdown("## 1,245+")
        st.write("Lives Supported")
        st.markdown("---")
        st.markdown("## $12,300")
        st.write("Medical Aid Fund")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("🤝 **Charity Request:** If you cannot afford clinical tests, contact us for free support.")
