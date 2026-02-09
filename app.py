import streamlit as st

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Profesyonel Parfüm Laboratuvarı", page_icon="🧪", layout="centered")

# --- YAN MENÜ (Maliyet Ayarları) ---
with st.sidebar:
    st.header("⚙️ Maliyet ve Oran Ayarları")
    st.info("Fiyatlar değişirse buradan güncelleyebilirsin.")
    
    esans_paket_gr = st.number_input("Esans Paket Gramajı (gr)", value=25.0)
    alkol_litre_fiyat = st.number_input("Alkol Litre Fiyatı (TL)", value=250.0)
    saf_su_litre_fiyat = st.number_input("Saf Su Litre Fiyatı (TL)", value=10.0) # Su ucuzdur ama ekleyelim
    sise_maliyet = st.number_input("Boş Şişe + Kutu Maliyeti (TL)", value=75.0)
    
    st.divider()
    su_orani = st.slider("Karışımdaki Su Oranı (%)", 0, 10, 5) # Varsayılan %5

# --- VERİ TABANI (İsim Odaklı) ---
# "Parfüm Adı": {"kod": "Uxxx", "fiyat": Paket Fiyatı (TL), "oran": Esans Oranı (%)}
parfumler = {
    "Guerlain - Neroli Oudrenoir": {"kod": "U345", "fiyat": 839.36, "oran": 25},
    "Initio - Narcotic Delight": {"kod": "U344", "fiyat": 500.44, "oran": 25},
    "Creed - Delphinus": {"kod": "U343", "fiyat": 532.12, "oran": 25},
    "Clive Christian - Matsukita": {"kod": "U342", "fiyat": 807.69, "oran": 30},
    "Afnan - 9pm Rebel": {"kod": "U341", "fiyat": 383.03, "oran": 20},
    "Tiziana Terenzi - Kirke Overdose": {"kod": "U340", "fiyat": 545.08, "oran": 25},
    "Essential Parfums - Bois Imperial": {"kod": "FR19", "fiyat": 630.86, "oran": 20},
    "Nishane - Shem": {"kod": "FR9", "fiyat": 814.07, "oran": 25},
    "Nishane - Hundred Silent Ways": {"kod": "FR8", "fiyat": 844.74, "oran": 25},
    "By Kilian - Angel's Share": {"kod": "U306", "fiyat": 423.47, "oran": 25},
    "Tom Ford - Oud Wood": {"kod": "U190", "fiyat": 194.35, "oran": 22},
    "Parfums De Marly - Layton": {"kod": "U133", "fiyat": 191.15, "oran": 22},
    "MFK - Baccarat Rouge 540 Extrait": {"kod": "U70", "fiyat": 191.50, "oran": 25},
    "Jo Malone - Wood Sage & Sea Salt": {"kod": "U56", "fiyat": 183.98, "oran": 18},
    "Creed - Aventus (Muadil)": {"kod": "U100", "fiyat": 250.00, "oran": 25} 
}

# --- ANA EKRAN TASARIMI ---
st.title("🧪 Parfüm Laboratuvarı")
st.write("Profesyonel üretim reçetesi ve maliyet hesaplayıcı.")

# 1. Parfüm Seçimi (İsim Listesi)
secilen_isim = st.selectbox("Hangi parfümü üreteceksin?", list(parfumler.keys()))
p = parfumler[secilen_isim]

# Seçilen parfümün detaylarını göster
st.caption(f"📌 Kod: {p['kod']} | Önerilen Esans: %{p['oran']} | Paket Fiyatı: {p['fiyat']} TL")

# 2. Şişe Boyutu
sise_ml = st.slider("Hedeflenen Şişe Boyutu (ml)", min_value=10, max_value=100, value=50, step=5)

# --- HESAPLAMA MOTORU ---
if st.button("REÇETEYİ OLUŞTUR", type="primary"):
    
    # A. Miktar Hesaplamaları
    esans_ml = (sise_ml * p["oran"]) / 100
    su_ml = (sise_ml * su_orani) / 100
    alkol_ml = sise_ml - (esans_ml + su_ml)
    
    # B. Maliyet Hesaplamaları
    # Esans maliyeti: (Gereken ML * Paket Fiyatı) / Paket Gramajı
    esans_maliyeti = esans_ml * (p["fiyat"] / esans_paket_gr)
    
    # Alkol maliyeti: (Gereken ML / 1000) * Litre Fiyatı
    alkol_maliyeti = (alkol_ml / 1000) * alkol_litre_fiyat
    
    # Su maliyeti
    su_maliyeti = (su_ml / 1000) * saf_su_litre_fiyat
    
    # Toplam
    toplam_maliyet = esans_maliyeti + alkol_maliyeti + su_maliyeti + sise_maliyet

    # --- SONUÇ EKRANI ---
    st.markdown("---")
    st.subheader(f"🧴 {secilen_isim} - {sise_ml} ml Reçetesi")
    
    # Sonuçları 4 kolon halinde göster
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔸 Esans", f"{esans_ml:.1f} ml", f"{esans_maliyeti:.1f} TL")
    with col2:
        st.metric("🔹 Saf Su", f"{su_ml:.1f} ml", f"%{su_orani}")
    with col3:
        st.metric("💧 Alkol", f"{alkol_ml:.1f} ml", f"{alkol_maliyeti:.1f} TL")
    with col4:
        st.metric("📦 Şişe", "1 Adet", f"{sise_maliyet} TL")
    
    # Büyük Toplam
    st.success(f"💰 **TOPLAM MALİYET: {toplam_maliyet:.2f} TL**")
    
    # Kar Analizi (Opsiyonel Bilgi)
    tavsiye_satis = toplam_maliyet * 3  # Örnek: Maliyetin 3 katı
    st.info(f"💡 Tavsiye: Bu ürünü en az **{tavsiye_satis:.0f} TL**'ye satmalısın. (x3 Marj)")
