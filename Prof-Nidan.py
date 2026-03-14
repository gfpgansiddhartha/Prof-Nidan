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

# --- 3. DYNAMIC BANNER SLIDER (10 Alternate Slides) ---
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
            {i: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1200", t: "Charity & Trust 🕊", d: "Providing free healthcare support to those in need"},
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

# --- 4. CORE ENGINE & UTILITIES ---
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

def create_report_pdf(content):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN CLINICAL ANALYSIS REPORT", ln=True, align='C')
    pdf.ln(10); pdf.multi_cell(0, 10, txt=content.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 5. SESSION MANAGEMENT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

render_nidan_banner()

# --- 6. AUTHENTICATION ---
if not st.session_state.auth:
    l, c, r = st.columns([1, 1.8, 1])
    with c:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Register"])
        
        with t_log:
            if st.session_state.step == 1:
                em = st.text_input("Email", key="l_em")
                pw = st.text_input("Password", type="password", key="l_pw")
                if st.button("VERIFY IDENTITY"):
                    if em == st.secrets["EMAIL_USERNAME"] and pw == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state.auth = True; st.session_state.email = em; st.rerun()
                    try:
                        df = conn.read(worksheet="Users", ttl=0)
                        match = df[df['Email'] == em]
                        if not match.empty and str(match.iloc[0]['Password']) == pw:
                            otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                            st.session_state.otp = otp; st.session_state.email = em
                            if send_security_mail(em, otp): st.session_state.step = 2; st.rerun()
                            else: st.error("Email service busy.")
                        else: st.error("❌ Invalid Credentials.")
                    except: st.error("📡 Database connection failed.")
            else:
                code = st.text_input("Enter 4-Letter Code", max_chars=4).upper()
                if st.button("CONFIRM LOGIN"):
                    if code == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Incorrect Code.")

        with t_reg:
            rem = st.text_input("New Email", key="r_em")
            rpw = st.text_input("Create Password", type="password", key="r_pw")
            if st.button("CREATE ACCOUNT"):
                if len(rpw) < 8: st.warning("Password must be 8+ characters.")
                else:
                    try:
                        df = conn.read(worksheet="Users", ttl=0)
                        if rem in df['Email'].values: st.error("Email already exists.")
                        else:
                            new_row = pd.DataFrame([{"Email": rem, "Password": rpw}])
                            conn.update(worksheet="Users", data=pd.concat([df, new_row], ignore_index=True))
                            st.success("✅ Account Created! Please Login.")
                    except: st.error("📡 Database busy.")
        st.markdown('</div>', unsafe_allow_html=True)

else: # --- MAIN DASHBOARD ---
    st.sidebar.markdown(f"Verified User:\n{st.session_state.email}")
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.session_state.step = 1; st.rerun()

    main, side = st.columns([2.5, 1])
    
    with main:
        st.subheader("📋 Clinical Analysis Terminal")
        file = st.file_uploader("Upload Medical Specimen/Report", type=["jpg","png","jpeg"])
        if file:
            img = Image.open(file); st.image(img, use_container_width=True)
            lang = st.selectbox("Preferred Language", ["English", "Bengali", "Hindi"])
            if st.button("EXECUTE AI ANALYSIS"):
                with st.spinner("AI analyzing..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content([f"Provide forensic medical summary in {lang}", img])
                        report = res.text
                        st.markdown(f"### Diagnostic Summary:\n{report}")
                        
                        # Audio & PDF Exports
                        tts = gTTS(text=report, lang='en' if lang=="English" else ('bn' if lang=="Bengali" else 'hi'))
                        v_io = io.BytesIO(); tts.write_to_fp(v_io); st.audio(v_io)
                        st.download_button("📄 Download PDF Report", create_report_pdf(report), "Diagnostic_Report.pdf", "application/pdf")
                    except: st.error("🤖 Engine Timeout. Please try again.")

    with side:
        # --- DYNAMIC IMPACT COUNTER ---
        st.markdown('<div class="impact-stats">', unsafe_allow_html=True)
        st.markdown("### 🕊 Social Impact")
        try:
            charity_df = conn.read(worksheet="Charity", ttl=0)
            if not charity_df.empty and 'Type' in charity_df.columns:
                p_val = charity_df[charity_df['Type'] == 'Patients']['Value'].values[0]
                f_val = charity_df[charity_df['Type'] == 'Fund']['Value'].values[0]
                st.metric("Lives Impacted", f"{p_val}+")
                st.metric("Charity Fund", f"${f_val}")
            else:
                st.metric("Lives Impacted", "1,200+")
                st.metric("Charity Fund", "$10,000")
        except:
            st.metric("Lives Impacted", "1,200+")
            st.metric("Charity Fund", "$10,000")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.warning("🤝 Request Assistance")
        st.write("Need free clinical aid? Log a request below.")
        req = st.text_area("Describe your case...")
        if st.button("Submit Ticket"):
            if req:
                try:
                    t_df = conn.read(worksheet="Tickets", ttl=0)
                    new_t = pd.DataFrame([{"Email": st.session_state.email, "Request": req, "Status": "Pending"}])
                    conn.update(worksheet="Tickets", data=pd.concat([t_df, new_t], ignore_index=True))
                    st.success("Ticket submitted successfully.")
                except: st.error("📡 Database busy.")
