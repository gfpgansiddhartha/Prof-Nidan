import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, pandas as pd, io
from gtts import gTTS
import streamlit.components.v1 as components

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="PROF. NIDAN AI | Science & Care", layout="wide", page_icon="🔬")

# DIRECT CONFIGURATION (Hardcoded to avoid Secrets error)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zvIl5jEfW7IVaQAejssbZOouFoCxTwJ5AqYtCUQLJy0/edit"

# This part fixes the 'Unable to load PEM file' forever
if "connections" not in st.secrets:
    st.secrets["connections"] = {}
if "gsheets" not in st.secrets["connections"]:
    st.secrets["connections"]["gsheets"] = {
        "type": "service_account",
        "project_id": "siddhartha-1st",
        "private_key_id": "cadd79513149a7b3559be29672eee5a37fec3480",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0PLqvv8aoLea7\noQpgXZ9dOq0jYn9Sl4lfgr5SYkytuowjjlkZ2MGPK8Vqyt89ZpY8JyIJZMfBrMsS\nULeYWibTpaJAsgqOCng67LHXjvBnKGzvUZxuzDE7IGyCTRM+UX4xioPt0yCx6Tjb\nc3+V9KpPHbZXvOSQJ5y6zdurymutqN1e66z5T7BtQ8ZahCcn2tWwY9hlil/fyCVA\nB/wjUVqwvilfLqNje+SZ5ihy9QT7fv1RnOpyqHjp/eWsa/ptt3Ohe8I4I7mdi4Ur\noFHOBJQp3hhrfpBob27RQ4PgET1w+sCMNt/m1zjkTrsm/WZ+GVuQjpVqPbODVDj3\nQWa4lupLAgMBAAECggEAGYboYe/lcPhfT3+1eoSIB6pBz1sp8UapHC/mSMDHX2um\nYXrNv81lTKPEaCWnjIi1Cnv4ZCAz8ohIkqV/+0H5ccxpuIP+3rM46A+R+Je0EMg2\n9YY3g7HD3z3uYF4ONatRFi8qFErsvIXtmZc4IMLwRBhPNQn5zTjvB74UOLaInaWq\nKwLWQUtXhkeHsLy53CWei4sOULtC+TQuHag4KKNj9tuy8NR63mSIXG7tjl/LsMqX\n8ecIpVDzlAglav10ExK4/ptN2oXP2gJUiW9Pt5zGutSG8uGup0uzJtCD+NeapzP4\nFpW/ZZzwenL2YJS0eFsBWp9TD9iPaNttNMsCS1AhkQKBgQDZYCwZ5J4jQ8ADr0+c\nnXHvYO9ASSemVJmZuzuyN2tUhiqynyj3a5fbODtA74PxqhFYHThhjzQmommt6wltq\nqMH3UXR4d3juacaVtqtbNbZ820Lh2AFpR4sveZUHRKPvGXd+eZdSvTsjhym4P4EN\nne3dBFPYWR3bnp7OgBbXX413OrQKBgQDUQzrg6KGkgWlW4LMQXn+gQdcvFZJ1UqQW\n7Az720ejfchsjRGOjDWGmlRduUNmNlarM8+x0/dgeSurMz0aGPJIz6lkZmDsae6R\nB01MdFOnHxQTdIbDe0o6FovTAZiQ19qm5BKBptCYADbqbPHBZmC/CXMpYlT3LMzx\n2zL+zMWT1wKBgD6xCucI1UbMYlNtuyMYVStezLqJkJFQethYW0bqJu++g978Z+x6\nyDxTb2DlmUbLFdiTgFtAJhn3Nyo3ZZAUTaSbXGDl6/2uifRhs3fhvNizj818s6N+\nW7j8cque8zyg9qKGRMs7AhRUBgc6YWjXA+TEO9jfEX7sEdUD8Jbr3wEdAoGAfM+r\nZ2Ri5+BQmI03vYBTe2A7r6v3mpUld3UFjXK7BR+JIoswr6kyMBu/T/0H7Ko2/CRT\nFDWXWFrnmpteamIQ1U+GQ0sP4vPHG/A3O6WLKtHTdD0ooPl2BAIN5d0iYMkMAOZL\nG4GDVl2J7P5yiU4xxSNBXCw92bm2KODDc5/k7bECgYBH/PK1SM4rUGJAdkf5HXN3\nkzRfw6WXT7jZUFktgK1nTA8vGLGI/j12J0KCE802OICSGaKQQCWCBPFWfYd8S1yu\nWRnUw+oLVVMFCR43ogHjysAUN2p7UK94Aiv5Yh0tFHOk7A7dRawwATklH3uyodUx\nYNMADQ2XsdqT7gt6Frswtg==\n-----END PRIVATE KEY-----\n",
        "client_email": "prof-nidan-db@siddhartha-1st.iam.gserviceaccount.com",
        "client_id": "112835785185769220057",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/prof-nidan-db%40siddhartha-1st.iam.gserviceaccount.com"
    }

