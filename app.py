# TESTIRAMO SAMO JEDNU LIGU
liga_key = "soccer_usa_mls" 
url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
resp = requests.get(url)

st.write(f"Status kod za {liga_key}: {resp.status_code}")
st.write(f"Sadržaj odgovora: {resp.text[:500]}") # Ispisaće prvih 500 znakova
