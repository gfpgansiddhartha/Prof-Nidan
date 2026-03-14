import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 Database Diagnostic Tool")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Users", ttl=0)
    st.success("✅ Connection Successful! I can read your sheet.")
    st.write(df.head())
except Exception as e:
    st.error("❌ Connection Failed!")
    st.write("### Actual Error Message from Google:")
    st.code(str(e))
