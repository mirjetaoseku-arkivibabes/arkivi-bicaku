import streamlit as st
import pandas as pd
import re
import os
import unicodedata

# 1. KONFIGURIMI I FAQES
st.set_page_config(page_title="Arkivi digjital Biçaku", layout="wide")

def normalizo_tekstin(tekst):
    if not tekst: return ""
    tekst = tekst.lower().replace('ë', 'e').replace('ç', 'c')
    return "".join(c for c in unicodedata.normalize('NFD', tekst) if unicodedata.category(c) != 'Mn')

def pastro_formatimin(tekst):
    if pd.isna(tekst): return ""
    return re.sub('<[^<]+?>', '', str(tekst)).replace("**", "").strip()

def marko_tekstin(tekst, fjala):
    if not fjala or fjala.strip() == "": return tekst
    paster = pastro_formatimin(tekst)
    pattern = re.compile(f"({re.escape(fjala)})", re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: yellow; color: black; padding: 2px; border-radius: 4px;">\1</mark>', paster)

# 2. STILIZIMI (CSS)
st.markdown("""
    <style>
    button[data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; }
    [data-testid="stExpander"] p { font-size: 22px !important; font-weight: bold !important; color: #1E3A8A !important; }
    .teksti-formatuar { font-size: 20px; line-height: 1.6; color: #222; padding: 20px; background: white; border-radius: 8px; border: 1px solid #eee; }
    .control-panel-bottom { display: flex; justify-content: space-between; gap: 20px; background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 10px; }
    .butoni-opsion { flex: 1; text-align: center; border:none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; color: white !important; font-size: 16px; }
    .biografia-tekst { font-size: 19px; line-height: 1.6; color: #333; padding: 10px; }
    .info-box-sidebar { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; font-size: 17px; color: #333; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# Funksioni i rregulluar për tastin "Në Fillim"
def shto_butonat_fund(tekst):
    t_paster = pastro_formatimin(tekst).replace('"', "'").replace('\n', ' ')
    return f"""
    <div class="control-panel-bottom">
        <button style="background:#2e7d32;" class="butoni-opsion" onclick='window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance("{t_paster}"); msg.lang="sq-AL"; window.speechSynthesis.speak(msg);'>🔊 Dëgjo</button>
        <button style="background:#d32f2f;" class="butoni-opsion" onclick="window.speechSynthesis.cancel()">🛑 Ndalo</button>
        <button style="background:#1E3A8A;" class="butoni-opsion" onclick="window.print()">🖨️ Printo</button>
        <button style="background:#6c757d;" class="butoni-opsion" onclick="window.parent.scrollTo({{top: 0, behavior: 'smooth'}})">⬆️ Në Fillim</button>
    </div>
    """

# 3. SIDEBAR
if 'sq' not in st.session_state: st.session_state.sq = ""
with st.sidebar:
    st.markdown("## 🔍 Kërkimi")
    st.session_state.sq = st.text_input("Shkruaj fjalën:", value=st.session_state.sq)
    if st.button("❌ Fshi kërkimin", use_container_width=True):
        st.session_state.sq = ""
        st.rerun()
    st.markdown("---")
    st.markdown(f'<div class="info-box-sidebar">Arkivi digjital paraqet punën 40-vjeçare të <b>Prof. Hasanali Biçaku</b> në mjekësinë alternative dhe popullore.</div>', unsafe_allow_html=True)

# 4. KREU (I rregulluar si në foton tuaj)
col1, col2 = st.columns([1, 2.5])
with col1:
    if os.path.exists("babai.png"): 
        st.image("babai.png", width=180)
with col2:
    st.markdown("""
        <div style="margin-top: 45px;">
            <h1 style="color:#1E3A8A; font-size:42px; margin-bottom:0; line-height: 1.1;">
                Prof. HASANALI BIÇAKU
            </h1>
            <h2 style="color:#555; font-size:26px; margin-top:5px; font-weight: normal; letter-spacing: 1px;">
                ARKIVI DIGJITAL
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ Shënime mbi autorin", expanded=False):
        st.markdown("""
        <div class="biografia-tekst">
            <b>Prof. Hasanali Biçaku (1927-2001)</b> ishte nismëtar i shkencës në praktikë në Kosovë. <br><br>
            Studioi dhe dha mësim në fushën <b>Kimi-Fizikë</b>. Në vitin <b>1951-1952</b> krijoi 
            <b>laboratorin e parë të kimisë</b> në <b>Gjimnazin Shqiptar në Prishtinë</b>.
        </div>
        """, unsafe_allow_html=True)

# 5. LOGJIKA E SHFAQJES
try:
    df = pd.read_excel("arkivi_HB.xlsx")
    tabs = st.tabs(["📙 STOP MAJASILLIT KUDO NË TRUP", "📙 KREJT MBI KOKËDHIMBJEN"])
    
    def shfaq_kapitujt(tema, foto, kerkimi, tab_obj):
        with tab_obj:
            c1, c2 = st.columns([1, 2.2])
            with c1:
                if os.path.exists(foto): st.image(foto, use_container_width=True)
            with c2:
                norm_kerkimi = normalizo_tekstin(kerkimi)
                filtër = df[df["BROSHURAT"].str.contains(tema, na=False, case=False)]
                if norm_kerkimi:
                    df['norm_teksti'] = df['TEKSTI I KAPITULLIT'].apply(normalizo_tekstin)
                    filtër = filtër[df['norm_teksti'].str.contains(norm_kerkimi, na=False)]
                for i, r in filtër.iterrows():
                    emri = pastro_formatimin(r['EMRI I KAPITULLIT']).upper()
                    with st.expander(emri, expanded=False):
                        txt = str(r['TEKSTI I KAPITULLIT'])
                        mark_txt = marko_tekstin(txt, kerkimi)
                        st.markdown(f'<div class="teksti-formatuar">{mark_txt.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                        st.components.v1.html(shto_butonat_fund(txt), height=100)

    shfaq_kapitujt("majasill", "majasilli.png", st.session_state.sq, tabs[0])
    shfaq_kapitujt("kokë", "kokëdhimbja.png", st.session_state.sq, tabs[1])
except Exception as e:
    st.error(f"Gabim: {e}")

# Butoni rrethor mavi (Gjithashtu i rregulluar)
st.markdown("""
    <button onclick="window.parent.scrollTo({top: 0, behavior: 'smooth'})" 
    style="position:fixed; bottom:30px; right:30px; background:#1E3A8A; color:white; width:50px; height:50px; border-radius:50%; border:none; cursor:pointer; z-index:1000; font-size:25px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">▲</button>
""", unsafe_allow_html=True)
