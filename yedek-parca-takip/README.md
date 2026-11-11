# Yedek Parça Takip Sistemi – Eksik Stok Raporu

Servis Performans "Eşleşenler" Excel dosyasından üretilen tek dosyalık HTML raporu.

- `index.html` (repo kökü) – canlı rapor sayfası (GitHub Pages), tarayıcıda da açılır, internet gerekmez
- **Genel Rapor:** Adet ve Bekleyen değeri 0 olan (eksik) satırlar, özetler, filtreler; Excel / PDF / HTML olarak kaydet
- **Eksik Alım Yapan Servisler:** Her servis için A4 dikey yazı (logolar, alım yapılmayan parçalar, uyumlu modeller, uyarı notu); PDF / JPG olarak kaydet
- `kaynak/` – Excel kaynak dosyası, `build/` – şablon ve üretim betiği, `assets/` – logolar

Yeniden üretmek için: `npm install`, `pip install pandas openpyxl`, `python build/make.py`.

> Repo private olmalı: bayi adları ve stok bilgileri içerir.
