import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🚀 PROF. NIDAN - Final Launch")

try:
    # ১. ডাটাবেস কানেকশন
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ২. ডাটা পড়ার চেষ্টা (Users শিট থেকে)
    # খেয়াল করুন: আপনার শিটের নাম যেন হুবহু 'Users' হয়
    df = conn.read(worksheet="Users", ttl=0)
    
    st.success("✅ অভিনন্দন সিদ্ধার্থ! ডাটাবেস একদম নিখুঁতভাবে কানেক্ট হয়েছে।")
    st.write("### Users Database Preview:")
    st.dataframe(df.head())
    
    st.info("আপনার ডাটাবেস এখন লাইভ। এবার কি আমি মেইন অ্যাপের বাকি কোডগুলো যোগ করে দেব?")

except Exception as e:
    st.error("❌ কানেকশন এখনো সফল হয়নি।")
    st.write("### 🔍 সমস্যার আসল কারণ:")
    error_msg = str(e)
    
    if "WorksheetNotFound" in error_msg:
        st.warning("⚠️ আপনার গুগল শিটের নামের সাথে কোডের নামের মিল নেই। গুগল শিটের নিচের ট্যাবে গিয়ে নাম বদলে 'Users' করে দিন।")
    elif "RefreshError" in error_msg or "invalid_grant" in error_msg:
        st.warning("⚠️ Private Key-তে সমস্যা। Secrets বক্স থেকে আগের সব মুছে নতুন করে আমার দেওয়া কী-টি বসান।")
    else:
        st.code(error_msg)
