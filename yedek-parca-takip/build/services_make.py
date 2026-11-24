"""services_version/index.html üretir: servis girişi (cari kodu + mail) ile yalnızca kendi PDF'i.
Kullanım: npm install && pip install pandas openpyxl cryptography && python build/services_make.py
Kaynaklar: kaynak/Servis_Performans_Eslesenler_YEDEK_PARCA_ADET.xlsx (veri), kaynak/kullanici_listesi.xlsx (cari kodu + mail listesi)
"""
import pandas as pd, json, re, os, base64, hashlib, unicodedata
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ProcessPoolExecutor
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
root=Path(__file__).resolve().parent.parent
USERS=root/'kaynak'/'kullanici_listesi.xlsx'
DATA=root/'kaynak'/'Servis_Performans_Eslesenler_YEDEK_PARCA_ADET.xlsx'
OUT=root.parent/'services_version'/'index.html'
IT=200000
B=lambda b:base64.b64encode(b).decode()

d=pd.read_excel(DATA,header=2).iloc[:-1]
now=datetime.now(ZoneInfo('Europe/Istanbul'))
fb=json.load(open(root/'kaynak'/'modeller.json',encoding='utf-8'))
def model(g):
    mv=g['Model Listesi'].dropna(); m=mv.iloc[0] if len(mv) else fb.get(g['Stok Kodu'].iloc[0])
    return ', '.join(x.strip() for x in str(m).split(',') if x.strip())
mod={k:model(g) for k,g in d.groupby('Stok Kodu',sort=False)}
eks=d[(d['Adet']==0)&(d['Bekleyen']==0)]
info={}
for _,r in d.iterrows(): info.setdefault(r['Cari Kodu'],(r['Cari İsim'],r['Şehir']))
parts={}
for _,r in eks.iterrows(): parts.setdefault(r['Cari Kodu'],[]).append([r['Stok Kodu'],r['Stok Adı'],mod[r['Stok Kodu']]])
for v in parts.values(): v.sort(key=lambda p:p[0])

u=pd.read_excel(USERS,header=2,usecols='B:G'); u=u[u['Cari Kodu'].notna()]
norm=lambda x:unicodedata.normalize('NFC',x).lower()
def mails(x): 
    out=[]
    for t in re.split(r'[;,\s]+',str(x)):
        t=t.strip().strip('.')
        if re.fullmatch(r'[^\s@;,]+@[^\s@;,]+\.[^\s@;,]+',t) and norm(t) not in out: out.append(norm(t))
    return out
G=os.urandom(12).hex()
def hid(c): return hashlib.sha256(('SYPTS|%s|%s'%(G,c)).encode()).hexdigest()[:16]

def build(job):
    cari,ml,payload=job
    salt=os.urandom(16); K=os.urandom(32); a=AESGCM(K)
    iv=os.urandom(12); p=B(iv+a.encrypt(iv,json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),None))
    w=[]
    for m in ml:
        wk=hashlib.pbkdf2_hmac('sha256',(cari+'|'+m).encode(),salt,IT,32); iv=os.urandom(12)
        w.append(B(iv+AESGCM(wk).encrypt(iv,K,None)))
    return cari,{'s':B(salt),'w':w,'p':p}

jobs=[];skipped=[]
tarih,tiso=now.strftime('%d.%m.%Y'),now.strftime('%Y-%m-%d')
for _,r in u.iterrows():
    c=str(r['Cari Kodu']).strip().upper(); ml=mails(r['Email'])
    if not ml: skipped.append(c); continue
    ad,il=info.get(c,(r['Bayi Adı'],r['Şehir']))
    jobs.append((c,ml,{'ad':str(ad),'il':str(il),'kod':c,'tarih':tarih,'tarihIso':tiso,'parts':parts.get(c,[])}))
if __name__=='__main__':
    with ProcessPoolExecutor() as ex: res=dict(ex.map(build,jobs,chunksize=20))
    db={'g':G,'it':IT,'u':{hid(c):v for c,v in res.items()}}
    t=open(root/'build'/'services_template.html',encoding='utf-8').read()
    m=open(root/'build'/'template.html',encoding='utf-8').read()
    css='\n'.join(l for l in m.splitlines() if re.match(r'\.sheet[ .]',l))
    sh=m[m.index('/* Kayıpsız'):m.index('let busy=false;')]
    H=lambda p:open(root/'node_modules'/p,encoding='utf-8').read()
    def b64f(f): return 'data:image/jpeg;base64,'+B(open(root/'assets'/f,'rb').read())
    def face(w,sub,rng):
        f=B(open(root/'node_modules'/'@fontsource'/'inter'/'files'/f'inter-{sub}-{w}-normal.woff2','rb').read())
        return "@font-face{font-family:'Inter';font-style:normal;font-weight:%s;font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}"%(w,f,rng)
    LAT='U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
    EXT='U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'
    fonts='\n'.join(face(w,'latin',LAT)+'\n'+face(w,'latin-ext',EXT) for w in (400,500,600,700))
    out=(t.replace('__FONTS__',fonts).replace('__SHEETCSS__',css).replace('__SHAREDJS__',sh)
          .replace('__LOGO_KURALKAN__',b64f('kuralkan_logo.jpg')).replace('__LOGO_BAJAJ__',b64f('bajaj_logo.jpg'))
          .replace('__H2C__',H('html2canvas/dist/html2canvas.min.js')).replace('__DB__',json.dumps(db,separators=(',',':'))))
    OUT.parent.mkdir(exist_ok=True); open(OUT,'w',encoding='utf-8').write(out)
    print('kullanıcı:',len(res),'mailsiz atlanan:',skipped,'eksikli cari:',len(parts),'boyut:',len(out))
