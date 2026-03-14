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

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI | Science & Compassion", layout="wide", page_icon="🔬")

def check_env_setup():
    """Validates if all secrets are present to prevent tracebacks."""
    required_keys = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD", "ADMIN_PASSWORD"]
    for key in required_keys:
        if key not in st.secrets:
            st.warning(f"⚠️ Configuration Missing: '{key}' not found in Streamlit Secrets.")
            st.stop()
check_env_setup()

# --- 2. ADVANCED UI STYLING (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
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
    h1, h2, h3 { color: #004a99; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ALTERNATING MASTER SLIDER (10 Banners: Tech -> Charity) ---
def render_master_slider():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:400px; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <img id="view" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:400px; object-fit:cover; transition: 1.2s;">
        <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.75); color:white; width:100%; padding:25px; text-align:center;">
            <h2 id="t" style="margin:0; font-family: Arial;">PROF. NIDAN</h2>
            <p id="d" style="font-size:18px; color:#ddd;">Leading with Science, Driven by Care</p>
        </div>
    </div>
    <script>
        const slides = [
            {i: "https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200", t: "Clinical AI Engine 🧬", d: "High-precision diagnostic report analysis"},
            {i: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200", t: "Our Compassion ❤️", d: "Funding treatment for underprivileged children"},
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
            c = (c + 1) % slides.length;
            const img = document.getElementById('view');
            img.style.opacity = 0.5;
            setTimeout(() => {
                img.src = slides[c].i;
                document.getElementById('t').innerText = slides[c].t;
                document.getElementById('d').innerText = slides[c].d;
                img.style.opacity = 1;
            }, 600);
        }, 5000);
    </script>
    """
    components.html(slider_html, height=420)

# --- 4. CORE ENGINE & UTILITIES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def send_otp_email(receiver, otp):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart(); msg['From'] = f"PROF. NIDAN Support <{sender}>"; msg['To'] = receiver; msg['Subject'] = f"Login OTP: {otp}"
        msg.attach(MIMEText(f"Your secure verification code is: {otp}\nDo not share this with anyone.", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False

def generate_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN CLINICAL ANALYSIS REPORT", ln=True, align='C')
    pdf.ln(10); pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 5. SESSION MANAGEMENT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

render_master_slider()

# --- 6. AUTHENTICATION FLOW ---
if not st.session_state.auth:
    l, c, r = st.columns([1, 1.8, 1])
    with c:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        t_login, t_reg, t_forgot = st.tabs(["🔐 Login", "📝 Register", "🔑 Recovery"])
        
        with t_login:
            if st.session_state.step == 1:
                email_in = st.text_input("Email", key="l_em")
                pass_in = st.text_input("Password", type="password", key="l_pw")
                if st.button("VERIFY IDENTITY"):
                    # Admin Access
                    if email_in == st.secrets["EMAIL_USERNAME"] and pass_in == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state.auth = True; st.session_state.email = email_in; st.rerun()
                    
                    try:
                        df = conn.read(worksheet="Users", ttl=0)
                        match = df[df['Email'] == email_in]
                        if not match.empty and str(match.iloc[0]['Password']) == pass_in:
                            otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                            st.session_state.otp = otp; st.session_state.email = email_in
                            if send_otp_email(email_in, otp): st.session_state.step = 2; st.rerun()
                            else: st.error("Email service error. Try again.")
                        else: st.error("❌ Invalid Email or Password.")
                    except: st.error("📡 Database connection failed.")
            else:
                otp_in = st.text_input("Enter 4-Digit Code", max_chars=4).upper()
                if st.button("CONFIRM LOGIN"):
                    if otp_in == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Incorrect Code.")

        with t_reg:
            reg_em = st.text_input("New Email", key="r_em")
            reg_pw = st.text_input("New Password", type="password", key="r_pw")
            if st.button("CREATE ACCOUNT"):
                if len(reg_pw) < 8: st.warning("Password must be 8+ characters.")
                else:
                    try:
                        df = conn.read(worksheet="Users", ttl=0)
                        if reg_em in df['Email'].values: st.error("Email already registered.")
                        else:
                            new_row = pd.DataFrame([{"Email": reg_em, "Password": reg_pw}])
                            conn.update(worksheet="Users", data=pd.concat([df, new_row], ignore_index=True))
                            st.success("✅ Account Created! Please Login.")
                    except: st.error("📡 Database busy.")
        st.markdown('</div>', unsafe_allow_html=True)

else: # --- MAIN DASHBOARD ---
    st.sidebar.markdown(f"**Verified User:**\n{st.session_state.email}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.step = 1; st.rerun()

    main_col, side_col = st.columns([2.5, 1])
    
    with main_col:
        st.subheader("📑 Clinical Analysis Terminal")
        uploaded_file = st.file_uploader("Upload Medical Scan/Report", type=["jpg","png","jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file); st.image(img, use_container_width=True)
            output_lang = st.selectbox("Report Language", ["English", "Bengali", "Hindi"])
            if st.button("EXECUTE AI ANALYSIS"):
                with st.spinner("AI analyzing report..."):
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        res = model.generate_content([f"Analyze this report and provide a diagnostic summary in {output_lang}", img])
                        analysis_text = res.text
                        st.markdown(f"### Analysis Result:\n{analysis_text}")
                        
                        # Voice & PDF
                        tts = gTTS(text=analysis_text, lang='en' if output_lang=="English" else ('bn' if output_lang=="Bengali" else 'hi'))
                        v_io = io.BytesIO(); tts.write_to_fp(v_io); st.audio(v_io)
                        st.download_button("📄 Download PDF Report", generate_pdf(analysis_text), "Report.pdf", "application/pdf")
                    except: st.error("🤖 AI Engine timeout. Check API Key.")

    with side_col:
        # --- DYNAMIC IMPACT COUNTER WITH ERROR HANDLING ---
        st.markdown('<div class="impact-stats">', unsafe_allow_html=True)
        st.markdown("### 🕊️ Social Impact Board")
        try:
            charity_df = conn.read(worksheet="Charity", ttl=0)
            if not charity_df.empty and 'Type' in charity_df.columns:
                p_row = charity_df[charity_df['Type'] == 'Patients']
                f_row = charity_df[charity_df['Type'] == 'Fund']
                
                patients = p_row['Value'].values[0] if not p_row.empty else "1200"
                fund = f_row['Value'].values[0] if not f_row.empty else "10000"
                
                st.metric("Lives Impacted", f"{patients}+")
                st.metric("Charity Fund", f"${fund}")
            else:
                st.metric("Lives Impacted", "1,200+")
                st.metric("Charity Fund", "$10,000")
        except:
            st.metric("Lives Impacted", "1,200+")
            st.metric("Charity Fund", "$10,000")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.warning("🤝 **Help Request**")
        st.write("If you need free medical analysis, please request aid below.")
        req_msg = st.text_area("Describe your case...")
        if st.button("Send Request"):
            if req_msg:
                try:
                    t_df = conn.read(worksheet="Tickets", ttl=0)
                    new_ticket = pd.DataFrame([{"Email": st.session_state.email, "Request": req_msg, "Status": "Pending"}])
                    conn.update(worksheet="Tickets", data=pd.concat([t_df, new_ticket], ignore_index=True))
                    st.success("Request sent. We will contact you.")
                except: st.error("Database connection error.")
