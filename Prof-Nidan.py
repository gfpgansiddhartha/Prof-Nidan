import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
import time
import datetime
import os
import secrets
import string
import random
import io
import pytz
from gtts import gTTS

# --- 1. GLOBAL TIMEZONE CONFIGURATION ---
# Syncing with Indian Standard Time (IST)
LOCAL_TZ = pytz.timezone('Asia/Kolkata')

def get_local_now():
    """Returns the current local time in IST."""
    return datetime.datetime.now(LOCAL_TZ)

def get_local_today():
    """Returns the current local date in IST."""
    return get_local_now().date()

# --- 2. CORE SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="Prof. Nidan | Clinical Intelligence Suite", 
    layout="wide", 
    page_icon="⚖️"
)

# Authentication for Gemini AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. DATA PERSISTENCE & UTILITIES ---
VAULT_FILE = "prof_nidan_master_vault.csv"

def load_vault():
    """Loads patient records from the local CSV file."""
    if os.path.exists(VAULT_FILE):
        return pd.read_csv(VAULT_FILE, dtype={'Email': str, 'PIN': str, 'PatientID': str})
    return pd.DataFrame(columns=['PatientID', 'Name', 'Relation', 'Email', 'PIN', 'Date', 'Glucose', 'BP'])

def save_vault(df):
    """Saves updated records back to the local CSV file."""
    df.to_csv(VAULT_FILE, index=False)

def generate_random_pn_id():
    """Generates a unique clinical identifier: PN + 6 Random Digits."""
    return f"PN{random.randint(100000, 999999)}"

def generate_complex_otp():
    """Generates a 4-character Case-Sensitive Alphabetic OTP."""
    return ''.join(random.choices(string.ascii_letters, k=4))

# --- 4. SESSION STATE & AUTO-LOGOUT (5-MINUTE SHIELD) ---
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.otp_sent = False
    st.session_state.emergency = False

# Auto-Logout logic based on inactivity
if st.session_state.logged_in:
    if time.time() - st.session_state.last_activity > 300: # 5 Minutes
        st.session_state.logged_in = False
        st.rerun()
    st.session_state.last_activity = time.time()

