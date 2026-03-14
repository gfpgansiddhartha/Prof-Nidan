import streamlit as st
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="PROF. NIDAN", layout="wide")

# 2. SETUP GEMINI API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Missing API Key. Please check Streamlit Secrets.")

# 3. LOGGING & BANNING SYSTEM (Session-based)
if "logs" not in st.session_state:
    st.session_state.logs = []
if "banned_users" not in st.session_state:
    st.session_state.banned_users = []

def add_log(user, action):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append({"Time": now, "User": user, "Action": action})

# 4. EMAIL FUNCTION (OTP)
def send_otp_email(receiver_email, otp_code):
    sender_email = st.secrets["EMAIL_USERNAME"]
    sender_password = st.secrets["EMAIL_PASSWORD"]
    
    message = MIMEMultipart()
    message["From"] = f"PROF. NIDAN Support <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = "Your Security Verification Code"
    
    body = f"Hello,\n\nYour 4-character security code for PROF. NIDAN is: {otp_code}\n\nDo not share this with anyone."
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email delivery failed: {e}")
        return False

# 5. INITIALIZE SESSION STATES
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "otp" not in st.session_state:
    st.session_state.otp = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# 6. LOGIN INTERFACE
if not st.session_state.authenticated:
    st.title("🛡️ PROF. NIDAN - Secure Portal")
    login_mode = st.radio("Choose Login Type:", ["User (Email OTP)", "Admin (Password)"])
    
    if login_mode == "Admin (Password)":
        admin_pass = st.text_input("Enter Admin Password:", type="password")
        if st.button("LOGIN AS ADMIN"):
            if admin_pass == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.session_state.current_user = "Admin"
                add_log("Admin", "Logged In")
                st.rerun()
            else:
                st.error("Invalid Admin Password!")
                
    else:
        user_email = st.text_input("Enter your Email ID:")
        if user_email in st.session_state.banned_users:
            st.error("This account has been banned due to suspicious activity.")
        else:
            if st.button("SEND OTP"):
                if user_email:
                    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    st.session_state.otp = otp
                    if send_otp_email(user_email, otp):
                        st.success(f"A 4-character code has been sent to {user_email}")
                else:
                    st.warning("Please enter a valid email address.")
                    
            entered_otp = st.text_input("Enter the OTP received:")
            if st.button("VERIFY & LOG IN"):
                if entered_otp == st.session_state.otp and st.session_state.otp != "":
                    st.session_state.authenticated = True
                    st.session_state.is_admin = False
                    st.session_state.current_user = user_email
                    add_log(user_email, "Logged In")
                    st.rerun()
                else:
                    st.error("Incorrect OTP. Please try again.")

# 7. MAIN APPLICATION (POST-LOGIN)
else:
    # Sidebar Navigation
    st.sidebar.title("PROF. NIDAN")
    if st.session_state.is_admin:
        st.sidebar.success("Mode: ADMINISTRATOR")
        page = st.sidebar.radio("Navigate to:", ["App Dashboard", "System Activity", "User Management"])
    else:
        st.sidebar.info(f"User: {st.session_state.current_user}")
        page = "App Dashboard"
        
    if st.sidebar.button("Logout"):
        add_log(st.session_state.current_user, "Logged Out")
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()

    # --- PAGE: USER MANAGEMENT (Admin Only) ---
    if st.session_state.is_admin and page == "User Management":
        st.title("🚫 User Control & Banning")
        st.subheader("Banned Users")
        if st.session_state.banned_users:
            for b_user in st.session_state.banned_users:
                c1, c2 = st.columns([3, 1])
                c1.write(b_user)
                if c2.button("Unban", key=b_user):
                    st.session_state.banned_users.remove(b_user)
                    st.rerun()
        else:
            st.info("No users are currently banned.")

        st.divider()
        st.subheader("Ban a User")
        email_to_ban = st.text_input("Enter Email to ban:")
        if st.button("CONFIRM BAN"):
            if email_to_ban and email_to_ban not in st.session_state.banned_users:
                st.session_state.banned_users.append(email_to_ban)
                add_log("Admin", f"Banned User: {email_to_ban}")
                st.success(f"User {email_to_ban} is now banned.")
                st.rerun()

    # --- PAGE: SYSTEM ACTIVITY (Admin Only) ---
    elif st.session_state.is_admin and page == "System Activity":
        st.title("📊 System Usage Logs")
        col1, col2 = st.columns(2)
        col1.metric("Total Activities", len(st.session_state.logs))
        col2.metric("System Status", "Live/Healthy")

        if st.session_state.logs:
            df = pd.DataFrame(st.session_state.logs)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No activity logs available.")

    # --- PAGE: APP DASHBOARD ---
    else:
        st.title("🔬 Forensic Diagnostic Vision")
        
        # Social Mission Info
        st.info("""
        🕊️ **Our Mission:** This project aims to support underprivileged children. 
        We are working to partner with orphanages to ensure that a portion of our 
        future proceeds goes directly to their medical care.
        """)

        uploaded_file = st.file_uploader("Upload specimen (X-Ray, Lab Report, etc.)", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Specimen", width=500)
            
            # Language Mapping
            languages = {
                "English": "English",
                "Bengali (বাংলা)": "Bengali",
                "Hindi (हिन्दी)": "Hindi",
                "Marathi (मराठी)": "Marathi",
                "Tamil (தமிழ்)": "Tamil",
                "Telugu (తెలుగు)": "Telugu",
                "Gujarati (ગુજરાતી)": "Gujarati"
            }
            
            selected_lang = st.selectbox("Select Report Language:", list(languages.keys()))
            
            if st.button("EXECUTE CLINICAL ANALYSIS"):
                add_log(st.session_state.current_user, f"Analyzed Image ({selected_lang})")
                with st.spinner("Analyzing Specimen... Please wait."):
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        target_lang = languages[selected_lang]
                        prompt = f"Analyze this medical image and provide a detailed diagnostic report strictly in {target_lang}."
                        
                        response = model.generate_content([prompt, image])
                        st.subheader("Diagnostic Report:")
                        st.markdown(response.text)
                        
                        st.warning("⚠️ DISCLAIMER: This is an AI-generated analysis and NOT a final medical diagnosis. Consult a registered doctor for medical decisions.")
                    
                    except Exception as e:
                        st.error("The AI server is temporarily busy. Please try again in 60 seconds.")
