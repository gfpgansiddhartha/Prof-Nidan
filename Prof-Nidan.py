import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🚀 PROF. NIDAN - Database Test")

try:
    # কানেকশন তৈরি করা
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ডাটাবেস থেকে 'Users' শিট পড়ার চেষ্টা
    df = conn.read(worksheet="Users", ttl=0)
    
    st.success("🎯 বিঙ্গো! আপনার ডাটাবেস কানেক্ট হয়ে গেছে।")
    st.write("এখানে আপনার ডাটাবেসের কিছু অংশ দেখানো হলো:")
    st.dataframe(df.head())
    
except Exception as e:
    st.error("❌ কানেকশন এখনো হয়নি। নিচে আসল কারণটি দেখুন:")
    st.code(str(e))