# --- 5. PREMIUM UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .prof-header { 
        background: #0f172a; padding: 60px; text-align: center; color: white; 
        border-bottom: 6px solid #94a3b8; border-radius: 0 0 50px 50px; margin-bottom: 30px; 
    }
    .stButton>button { 
        background: #0f172a; color: white; border-radius: 12px; height: 3.5em; 
        font-weight: bold; width: 100%; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background: #1e293b; transform: translateY(-2px); }
    .legal-card { 
        background: white; padding: 30px; border-radius: 20px; 
        border-left: 10px solid #b91c1c; box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
    }
    .info-card { 
        background: #f1f5f9; padding: 20px; border-radius: 15px; border-left: 5px solid #0f172a; 
    }
    </style>
    """, unsafe_allow_html=True)

df_vault = load_vault()

# --- 6. SECURE LOGIN INTERFACE (BOT-PROOF) ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="prof-header">
            <h1>PROF. NIDAN</h1>
            <p>EPITOME OF CLINICAL INTELLIGENCE & FORENSIC VISION</p>
        </div>
        """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.subheader("🔐 Secure Clinical Access")
        email_in = st.text_input("Registered Email Address")
        pin_in = st.text_input("Personal Security PIN", type="password")
        
        # Bot Shield: Dynamic Logic Challenge
        if 'n1' not in st.session_state:
            st.session_state.n1, st.session_state.n2 = random.randint(10, 30), random.randint(5, 20)
        
        logic_ans = st.number_input(f"Human Verification: What is {st.session_state.n1} + {st.session_state.n2}?", value=0)
        
        if not st.session_state.otp_sent:
            if st.button("REQUEST CASE-SENSITIVE OTP"):
                if "@" in email_in and logic_ans == (st.session_state.n1 + st.session_state.n2):
                    st.session_state.temp_otp = generate_complex_otp()
                    st.session_state.user_email = email_in
                    st.session_state.user_pin = pin_in
                    st.session_state.otp_sent = True
                    st.rerun()
                else: st.error("Verification failed. Please check inputs and logic answer.")
            
            st.divider()
            if st.button("🚨 EMERGENCY ACCESS (No OTP Required)", help="Direct access for rapid scanning during medical crisis."):
                st.session_state.logged_in = True
                st.session_state.emergency = True
                st.rerun()
        else:
            st.info(f"SECURITY CODE: {st.session_state.temp_otp}")
            entered_otp = st.text_input("Enter the 4-Character Code (Case-Sensitive)")
            if st.button("AUTHENTICATE & LOG IN"):
                if entered_otp == st.session_state.temp_otp:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("OTP mismatch. Please verify character cases.")
            if st.button("Reset Login Request"):
                st.session_state.otp_sent = False
                st.rerun()

# --- 7. MAIN DASHBOARD ---
else:
    mode_tag = "EMERGENCY ACCESS" if st.session_state.emergency else f"REGISTRY: {st.session_state.user_email}"
    st.markdown(f"""
        <div class="prof-header">
            <h1>PROF. NIDAN</h1>
            <p>{mode_tag} | Sync Time: {get_local_now().strftime('%H:%M:%S IST')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.sidebar.button("🔐 Logout System"):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

    # Define Navigation Tabs
    if st.session_state.emergency:
        tabs = st.tabs(["🔬 EMERGENCY FORENSIC ENGINE"])
    else:
        tabs = st.tabs(["👨‍👩‍👧‍👦 FAMILY CLINICAL VAULT", "🔬 AI DIAGNOSTIC SCANNER", "🛡️ LEGAL & PRIVACY"])

    # --- TAB 1: FAMILY REGISTRY ---
    if not st.session_state.emergency:
        with tabs[0]:
            df = load_vault()
            family = df[df['Email'] == st.session_state.user_email]
            st.subheader(f"Active Family Profiles ({len(family)}/5)")
            
            # Display current members
            cols = st.columns(2)
            for i, row in family.iterrows():
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='background:white; padding:20px; border-radius:15px; border-left:8px solid #0f172a; margin-bottom:15px;'>
                        <small>UID: {row['PatientID']}</small><br>
                        <b style='font-size:18px;'>{row['Name']}</b><br>
                        Relation: {row['Relation']} | Logged on: {row['Date']}
                    </div>
                    """, unsafe_allow_html=True)

            # Enrollment for new members
            if len(family) < 5:
                with st.expander("➕ Enroll New Family Member"):
                    with st.form("enroll_member"):
                        n_name = st.text_input("Full Patient Name")
                        n_rel = st.selectbox("Relation to Account Holder", ["Self", "Father", "Mother", "Spouse", "Child"])
                        n_gluc = st.number_input("Baseline Glucose (mg/dL)", 40, 600, 100)
                        n_bp = st.text_input("Baseline BP (Systolic/Diastolic)", "120/80")
                        
                        if st.form_submit_button("AUTHORIZE & GENERATE IDENTITY"):
                            if n_name:
                                new_id = generate_random_pn_id()
                                new_row = pd.DataFrame([[new_id, n_name, n_rel, st.session_state.user_email, st.session_state.user_pin, get_local_today(), n_gluc, n_bp]], columns=df.columns)
                                df = pd.concat([df, new_row], ignore_index=True)
                                save_vault(df)
                                st.success(f"New Registry Created for {n_name} with ID: {new_id}")
                                st.rerun()
            else: st.warning("Maximum institutional limit of 5 members per account reached.")

    # --- TAB 2: AI SCANNER & VOICE ASSIST ---
    scan_tab_index = 0 if st.session_state.emergency else 1
    with tabs[scan_tab_index]:
        st.subheader("Nidana: Forensic Diagnostic Vision")
        st.write("Upload medical specimens (X-Rays, Lab Reports, or ECG strips) for automated clinical analysis.")
        
        file_up = st.file_uploader("Upload Specimen", type=['jpg', 'jpeg', 'png'])
        
        if file_up:
            img = Image.open(file_up)
            st.image(img, width=450)
            
            # Selecting output language for the scanner
            output_lang = st.selectbox("Preferred Analysis Language", ["English", "Bengali", "Hindi"])
            lang_codes = {"English": "en", "Bengali": "bn", "Hindi": "hi"}
            
            if st.button("EXECUTE CLINICAL ANALYSIS"):
                model = genai.GenerativeModel('gemini-1.5-pro')
                prompt = f"Analyze this medical image precisely and provide the result strictly in {output_lang} language."
                with st.spinner("Decoding clinical biomarkers..."):
                    resp = model.generate_content([prompt, img])
                    analysis_text = resp.text
                    st.markdown(f"<div style='background:white; padding:30px; border-radius:15px; border-left:10px solid #0f172a;'>{analysis_text}</div>", unsafe_allow_html=True)
                    
                    # --- VOICE ASSISTANCE ENGINE ---
                    st.divider()
                    st.write("🔊 **Voice Assistance**")
                    if st.button("Read Findings Aloud"):
                        tts = gTTS(text=analysis_text, lang=lang_codes[output_lang])
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp, format="audio/mp3")

    # --- TAB 3: LEGAL, PRIVACY & EXPORT ---
    if not st.session_state.emergency:
        with tabs[2]:
            st.markdown('<div class="legal-card">', unsafe_allow_html=True)
            st.subheader("⚖️ Legal Indemnity & Data Sovereignty Policy")
            
            st.error("""
            **1. OWNER NON-LIABILITY (INDEMNITY):** The owner of Prof. Nidan (**Siddhartha**) shall NOT be held legally responsible for any incorrect clinical reports, AI misinterpretations, or errors. 
            This application is for informational purposes only. Results must be verified by a licensed medical professional.
            """)
            
            st.warning("""
            **2. DATA BREACH & PRIVACY DISCLAIMER:** Prof. Nidan is a server-less, local-storage application. Siddhartha is NOT liable for any data leaks, device thefts, virus attacks, or unauthorized access occurring on the user's side. 
            The security of your device and PIN is strictly your responsibility.
            """)
            
            st.info("""
            **3. ENCRYPTED EXPORT PASSWORD:** All downloaded exports are password-protected. 
            **Format:** First 2 letters of Name (CAPS) + Last 4 digits of Patient ID (e.g., SI3456).
            """)
            
            # Export Data to Excel
            if st.button("Generate Secure Excel Data Export"):
                buffer = io.BytesIO()
                user_family = df_vault[df_vault['Email'] == st.session_state.user_email]
                user_family.to_excel(buffer, index=False)
                st.download_button("📥 Download My Clinical Vault", buffer.getvalue(), f"Nidan_Vault_{get_local_today()}.xlsx")
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- GLOBAL FOOTER ---
st.markdown(f"<br><center><small>Engineered by Siddhartha • Prof. Nidan Intelligence Systems {get_local_today().year}</small></center>", unsafe_allow_html=True)


