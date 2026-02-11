import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Parfüm Maliyet Uzmanı", page_icon="🧪", layout="wide")

# --- YAN MENÜ (AYARLAR) ---
with st.sidebar:
    st.header("⚙️ Üretim Ayarları")
    
    st.subheader("💲 Kur Bilgisi")
    dolar_kuru = st.number_input("Dolar Kuru (TL)", value=44.60, step=0.10, format="%.2f")
    
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
st.title("🧪 Parfüm Maliyet Hesaplayıcı v9.0")
st.write("Çok sayfalı Excel dosyalarınızı veya CSV'leri aşağıdaki alana bırakın.")

# DOSYA YÜKLEME ALANI
yuklenenler = st.file_uploader("Dosyaları Buraya Bırakın", type=['csv', 'xlsx'], accept_multiple_files=True)

if yuklenenler:
    df_list = []
    
    # Dosyaları Oku
    for dosya in yuklenenler:
        try:
            if dosya.name.endswith('.csv'):
                # CSV Dosyası Okuma
                df = pd.read_csv(dosya)
                df_list.append(df)
            else:
                # EXCEL İÇİN GÜNCELLEME: Tüm sayfaları oku (sheet_name=None)
                # Bu işlem {Sayfa1: Tablo1, Sayfa2: Tablo2} şeklinde bir sözlük döndürür
                excel_sozlugu = pd.read_excel(dosya, sheet_name=None, engine='openpyxl')
                
                # Sözlükteki tüm sayfaları listeye ekle
                for sayfa_adi, sayfa_tablosu in excel_sozlugu.items():
                    # İstersen hangi sayfadan geldiğini de ekleyebilirsin (Opsiyonel)
                    # sayfa_tablosu['KATEGORİ'] = sayfa_adi 
                    df_list.append(sayfa_tablosu)
            
        except Exception as e:
            st.error(f"{dosya.name} dosyası okunurken hata oluştu: {e}")

    if df_list:
        # Tüm dosyaları ve sayfaları alt alta birleştir
        ana_tablo = pd.concat(df_list, ignore_index=True)
        
        # Sütun isimlerindeki boşlukları temizle
        ana_tablo.columns = ana_tablo.columns.str.strip()
        
        # SENİN DOSYANDAKİ SÜTUNLAR
        kolon_marka = 'BRAND'
        kolon_tip = 'TYPE'
        kolon_fiyat = 'FOB PRICE(US$/KG)'
        
        # Kontrol Et: Bu sütunlar var mı?
        if kolon_marka in ana_tablo.columns and kolon_fiyat in ana_tablo.columns:
            
            # 1. Parfüm Tam Adını Oluştur
            ana_tablo['TAM_AD'] = ana_tablo[kolon_marka].astype(str) + " - " + ana_tablo[kolon_tip].astype(str)
            
            # 2. Fiyatı Sayıya Çevir (Hata önleyici temizlik)
            ana_tablo[kolon_fiyat] = ana_tablo[kolon_fiyat].astype(str).str.replace('$', '', regex=False)
            ana_tablo[kolon_fiyat] = ana_tablo[kolon_fiyat].str.replace(',', '.', regex=False)
            ana_tablo[kolon_fiyat] = pd.to_numeric(ana_tablo[kolon_fiyat], errors='coerce')
            
            # Fiyatı 0 veya boş olanları listeden çıkar
            ana_tablo = ana_tablo.dropna(subset=[kolon_fiyat])
            
            # --- ARAYÜZ ---
            st.markdown("---")
            
            # Alfabetik sıraya diz
            liste = sorted(ana_tablo['TAM_AD'].unique().tolist())
            
            # Kaç parfüm bulunduğunu göster
            st.success(f"✅ Toplam **{len(liste)}** adet parfüm başarıyla yüklendi.")
            
            secilen_urun = st.selectbox("Hangi parfümü üreteceksin?", liste)
            
            # Şişe Seçimi
            col1, col2 = st.columns([1, 2])
            with col1:
                sise_tipi = st.radio("Şişe Boyutu", ["10 ml (Tester)", "50 ml (Standart)"])
            
            # Seçime göre maliyetleri ayarla
            if "10 ml" in sise_tipi:
                sise_ml = 10.0
                sise_bos_maliyet = 15.0
            else:
                sise_ml = 50.0
                sise_bos_maliyet = 75.0
                
            # --- HESAPLAMA MOTORU ---
            
            # Seçilen parfümün verisini bul
            veri = ana_tablo[ana_tablo['TAM_AD'] == secilen_urun].iloc[0]
            dolar_kg_fiyati = veri[kolon_fiyat]
            
            # Gram Maliyetini Bul (Dolar -> TL)
            tl_kg_fiyati = dolar_kg_fiyati * dolar_kuru
            tl_gram_fiyati = tl_kg_fiyati / 1000
            
            # Reçete
            esans_ml = (sise_ml * esans_orani) / 100
            su_ml = (sise_ml * su_orani) / 100
            alkol_ml = sise_ml - esans_ml - su_ml
            
            # Maliyetler
            maliyet_esans = esans_ml * tl_gram_fiyati
            maliyet_alkol = (alkol_ml / 1000) * alkol_litre
            maliyet_su = (su_ml / 1000) * saf_su_litre
            maliyet_ambalaj = sise_bos_maliyet + kutu_maliyet + etiket_maliyet
            
            toplam_maliyet = maliyet_esans + maliyet_alkol + maliyet_su + maliyet_ambalaj
            
            # --- SONUÇ EKRANI ---
            st.markdown("---")
            st.subheader(f"📊 {secilen_urun}")
            st.caption(f"Hammadde: ${dolar_kg_fiyati} / KG  |  {tl_gram_fiyati:.2f} TL / Gram")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔸 Esans", f"{maliyet_esans:.2f} TL", f"{esans_ml} ml")
            c2.metric("🔹 Alkol", f"{maliyet_alkol:.2f} TL", f"{alkol_ml} ml")
            c3.metric("💧 Su", f"{maliyet_su:.2f} TL", f"{su_ml} ml")
            c4.metric("📦 Ambalaj", f"{maliyet_ambalaj:.2f} TL", "Şişe+Kutu+Etkt")
            
            st.success(f"💰 TOPLAM MALİYET: {toplam_maliyet:.2f} TL")
            st.info(f"🏷️ Tavsiye Satış (x3): {toplam_maliyet*3:.2f} TL")
            
        else:
            st.error("Dosyada 'BRAND' veya 'FOB PRICE(US$/KG)' sütunları bulunamadı.")
            st.write("Okunan Sütunlar:", ana_tablo.columns.tolist())

else:
    st.info("👆 Excel veya CSV dosyanızı yukarı sürükleyin.")
