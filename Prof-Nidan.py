import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔍 Deep Database Diagnostics")

# ১. সিক্রেটস চেক
st.subheader("Step 1: Checking Secrets")
if "gsheets" in st.secrets:
    st.success("✅ 'gsheets' section found in Secrets.")
else:
    st.error("❌ 'gsheets' section NOT found in Secrets. Please check the [gsheets] header.")
    st.stop()

# ২. কানেকশন এবং এরর চেক
st.subheader("Step 2: Testing Connection")
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # এখানে আপনার শিটের নামগুলো একে একে টেস্ট করা হবে
    sheet_names = ["Users", "Charity", "Tickets"]
    
    for name in sheet_names:
        try:
            df = conn.read(worksheet=name, ttl=0)
            st.success(f"✅ Successfully read worksheet: '{name}'")
            st.write(f"Preview of {name}:", df.head(2))
        except Exception as e:
            st.warning(f"⚠️ Could not read worksheet '{name}'. Error: {e}")
            st.info(f"Is the worksheet name in Google Sheets exactly '{name}'?")

except Exception as e:
    st.error("❌ Connection Failed Completely!")
    st.write("### Technical Error Details:")
    st.code(str(e))
