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
st.set_page_config(page_title="PROF. NIDAN AI", layout="wide", page_icon="⚖️")

def check_env():
    # সিক্রেটস চেক করার লজিক (Traceback রোধে)
    keys = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD", "ADMIN_PASSWORD"]
    for k in keys:
        if k not in st.secrets:
            st.warning(f"⚠️ Configuration Missing: {k} in Secrets.")
            st.stop()
check_env()

# --- 2. ADVANCED CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #004a99 0%, #007bff 100%);
        color: white; font-weight: bold; border: none;
    }
    .auth-card { padding: 30px; border-radius: 20px; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .impact-stats { text-align: center; padding: 20px; border-radius: 15px; background: white; border-top: 5px solid #004a99; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC ALTERNATING SLIDER (Scientific + Compassionate) ---
def render_master_slider():
    slider_html = """
    <div style="width:100%; border-radius:20px; overflow:hidden; height:400px; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <img id="view" src="https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200" style="width:100%; height:400px; object-fit:cover; transition: 1.2s;">
        <div style="position:absolute; bottom:0; background:rgba(0,0,0,0.7); color:white; width:100%; padding:25px; text-align:center;">
            <h2 id="t">PROF. NIDAN</h2><p id="d">Leading with Science, Driven by Care</p>
        </div>
    </div>
    <script>
        const slides = [
            {i: "https://images.unsplash.com/photo-1579154235602-3c2c249bc918?q=80&w=1200", t: "Clinical AI Engine 🧬", d: "Deep Analysis of Clinical Specimen Data"},
            {i: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200", t: "Our Compassion ❤️", d: "Funding treatment for children in need"},
            {i: "https://images.unsplash.com/photo-1532187863486-abf9d39d6618?q=80&w=1200", t: "Forensic Intelligence 🔬", d: "Precision Identification of Medical Evidence"},
            {i: "https://images.unsplash.com/photo-1532629345422-7515f3d16bb6?q=80&w=1200", t: "Charity Board 🕊️", d: "Empowering Underprivileged Communities"},
            {i: "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=1200", t: "Advanced Diagnostics 💻", d: "Real-time AI Clinical Interpretation"}
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
            }, 500);
        }, 5000);
    </script>
    """
    components.html(slider_html, height=420)

# --- 4. CORE ENGINE & TOOLS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def send_security_mail(email, otp):
    try:
        msg = MIMEMultipart(); msg['From'] = st.secrets["EMAIL_USERNAME"]; msg['To'] = email; msg['Subject'] = f"Access Code: {otp}"
        msg.attach(MIMEText(f"Your secure login code for PROF. NIDAN is: {otp}", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls()
        server.login(st.secrets["EMAIL_USERNAME"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg); server.quit()
        return True
    except: return False

def create_pdf_report(content):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="PROF. NIDAN CLINICAL ANALYSIS", ln=True, align='C')
    pdf.ln(10); pdf.multi_cell(0, 10, txt=content.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 5. APP STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

render_master_slider()

if not st.session_state.auth:
    l_col, c_col, r_col = st.columns([1, 1.8, 1])
    with c_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_l, tab_s, tab_f = st.tabs(["🔐 Login", "📝 Register", "🔑 Recovery"])
        
        with tab_l:
            if st.session_state.step == 1:
                em = st.text_input("Email", key="login_em")
                pw = st.text_input("Password", type="password", key="login_pw")
                if st.button("VERIFY IDENTITY"):
                    # Admin Bypass
                    if em == st.secrets["EMAIL_USERNAME"] and pw == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state.auth = True; st.session_state.email = em; st.rerun()
                    
                    df = conn.read(worksheet="Users", ttl=0)
                    match = df[df['Email'] == em]
                    if not match.empty and str(match.iloc[0]['Password']) == pw:
                        otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                        st.session_state.otp = otp; st.session_state.email = em
                        if send_security_mail(em, otp): st.session_state.step = 2; st.rerun()
                    else: st.error("❌ Credentials Not Found.")
            else:
                code = st.text_input("Enter 4-Letter Code", max_chars=4).upper()
                if st.button("CONFIRM ACCESS"):
                    if code == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Invalid Code.")

        with tab_s:
            nem = st.text_input("New Email", key="reg_em")
            npw = st.text_input("Create Password", type="password", key="reg_pw")
            if st.button("START JOURNEY"):
                if len(npw) < 8: st.warning("Security: Use 8+ characters.")
                else:
                    df = conn.read(worksheet="Users", ttl=0)
                    if nem in df['Email'].values: st.error("Already registered.")
                    else:
                        new_data = pd.DataFrame([{"Email": nem, "Password": npw}])
                        conn.update(worksheet="Users", data=pd.concat([df, new_data], ignore_index=True))
                        st.success("✅ Account Created! Log in now.")
        st.markdown('</div>', unsafe_allow_html=True)

else: # --- MAIN DASHBOARD ---
    st.sidebar.markdown(f"**Verified Account:**\n{st.session_state.email}")
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.session_state.step = 1; st.rerun()

    c_main, c_side = st.columns([2.5, 1])
    
    with c_main:
        st.subheader("📊 Clinical Analysis Terminal")
        file = st.file_uploader("Upload Specimen / Report Image", type=["jpg","png","jpeg"])
        if file:
            img = Image.open(file); st.image(img, use_container_width=True)
            lang = st.selectbox("Report Language", ["English", "Bengali", "Hindi"])
            if st.button("EXECUTE ANALYSIS"):
                with st.spinner("AI Engine Processing..."):
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    res = model.generate_content([f"Provide forensic diagnostic report in {lang}", img])
                    report = res.text
                    st.markdown(f"### Result:\n{report}")
                    
                    # Voice & PDF Support
                    tts = gTTS(text=report, lang='en' if lang=="English" else ('bn' if lang=="Bengali" else 'hi'))
                    v_io = io.BytesIO(); tts.write_to_fp(v_io); st.audio(v_io)
                    st.download_button("📄 Download PDF", create_report_pdf(report), "Report.pdf", "application/pdf")

    with c_side:
        # --- DYNAMIC IMPACT COUNTER ---
        st.markdown('<div class="impact-stats">', unsafe_allow_html=True)
        st.markdown("### 🕊️ Social Impact Board")
        try:
            charity_df = conn.read(worksheet="Charity", ttl=0)
            patients = charity_df[charity_df['Type'] == 'Patients']['Value'].values[0]
            fund = charity_df[charity_df['Type'] == 'Fund']['Value'].values[0]
            st.metric("Lives Impacted", f"{patients}+")
            st.metric("Medical Aid Fund", f"${fund}")
        except:
            st.metric("Lives Impacted", "1,200+")
            st.metric("Medical Aid Fund", "$10,000")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.warning("🤝 **Help Request**\nAre you underprivileged? Request free clinical aid.")
        req_msg = st.text_area("How can we help you?")
        if st.button("Send Request"):
            if req_msg:
                try:
                    t_df = conn.read(worksheet="Tickets", ttl=0)
                    new_ticket = pd.DataFrame([{"Email": st.session_state.email, "Request": req_msg, "Status": "Pending"}])
                    conn.update(worksheet="Tickets", data=pd.concat([t_df, new_ticket], ignore_index=True))
                    st.success("Request logged. We will contact you.")
                except: st.error("Database Busy. Contact support.")
