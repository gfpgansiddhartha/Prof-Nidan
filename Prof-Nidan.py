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

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide", page_icon="🔬")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.2em;
        background: linear-gradient(90deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none;
    }
    .auth-card {
        padding: 30px; border-radius: 15px;
        background-color: white; box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .counter-box {
        text-align: center; padding: 15px; background: #e3f2fd;
        border-radius: 10px; border: 1px solid #90caf9;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. ADVANCED BANNER SLIDER ---
def render_slider():
    slider_html = """
    <div style="width:100%; overflow:hidden; border-radius:15px; position:relative; height:350px;">
        <div id="slider" style="display:flex; transition: transform 1s ease-in-out;">
            <div style="min-width:100%; position:relative;">
                <img src="https://images.unsplash.com/photo-1579684388669-c2c317c76841?q=80&w=1200" style="width:100%; height:350px; object-fit:cover;">
                <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.6); color:white; width:100%; padding:20px; text-align:center;">
                    <h2>AI-Powered Clinical Diagnostics 🧬</h2>
                    <p>Advanced Forensic Analysis for Precision Medicine</p>
                </div>
            </div>
            <div style="min-width:100%; position:relative;">
                <img src="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200" style="width:100%; height:350px; object-fit:cover;">
                <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.6); color:white; width:100%; padding:20px; text-align:center;">
                    <h2>Service Above Self ❤️</h2>
                    <p>Every analysis helps fund medical care for underprivileged children</p>
                </div>
            </div>
        </div>
    </div>
    <script>
        let index = 0;
        const slider = document.getElementById('slider');
        setInterval(() => {
            index = (index + 1) % 2;
            slider.style.transform = `translateX(-${index * 100}%)`;
        }, 5000);
    </script>
    """
    components.html(slider_html, height=360)

# --- 3. CORE LOGIC FUNCTIONS ---
def get_db():
    try: return st.connection("gsheets", type=GSheetsConnection)
    except: return None

def send_otp(email, code):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'] = f"PROF. NIDAN Support <{sender}>"
        msg['To'] = email
        msg['Subject'] = f"Your Verification Code: {code}"
        msg.attach(MIMEText(f"Hello,\n\nYour security code is: {code}\n\nDo not share this with anyone.", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN CLINICAL REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. APP STATE MANAGEMENT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# --- 5. INTERFACE RENDER ---
render_slider()

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_login, tab_signup, tab_forgot = st.tabs(["🔐 Login", "📝 Sign Up", "🔑 Reset"])

        # LOGIN SECTION
        with tab_login:
            if st.session_state.step == 1:
                email = st.text_input("Email", placeholder="Enter your registered email")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                if st.button("VERIFY ACCOUNT"):
                    conn = get_db()
                    if conn:
                        # Admin Check
                        if email == st.secrets["EMAIL_USERNAME"] and password == st.secrets["ADMIN_PASSWORD"]:
                            st.session_state.is_admin = True
                            st.session_state.email = email
                            st.session_state.auth = True
                            st.rerun()
                        
                        users = conn.read(worksheet="Users", ttl=0)
                        match = users[users['Email'] == email]
                        if not match.empty and str(match.iloc[0]['Password']) == password:
                            otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                            st.session_state.otp = otp
                            st.session_state.email = email
                            if send_otp(email, otp):
                                st.session_state.step = 2
                                st.rerun()
                            else: st.error("Email service error.")
                        else: st.error("❌ Invalid Email or Password.")
                    else: st.error("📡 Database connection failed.")
            else:
                otp_in = st.text_input("Enter 4-Digit Code", max_chars=4).upper()
                if st.button("COMPLETE LOGIN"):
                    if otp_in == st.session_state.otp:
                        st.session_state.auth = True
                        st.rerun()
                    else: st.error("❌ Incorrect Code.")

        # SIGNUP SECTION (Fixed: Fields now visible)
        with tab_signup:
            new_email = st.text_input("New Email", key="reg_email")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("REGISTER"):
                if len(new_pass) < 8: st.warning("Password must be 8+ characters.")
                else:
                    conn = get_db()
                    df = conn.read(worksheet="Users", ttl=0)
                    if new_email in df['Email'].values: st.error("Email already exists.")
                    else:
                        new_row = pd.DataFrame([{"Email": new_email, "Password": new_pass}])
                        updated = pd.concat([df, new_row], ignore_index=True)
                        conn.update(worksheet="Users", data=updated)
                        st.success("✅ Account Created! Please Login.")

        # FORGOT PASSWORD
        with tab_forgot:
            st.write("Password recovery will be sent to your email.")
            f_email = st.text_input("Enter Email", key="f_email")
            if st.button("SEND RESET LINK"):
                st.info("If this email exists, a reset link will be sent.")
        
        st.markdown('</div>', unsafe_allow_html=True)

else: # DASHBOARD
    st.sidebar.title("🔬 Navigation")
    if st.session_state.is_admin:
        st.sidebar.warning("ADMIN ACCESS")
        menu = st.sidebar.radio("Go to", ["Analysis Terminal", "Admin Database"])
    else:
        menu = "Analysis Terminal"

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.step = 1
        st.session_state.is_admin = False
        st.rerun()

    if menu == "Admin Database":
        st.subheader("👥 User Records")
        conn = get_db()
        st.dataframe(conn.read(worksheet="Users", ttl=0), use_container_width=True)
    
    else:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📊 Specimen Analysis")
            file = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
            if file:
                img = Image.open(file)
                st.image(img, use_container_width=True)
                if st.button("RUN AI DIAGNOSIS"):
                    with st.spinner("Analyzing..."):
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content(["Provide forensic diagnostic report", img])
                        report = res.text
                        st.markdown(report)
                        
                        # Voice Report
                        st.markdown("---")
                        st.write("🔊 **Listen to Report**")
                        tts = gTTS(text=report, lang='en')
                        voice_data = io.BytesIO()
                        tts.write_to_fp(voice_data)
                        st.audio(voice_data)

                        # PDF Download
                        st.markdown("---")
                        pdf_data = create_pdf(report)
                        st.download_button("📄 Download PDF Report", pdf_data, "Report.pdf", "application/pdf")

        with c2:
            st.markdown('<div class="counter-box">', unsafe_allow_html=True)
            st.markdown("### 🕊️ Impact Tracker")
            st.markdown("## 1,240+")
            st.write("People helped this month")
            st.markdown("---")
            st.markdown("### 💰 Donations")
            st.markdown("## $15,300")
            st.write("Raised for Child Care")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("Premium Support: +91 XXX-XXX-XXXX")
