"""Excel kaynağından tek dosyalık HTML raporu üretir.
Kullanım:  npm install  &&  pip install pandas openpyxl  &&  python build/make.py
"""
import base64, json
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
d = pd.read_excel(root/'kaynak'/'Servis_Performans_Eslesenler_YEDEK_PARCA_ADET.xlsx', header=2).iloc[:-1]  # son satır not satırı
st = d.drop_duplicates('Stok Kodu')[['Stok Kodu','Stok Adı','Model Listesi']]
stoklar = [{'kod':a,'ad':b,'model':c} for a,b,c in st.itertuples(index=False)]
idx = {s['kod']:i for i,s in enumerate(stoklar)}
rows = [[r['Cari Kodu'],r['Cari İsim'],r['Şehir'],idx[r['Stok Kodu']],int(r['Adet']),int(r['Bekleyen'])] for _,r in d.iterrows()]
data = json.dumps({'stoklar':stoklar,'rows':rows}, ensure_ascii=False, separators=(',',':')).replace('</','<\\/')

def lib(p): return (root/'node_modules'/p).read_text(encoding='utf-8')
def b64(f): return 'data:image/jpeg;base64,'+base64.b64encode((root/'assets'/f).read_bytes()).decode()

t = (root/'build'/'template.html').read_text(encoding='utf-8')
out = (t.replace('__H2C__', lib('html2canvas/dist/html2canvas.min.js'))
        .replace('__JSZIP__', lib('jszip/dist/jszip.min.js'))
        .replace('__XLSX__', lib('xlsx/dist/xlsx.mini.min.js'))
        .replace('__LOGO_BAJAJ__', b64('bajaj_logo.jpg'))
        .replace('__LOGO_KURALKAN__', b64('kuralkan_logo.jpg'))
        .replace('__DATA__', data))
(root/'rapor'/'Yedek_Parca_Eksik_Stok_Raporu.html').write_text(out, encoding='utf-8')
print(len(rows), 'satır yazıldı')
