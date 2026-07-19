import requests
import streamlit as st
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="X Analizator", layout="wide")
st.title("⚽ Debug Analizator")

API_KEY = "3ddcbeccab1913faff15acd0af83268f"
REGION = "eu"
MARKETS = "h2h"

if st.button("🔄 Osvježi"):
    st.rerun()

# 1. Uzmi listu liga
url_lige = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
try:
    odgovor = requests.get(url_lige)
    lige = [l["key"] for l in odgovor.json() if l.get("group") == "Soccer" and l.get("active")]
    
    st.write(f"Ukupno aktivnih liga za skeniranje: {len(lige)}")
    
    svi_parovi = []
    
    # Skeniramo prvih 10 liga radi brzine testa
    for liga_key in lige[:10]:
        url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
        resp = requests.get(url)
        
        if resp.status_code == 200:
            data = resp.json()
            st.write(f"Liga {liga_key} vraća {len(data)} mečeva.")
            
            for mec in data:
                # Provjera da li ima 'Draw' u ponudi
                for bm in mec.get("bookmakers", []):
                    for m in bm.get("markets", []):
                        if m["key"] == "h2h":
                            for o in m["outcomes"]:
                                if o["name"] == "Draw":
                                    kx = float(o["price"])
                                    sansa = int((1 / kx) * 250)
                                    if sansa >= 10:
                                        svi_parovi.append({
                                            "Liga": liga_key,
                                            "Par": f"{mec['home_team']} - {mec['away_team']}",
                                            "Šansa": f"{sansa}%",
                                            "Kvota X": kx
                                        })
    
    if svi_parovi:
        st.table(svi_parovi)
    else:
        st.warning("Nije pronađen nijedan meč sa 'Draw' opcijom u ovim ligama.")

except Exception as e:
    st.error(f"Greška: {e}")
