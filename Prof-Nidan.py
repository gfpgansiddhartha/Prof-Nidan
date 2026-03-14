import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random, string, datetime, re, pandas as pd

# 1. DATABASE CONNECTION (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    """Fetches data directly from Google Sheets."""
    return conn.read(worksheet=worksheet_name, ttl=0)

def save_user_to_db(email, password):
    """Saves a new user to the database."""
    df = get_data("Users")
    new_user = pd.DataFrame([{"Email": email, "Password": password}])
    updated_df = pd.concat([df, new_user], ignore_index=True)
    conn.update(worksheet="Users", data=updated_df)
    st.cache_data.clear()

# 2. EMAIL OTP FUNCTION (4-Character Alphabetic OTP)
def send_otp(receiver_email, otp_code):
    sender = st.secrets["EMAIL_USERNAME"]
    pwd = st.secrets["EMAIL_PASSWORD"]
    
    msg = MIMEMultipart()
    msg['From'] = f"PROF. NIDAN Support <{sender}>"
    msg['To'] = receiver_email
    msg['Subject'] = "Your Login Verification Code"
    msg.attach(MIMEText(f"Hello, your security verification code is: {otp_code}", 'plain'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# 3. PASSWORD STRENGTH CHECK (Minimum 8 Characters)
def check_password(p):
    if len(p) < 8: 
        return False, "Password must be at least 8 characters long."
    if not re.search("[A-Z]", p) or not re.search("[0-9]", p):
        return False, "Password must contain at least one uppercase letter and one number."
    return True, "Strong Password!"

# --- MAIN APP INTERFACE ---
st.title("🔬 PROF. NIDAN: Clinical Intelligence")

if "auth" not in st.session_state: st.session_state.auth = False
if "step" not in st.session_state: st.session_state.step = 1

if not st.session_state.auth:
    menu = st.sidebar.selectbox("Menu", ["Login", "Create New Account"])
    
    if menu == "Create New Account":
        st.subheader("Sign Up")
        email = st.text_input("Enter your Email:")
        pwd = st.text_input("Create Password (Min 8 characters):", type="password")
        
        ok, msg = check_password(pwd)
        if pwd: 
            if ok: st.success(msg)
            else: st.error(msg)
        
        if st.button("Register Now") and ok:
            users = get_data("Users")
            if email in users['Email'].values: 
                st.error("This email is already registered!")
            else:
                save_user_to_db(email, pwd)
                st.success("Account created successfully! Please proceed to Login.")

    elif menu == "Login":
        st.subheader("User Login")
        if st.session_state.step == 1:
            email = st.text_input("Email:")
            pwd = st.text_input("Password:")
            if st.button("Next Step"):
                users = get_data("Users")
                # Verification logic
                if email in users['Email'].values and str(users.loc[users['Email']==email, 'Password'].values[0]) == pwd:
                    otp = ''.join(random.choices(string.ascii_uppercase, k=4))
                    st.session_state.otp = otp
                    st.session_state.email = email
                    if send_otp(email, otp):
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("Failed to send OTP. Please check your internet or configuration.")
                else: 
                    st.error("Invalid Email or Password!")
        
        else:
            st.info(f"A 4-character code has been sent to {st.session_state.email}")
            otp_in = st.text_input("Enter the 4-character code:").upper()
            if st.button("Verify & Login"):
                if otp_in == st.session_state.otp:
                    st.session_state.auth = True
                    st.success("Login Successful!")
                    st.rerun()
                else: 
                    st.error("Incorrect code! Please check your email.")
            
            if st.button("Go Back"):
                st.session_state.step = 1
                st.rerun()

else:
    # --- AUTHENTICATED APP SECTION ---
    st.sidebar.success(f"User: {st.session_state.email}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.step = 1
        st.rerun()

    st.subheader("Upload Clinical Report or Specimen Image")
    
    # Placeholder for AI Analysis
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Specimen', use_container_width=True)
        
        if st.button("Run Forensic AI Analysis"):
            with st.spinner("AI is analyzing the specimen..."):
                # Your Gemini AI logic goes here
                st.write("AI analysis result will appear here.")
