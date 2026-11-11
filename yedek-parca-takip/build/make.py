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
def face(w, sub, rng):
    f = base64.b64encode((root/'node_modules'/'@fontsource'/'inter'/'files'/f'inter-{sub}-{w}-normal.woff2').read_bytes()).decode()
    return ("@font-face{font-family:'Inter';font-style:normal;font-weight:%s;font-display:block;"
            "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}") % (w, f, rng)
LAT = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'
fonts = '\n'.join(face(w,'latin',LAT)+'\n'+face(w,'latin-ext',EXT) for w in (400,500,600,700))

t = (root/'build'/'template.html').read_text(encoding='utf-8').replace('__FONTS__', fonts)
out = (t.replace('__H2C__', lib('html2canvas/dist/html2canvas.min.js'))
        .replace('__JSZIP__', lib('jszip/dist/jszip.min.js'))
        .replace('__XLSX__', lib('xlsx/dist/xlsx.mini.min.js'))
        .replace('__LOGO_BAJAJ__', b64('bajaj_logo.jpg'))
        .replace('__LOGO_KURALKAN__', b64('kuralkan_logo.jpg'))
        .replace('__DATA__', data))
(root.parent/'index.html').write_text(out, encoding='utf-8')  # canlı sayfa (GitHub Pages kökü)
print(len(rows), 'satır yazıldı')
