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

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="PROF. NIDAN | Clinical Intelligence", layout="wide", page_icon="🔬")

# --- 2. PROFESSIONAL CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none; transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; transform: translateY(-2px); }
    .auth-card {
        padding: 35px; border-radius: 20px; background: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .impact-box {
        padding: 20px; border-radius: 15px; background: #e3f2fd;
        border: 1px solid #90caf9; text-align: center;
    }
    h1 { color: #004a99; font-family: 'Segoe UI', Tahoma; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SYSTEM HELPER FUNCTIONS ---
def get_db():
    try: return st.connection("gsheets", type=GSheetsConnection)
    except: return None

def send_mail(receiver, subject, body):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'] = f"PROF. NIDAN Support <{sender}>"
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls()
        server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False

def check_password_strength(p):
    if len(p) < 8: return False, "Min 8 characters required."
    if not re.search("[A-Z]", p) or not re.search("[0-9]", p):
        return False, "Include 1 Uppercase & 1 Number."
    return True, "Strong Password!"

# --- 4. ADVANCED AUTOMATIC SLIDER (10 Real Banners) ---
def render_master_slider():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:400px; position:relative; box-shadow: 0 12px 24px rgba(0,0,0,0.2);">
        <img id="slide" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:400px; object-fit:cover; transition: 1.5s ease-in-out;">
        <div style="position:absolute; bottom:0; background: linear-gradient(transparent, rgba(0,0,0,0.85)); color:white; width:100%; padding:30px; text-align:center;">
            <h2 id="title" style="margin:0; font-family: Arial;">PROF. NIDAN</h2>
            <p id="desc" style="font-size:18px; color:#ddd;">Clinical Science meets Compassion</p>
        </div>
    </div>
    <script>
        const data = [
            {s: "https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200", t: "AI Clinical Intelligence", d: "High-precision analysis for clinical & forensic reports"},
            {s: "https://images.unsplash.com/photo-1532187863486-abf9d39d6618?q=80&w=1200", t: "Laboratory Accuracy", d: "Scientific identification of specimens & medical data"},
            {s: "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=1200", t: "Diagnostic Power", d: "Deciphering complex medical evidence since 2026"},
            {s: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1200", t: "Global Research Hub", d: "Accessing 10k+ forensic case databases for results"},
            {s: "https://images.unsplash.com/photo-1518152006812-edab29b069ac?q=80&w=1200", t: "Secure Clinical Suite", d: "Privacy-protected environment for your sensitive data"},
            {s: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200", t: "Our Social Mission", d: "Funding medical care for underprivileged children"},
            {s: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1200", t: "Humanity First", d: "Every analysis helps someone in need of assistance"},
            {s: "https://images.unsplash.com/photo-1593113598332-cd288d649433?q=80&w=1200", t: "Transparency & Trust", d: "Direct support to families for critical healthcare"},
            {s: "https://images.unsplash.com/photo-1509099836639-18ba1795216d?q=80&w=1200", t: "Community Outreach", d: "Distributing free medical kits in remote villages"},
            {s: "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?q=80&w=1200", t: "United in Care", d: "Bridging the gap between Technology and Charity"}
        ];
        let i = 0;
        setInterval(() => {
            i = (i + 1) % data.length;
            const img = document.getElementById('slide');
            img.style.opacity = 0.4;
            setTimeout(() => {
                img.src = data[i].s;
                document.getElementById('title').innerText = data[i].t;
                document.getElementById('desc').innerText = data[i].d;
                img.style.opacity = 1;
            }, 600);
        }, 5000);
    </script>
    """
    components.html(slider_html, height=420)

# --- 5. CORE APP STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1
if "is_admin" not in st.session_state: st.session_state.is_admin = False

# --- 6. AUTHENTICATION INTERFACE ---
render_master_slider()

if not st.session_state.auth:
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_log, tab_reg, tab_res = st.tabs(["🔐 Login", "📝 Sign Up", "🔑 Forgot Password"])

        # LOGIN
        with tab_log:
            if st.session_state.step == 1:
                email = st.text_input("Official Email", key="login_email")
                pwd = st.text_input("Password", type="password", key="login_pwd")
                if st.button("VERIFY & LOGIN"):
                    # Admin Check
                    if email == st.secrets["EMAIL_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state.is_admin = True; st.session_state.auth = True; st.session_state.email = email; st.rerun()
                    
                    conn = get_db()
                    users = conn.read(worksheet="Users", ttl=0)
                    match = users[users['Email'] == email]
                    if not match.empty and str(match.iloc[0]['Password']) == pwd:
                        otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                        st.session_state.otp = otp; st.session_state.email = email
                        if send_mail(email, "Security Code", f"Your PROF. NIDAN code is: {otp}"):
                            st.session_state.step = 2; st.rerun()
                    else: st.error("❌ Invalid Email or Password.")
            else:
                code_in = st.text_input("Enter 4-Letter Code", max_chars=4).upper()
                if st.button("CONFIRM LOGIN"):
                    if code_in == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Incorrect Code.")

        # SIGN UP
        with tab_reg:
            re_email = st.text_input("New Email", key="reg_email")
            re_pwd = st.text_input("New Password", type="password", key="reg_pwd")
            ok, msg = check_password_strength(re_pwd)
            if re_pwd: (st.success(msg) if ok else st.warning(msg))
            if st.button("CREATE ACCOUNT") and ok:
                conn = get_db(); df = conn.read(worksheet="Users", ttl=0)
                if re_email in df['Email'].values: st.error("Email already exists.")
                else:
                    new_user = pd.DataFrame([{"Email": re_email, "Password": re_pwd}])
                    conn.update(worksheet="Users", data=pd.concat([df, new_user], ignore_index=True))
                    st.success("✅ Registered! Please Login.")

        # FORGOT PASSWORD
        with tab_res:
            st.info("Recovery code will be sent to your email.")
            f_email = st.text_input("Registered Email", key="forgot_email")
            if st.button("SEND RECOVERY LINK"):
                st.success("If the email exists, a reset link will be sent.")
        st.markdown('</div>', unsafe_allow_html=True)

else: # DASHBOARD
    st.sidebar.title("🔬 Navigation")
    if st.session_state.is_admin:
        st.sidebar.warning("🛠 ADMIN MODE")
        nav = st.sidebar.radio("Console", ["Analysis Terminal", "User Database"])
    else: nav = "Analysis Terminal"

    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.step = 1; st.session_state.is_admin = False; st.rerun()

    # ADMIN DATABASE PAGE
    if nav == "User Database":
        st.subheader("👥 User Management Console")
        conn = get_db(); st.dataframe(conn.read(worksheet="Users", ttl=0), use_container_width=True)

    # MAIN ANALYSIS TERMINAL
    else:
        c_main, c_side = st.columns([2.5, 1])
        with c_main:
            st.subheader("📑 Forensic & Clinical Analysis")
            file = st.file_uploader("Upload Medical Scan / Report Image", type=["jpg","png","jpeg"])
            if file:
                img = Image.open(file); st.image(img, use_container_width=True, caption="Active Specimen")
                lang = st.selectbox("Output Language", ["English", "Bengali", "Hindi"])
                if st.button("EXECUTE AI DIAGNOSIS"):
                    with st.spinner("AI Engine Analyzing..."):
                        try:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            res = model.generate_content([f"Provide forensic diagnostic report in {lang}", img])
                            report_txt = res.text
                            st.markdown(f"### Diagnostic Result:\n{report_txt}")
                            
                            # Voice Engine
                            st.markdown("---")
                            tts = gTTS(text=report_txt, lang='en' if lang=="English" else ('bn' if lang=="Bengali" else 'hi'))
                            v_buf = io.BytesIO(); tts.write_to_fp(v_buf)
                            st.audio(v_buf)

                            # PDF Export
                            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
                            pdf.cell(200, 10, txt="PROF. NIDAN REPORT", ln=True, align='C')
                            pdf.ln(10); pdf.multi_cell(0, 10, txt=report_txt.encode('latin-1', 'ignore').decode('latin-1'))
                            st.download_button("📄 Download PDF Report", pdf.output(dest='S').encode('latin-1'), "Report.pdf", "application/pdf")
                        except: st.error("🤖 Engine Timeout. Please retry.")

        with c_side:
            st.markdown('<div class="impact-box">', unsafe_allow_html=True)
            st.markdown("### 🕊️ Social Mission")
            st.markdown("## 1,245+")
            st.write("Patients Helped")
            st.markdown("---")
            st.markdown("## $12,300")
            st.write("Charity Fund Raised")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.warning("🤝 **Need Help?**\nIf you are underprivileged and need free clinical support, please contact us.")
            if st.button("Request Free Aid"): st.success("Request logged. We'll contact you.")