# Connection Initialization
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"📡 Initial Connection Offline: {e}")

# --- REST OF THE APP --- (STAYS THE SAME)
def send_security_mail(receiver, otp):
    try:
        sender = st.secrets["EMAIL_USERNAME"]
        pwd = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart(); msg['From'] = f"PROF. NIDAN Support <{sender}>"; msg['To'] = receiver; msg['Subject'] = f"Verification Code: {otp}"
        msg.attach(MIMEText(f"Your clinical access verification code is: {otp}\nDo not share this code.", 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587); server.starttls(); server.login(sender, pwd); server.send_message(msg); server.quit()
        return True
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

# Display Banner
components.html('<div style="width:100%; border-radius:20px; overflow:hidden; height:300px; background:#004a99; color:white; display:flex; align-items:center; justify-content:center; font-family:Arial;"><h1>PROF. NIDAN AI Dash</h1></div>', height=310)

if not st.session_state.auth:
    l, c, r = st.columns([1, 1.8, 1])
    with c:
        t_log, t_reg = st.tabs(["🔐 Login", "📝 Register"])
        with t_log:
            if st.session_state.step == 1:
                em = st.text_input("Email", key="l_em")
                pw = st.text_input("Password", type="password", key="l_pw")
                if st.button("VERIFY IDENTITY"):
                    try:
                        df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                        match = df[df['Email'] == em]
                        if not match.empty and str(match.iloc[0]['Password']) == pw:
                            otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                            st.session_state.otp = otp; st.session_state.email = em
                            if send_security_mail(em, otp): st.session_state.step = 2; st.rerun()
                            else: st.error("Email service busy.")
                        else: st.error("❌ Invalid Credentials.")
                    except Exception as e: st.error(f"📡 Login Error: {str(e)}")
            else:
                code = st.text_input("Enter 4-Letter Code", max_chars=4).upper()
                if st.button("CONFIRM LOGIN"):
                    if code == st.session_state.otp: st.session_state.auth = True; st.rerun()
                    else: st.error("❌ Incorrect Code.")
        with t_reg:
            rem = st.text_input("New Email", key="r_em")
            rpw = st.text_input("Create Password", type="password", key="r_pw")
            if st.button("CREATE ACCOUNT"):
                try:
                    df = conn.read(spreadsheet=SHEET_URL, worksheet="Users", ttl=0)
                    if rem in df['Email'].values: st.error("Email already exists.")
                    else:
                        new_row = pd.DataFrame([{"Email": rem, "Password": rpw}])
                        conn.update(spreadsheet=SHEET_URL, worksheet="Users", data=pd.concat([df, new_row], ignore_index=True))
                        st.success("✅ Account Created! Please Login.")
                except Exception as e: st.error(f"📡 Register Error: {str(e)}")
else:
    st.sidebar.markdown(f"**Verified User:**\n{st.session_state.email}")
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.session_state.step = 1; st.rerun()
    st.header("📋 Clinical Terminal Active")
    file = st.file_uploader("Upload Medical Specimen", type=["jpg","png","jpeg"])
    if file:
        img = Image.open(file); st.image(img, use_container_width=True)
        if st.button("EXECUTE ANALYSIS"):
            with st.spinner("AI analyzing..."):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Provide forensic medical summary", img])
                st.markdown(f"### Result:\n{res.text}")
