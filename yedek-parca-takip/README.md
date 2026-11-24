# Yedek Parça Takip Sistemi – Eksik Stok Raporu

Servis Performans "Eşleşenler" Excel dosyasından üretilen tek dosyalık HTML raporu.

- `index.html` (repo kökü) – canlı rapor sayfası (GitHub Pages), tarayıcıda da açılır, internet gerekmez
- **Genel Rapor:** Adet ve Bekleyen değeri 0 olan (eksik) satırlar, özetler, filtreler; Excel / PDF / HTML olarak kaydet
- **Eksik Alım Yapan Servisler:** Her servis için A4 dikey yazı (logolar, alım yapılmayan parçalar, uyumlu modeller, uyarı notu); PDF / JPG olarak kaydet
- `kaynak/` – Excel kaynak dosyası, `build/` – şablon ve üretim betiği, `assets/` – logolar

Yeniden üretmek için: `npm install`, `pip install pandas openpyxl`, `python build/make.py`.

## Servis girişi (`services_version/`)

- Adres: `…github.io/YP-TAKIP-KDS-ILE-GELEN-1.SI/services_version/`
- Servis, cari kodu (MY otomatik) + Kuralkan'da tanımlı mail adresini girer; yalnızca kendi güncel "Alım Yapılmayan Yedek Parçalar Listesi" PDF'ini indirir.
- Servis verileri sayfaya şifreli gömülür (cari kodu + mail ile çözülür); başka servisin verisi görünmez.
- Kaynaklar: `kaynak/kullanici_listesi.xlsx` (cari kodu + mail listesi), `kaynak/Servis_Performans_Eslesenler_YEDEK_PARCA_ADET.xlsx` (veri).
- Üretim: `pip install cryptography` ardından `python build/services_make.py` (veri güncellenince hem `make.py` hem `services_make.py` çalıştırılır).

> Repo herkese açıktır; veriler gizli değildir (kullanıcı onayı).
