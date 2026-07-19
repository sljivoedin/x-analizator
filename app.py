import requests
import streamlit as st

st.set_page_config(page_title="Debug Analizator", layout="wide")
st.title("⚽ Debug Analizator")

# 1. PRVO DEFINIŠEMO VARIJABLE
API_KEY = "3ddcbeccab1913faff15acd0af83268f"
REGION = "us,uk,eu"
MARKETS = "h2h"

if st.button("🔄 Osvježi"):
    st.rerun()

# 2. ONDA RADI TEST
liga_key = "soccer_usa_mls" 
url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"

try:
    resp = requests.get(url)
    st.write(f"Status kod za {liga_key}: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        st.write(f"Broj pronađenih mečeva: {len(data)}")
        if len(data) > 0:
            st.write("Prvi meč iz ponude:")
            st.write(data[0])
        else:
            st.warning("API je vratio praznu listu [].")
    else:
        st.error(f"Greška sa API-jem: {resp.text}")

except Exception as e:
    st.error(f"Kod je pukao: {e}")
