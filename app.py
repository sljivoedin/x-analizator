import requests
import streamlit as st
from datetime import datetime, timezone, timedelta

# Podešavanje izgleda
st.set_page_config(page_title="X Analizator Kvota", page_icon="⚽", layout="wide")
st.title("⚽ Globalni X Analizator Kvota")

API_KEY = "3ddcbeccab1913faff15acd0af83268f"
REGION = "eu"
MARKETS = "h2h"

if st.button("🔄 Osvježi ponudu"):
    st.rerun()

with st.spinner("🔍 Skeniram sve svjetske lige..."):
    # 1. Uzmi listu SVIH sportova
    url_lige = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    
    try:
        odgovor_lige = requests.get(url_lige)
        if odgovor_lige.status_code == 200:
            sve_fudbalske_lige = [liga["key"] for liga in odgovor_lige.json() if liga.get("group") == "Soccer" and liga.get("active")]
            
            svi_parovi = []
            sada_lokalno = datetime.now(timezone(timedelta(hours=2)))
            granica_24h = sada_lokalno + timedelta(hours=24)
            
            # Skeniramo sve pronađene lige
            for liga_key in sve_fudbalske_lige:
                url_mecevi = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
                odgovor_mecevi = requests.get(url_mecevi)
                
                if odgovor_mecevi.status_code == 200:
                    for mec in odgovor_mecevi.json():
                        # Provjera vremena
                        vrijeme_utc = datetime.fromisoformat(mec["commence_time"].replace("Z", "+00:00"))
                        lokalno_vrijeme = vrijeme_utc.astimezone(timezone(timedelta(hours=2)))
                        
                        if sada_lokalno <= lokalno_vrijeme <= granica_24h:
                            # Logika za X (remi)
                            for bm in mec.get("bookmakers", []):
                                for m in bm.get("markets", []):
                                    if m["key"] == "h2h":
                                        outcomes = {o["name"]: float(o["price"]) for o in m["outcomes"]}
                                        if "Draw" in outcomes:
                                            kx = outcomes["Draw"]
                                            # Tvoja formula za šansu
                                            sansa = int((1 / kx) * 250) 
                                            if sansa >= 10:
                                                svi_parovi.append({
                                                    "Šansa za X": f"{min(sansa, 99)}%",
                                                    "Liga": mec["sport_title"],
                                                    "Vrijeme": lokalno_vrijeme.strftime("%d.%m. %H:%M"),
                                                    "Par": f"{mec['home_team']} - {mec['away_team']}",
                                                    "Kvota X": kx
                                                })
            
            if svi_parovi:
                # Ukloni duplikate (isti par iz različitih kladionica)
                jedinstveni = {p["Par"]: p for p in svi_parovi}.values()
                st.table(list(jedinstveni))
            else:
                st.warning("Trenutno nema parova sa šansom > 10%.")
        else:
            st.error("API greška.")
    except Exception as e:
        st.error(f"Greška: {e}")
