import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Parfüm Maliyet Uzmanı", page_icon="🧪", layout="wide")

# --- YAN MENÜ (AYARLAR) ---
with st.sidebar:
    st.header("⚙️ Üretim Ayarları")
    
    st.subheader("💲 Kur Bilgisi")
    dolar_kuru = st.number_input("Dolar Kuru (TL)", value=43.64, step=0.10, format="%.2f")
    
    st.divider()
    
    st.subheader("📦 Sabit Giderler")
    kutu_maliyet = st.number_input("Kutu Maliyeti (TL)", value=15.0)
    etiket_maliyet = st.number_input("Etiket Maliyeti (TL)", value=2.0)
    
    st.divider()
    
    st.subheader("🛢️ Hammadde")
    alkol_litre = st.number_input("Alkol Litre (TL)", value=250.0)
    saf_su_litre = st.number_input("Saf Su Litre (TL)", value=10.0)
    
    st.divider()
    
    st.subheader("⚗️ Oranlar")
    esans_orani = st.slider("Esans Oranı (%)", 10, 40, 25)
    su_orani = st.slider("Su Oranı (%)", 0, 10, 5)

# --- ANA EKRAN ---
st.title("🧪 Parfüm Maliyet Hesaplayıcı v8.0")
st.write("Excel (.xlsx) veya CSV dosyalarınızı aşağıdaki alana sürükleyin.")

# DOSYA YÜKLEME ALANI
yuklenenler = st.file_uploader("Dosyaları Buraya Bırakın", type=['csv', 'xlsx'], accept_multiple_files=True)

if yuklenenler:
    df_list = []
    
    for dosya in yuklenenler:
        try:
            if dosya.name.endswith('.csv'):
                df = pd.read_csv(dosya)
            else:
                df = pd.read_excel(dosya, engine='openpyxl')
            df_list.append(df)
        except Exception as e:
            st.error(f"{dosya.name} dosyası okunurken hata oluştu: {e}")

    if df_list:
        ana_tablo = pd.concat(df_list, ignore_index=True)
        ana_tablo.columns = ana_tablo.columns.str.strip()
        
        kolon_marka = 'BRAND'
        kolon_tip = 'TYPE'
        kolon_fiyat = 'FOB PRICE(US$/KG)'
        
        if kolon_marka in ana_tablo.columns and kolon_fiyat in ana_tablo.columns:
            ana_tablo['TAM_AD'] = ana_tablo[kolon_marka].astype(str) + " - " + ana_tablo[kolon_tip].astype(str)
            ana_tablo[kolon_fiyat] = ana_tablo[kolon_fiyat].astype(str).str.replace('$', '', regex=False)
            ana_tablo[kolon_fiyat] = ana_tablo[kolon_fiyat].str.replace(',', '.', regex=False)
            ana_tablo[kolon_fiyat] = pd.to_numeric(ana_tablo[kolon_fiyat], errors='coerce')
            ana_tablo = ana_tablo.dropna(subset=[kolon_fiyat])
            
            st.markdown("---")
            liste = sorted(ana_tablo['TAM_AD'].unique().tolist())
            secilen_urun = st.selectbox("Hangi parfümü üreteceksin?", liste)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                sise_tipi = st.radio("Şişe Boyutu", ["10 ml (Tester)", "50 ml (Standart)"])
            
            if "10 ml" in sise_tipi:
                sise_ml, sise_bos_maliyet = 10.0, 15.0
            else:
                sise_ml, sise_bos_maliyet = 50.0, 75.0
                
            veri = ana_tablo[ana_tablo['TAM_AD'] == secilen_urun].iloc[0]
            dolar_kg_fiyati = veri[kolon_fiyat]
            tl_gram_fiyati = (dolar_kg_fiyati * dolar_kuru) / 1000
            
            esans_ml = (sise_ml * esans_orani) / 100
            su_ml = (sise_ml * su_orani) / 100
            alkol_ml = sise_ml - esans_ml - su_ml
            
            maliyet_esans = esans_ml * tl_gram_fiyati
            maliyet_alkol = (alkol_ml / 1000) * alkol_litre
            maliyet_su = (su_ml / 1000) * saf_su_litre
            maliyet_ambalaj = sise_bos_maliyet + kutu_maliyet + etiket_maliyet
            
            toplam_maliyet = maliyet_esans + maliyet_alkol + maliyet_su + maliyet_ambalaj
            
            st.markdown("---")
            st.subheader(f"📊 {secilen_urun}")
            st.caption(f"Hammadde: ${dolar_kg_fiyati} / KG  |  {tl_gram_fiyati:.2f} TL / Gram")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔸 Esans", f"{maliyet_esans:.2f} TL", f"{esans_ml} ml")
            c2.metric("🔹 Alkol", f"{maliyet_alkol:.2f} TL", f"{alkol_ml} ml")
            c3.metric("💧 Su", f"{maliyet_su:.2f} TL", f"{su_ml} ml")
            c4.metric("📦 Ambalaj", f"{maliyet_ambalaj:.2f} TL", "Kutu+Etkt")
            
            st.success(f"💰 TOPLAM MALİYET: {toplam_maliyet:.2f} TL")
            st.info(f"🏷️ Tavsiye Satış (x3): {toplam_maliyet*3:.2f} TL")
            
        else:
            st.error("Dosya formatı uygun değil. BRAND ve FOB PRICE sütunları bulunamadı.")
