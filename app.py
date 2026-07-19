from pyngrok import ngrok
import requests
import time
import streamlit as st
from datetime import datetime, timezone, timedelta

# Otvaranje javnog tunela za pristup
try:
    javni_url = ngrok.connect(8501)
    print(f"\n🌍 TVOJ LINK ZA POSAO I TELEFON: {javni_url.public_url} \n")
    st.success(f"Aplikacija je uživo na internetu! Link za posao: {javni_url.public_url}")
except Exception as e:
    print(f"\nGreška pri pokretanju ngrok-a: {e}\n")

# Podešavanje izgleda stranice
st.set_page_config(page_title="X Analizator Kvota", page_icon="⚽", layout="wide")

st.title("⚽ Globalni X Analizator Kvota")
st.write("Aplikacija automatski skenira sve aktivne lige na svijetu u narednih 24h i izdvaja mečeve sa najvećim potencijalom za remi.")

API_KEY = "3ddcbeccab1913faff15acd0af83268f"
REGION = "eu"
MARKETS = "h2h"

# Dugme za ručno osvježavanje
if st.button("🔄 Osvježi ponudu"):
    st.rerun()

with st.spinner("🔍 Duboko skeniram svjetske lige u naredna 24 sata..."):
    url_lige = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    
    try:
        odgovor_lige = requests.get(url_lige)
        if odgovor_lige.status_code == 200:
            sve_fudbalske_lige = []
            lige_podaci = odgovor_lige.json()
            
            for liga in lige_podaci:
                if liga.get("group") == "Soccer" and liga.get("active", False):
                    sve_fudbalske_lige.append(liga.get("key"))
            
            svi_parovi = []
            
            # Vremenski filter: naredna 24 sata (UTC+2 za BiH)
            sada_lokalno = datetime.now(timezone(timedelta(hours=2)))
            granica_24h = sada_lokalno + timedelta(hours=24)
            
            # Skeniramo do 50 liga odjednom
            za_skeniranje = sve_fudbalske_lige[:50]
            
            for liga_key in za_skeniranje:
                url_mecevi = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
                odgovor_mecevi = requests.get(url_mecevi)
                
                if odgovor_mecevi.status_code == 200:
                    mecevi_podaci = odgovor_mecevi.json()
                    
                    for mec in mecevi_podaci:
                        home_team = mec.get("home_team")
                        away_team = mec.get("away_team")
                        sport_title = mec.get("sport_title")
                        commence_time_str = mec.get("commence_time")
                        
                        try:
                            vrijeme_utc = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                            lokalno_vrijeme = vrijeme_utc.astimezone(timezone(timedelta(hours=2)))
                            
                            # Uzmi utakmice u naredna 24h
                            if sada_lokalno <= lokalno_vrijeme <= granica_24h:
                                vrijeme_prikaz = lokalno_vrijeme.strftime("%d.%m. u %H:%M")
                            else:
                                continue
                        except:
                            continue
                        
                        kvote_1 = []
                        kvote_x = []
                        kvote_2 = []
                        kladionice_lista = []
                        
                        bookmakers = mec.get("bookmakers", [])
                        for bm in bookmakers:
                            bm_title = bm.get("title")
                            markets = bm.get("markets", [])
                            for m in markets:
                                if m.get("key") == "h2h":
                                    outcomes = m.get("outcomes", [])
                                    k1, kx, k2 = None, None, None
                                    for o in outcomes:
                                        if o.get("name") == home_team:
                                            k1 = float(o.get("price"))
                                        elif o.get("name") == "Draw":
                                            kx = float(o.get("price"))
                                        elif o.get("name") == away_team:
                                            k2 = float(o.get("price"))
                                    
                                    if k1 and kx and k2:
                                        kvote_1.append(k1)
                                        kvote_x.append(kx)
                                        kvote_2.append(k2)
                                        kladionice_lista.append(bm_title)
                        
                        if kvote_x:
                            sr_1 = sum(kvote_1) / len(kvote_1)
                            sr_x = sum(kvote_x) / len(kvote_x)
                            sr_2 = sum(kvote_2) / len(kvote_2)
                            
                            najmanja_kvota = min(kvote_x)
                            indeks_najmanje = kvote_x.index(najmanja_kvota)
                            najbolja_kladionica = kladionice_lista[indeks_najmanje]
                            
                            # Formula za visoke procente
                            odnos_1_2 = abs((1/sr_1) - (1/sr_2))
                            baza_sanse = (1 / sr_x) * 100
                            
                            if odnos_1_2 < 0.15:  
                                izracunata_sansa = int(baza_sanse * 3.4)  
                            else:
                                izracunata_sansa = int(baza_sanse * 2.5)
                            
                            if izracunata_sansa > 96: 
                                izracunata_sansa = 96
                                
                            # NOVI FILTER: Prikazuj sve parove sa šansom većom ili jednakom 60%
                            if izracunata_sansa >= 60:
                                pronalazak = {
                                    "Šansa za X": f"{izracunata_sansa}%",
                                    "Liga": sport_title,
                                    "Satnica": vrijeme_prikaz,
                                    "Utakmica": f"{home_team} - {away_team}",
                                    "Kvote (1 | X | 2)": f"{sr_1:.2f} | {sr_x:.2f} | {sr_2:.2f}",
                                    "Kladionica": najbolja_kladionica,
                                    "sansa_num": izracunata_sansa
                                }
                                svi_parovi.append(pronalazak)
            
            # Sortiranje po šansi (od najveće ka najmanjoj)
            svi_parovi.sort(key=lambda x: x["sansa_num"], reverse=True)
            
            for p in svi_parovi:
                p.pop("sansa_num", None)
            
            if svi_parovi:
                st.success(f"Analiza završena! Pronađeno i rangirano parova: {len(svi_parovi)}")
                st.table(svi_parovi)
            else:
                st.warning("⚠️ Trenutno nema parova u naredna 24h koji prelaze šansu od 60%. Pokušaj malo kasnije.")
        else:
            st.error("Greška pri povlačenju podataka sa API-ja.")
            
    except Exception as e:
        st.error(f"Došlo je do greške u analizi: {e}")