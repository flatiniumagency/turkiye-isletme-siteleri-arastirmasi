"""
Şehir işletme siteleri taraması — 2. adım: siteleri aynı ölçütlerle tara.
Ankara betiğinin (olcum/ankara-tarama/tara.py) şehir parametreli kopyası. Eleme, ölçütler,
User-Agent, zaman aşımı (15 sn) ve eşzamanlılık (6) birebir aynı. Ankara taramasında elle
yapılan llms.txt doğrulama geçişi (llms_gercek) de aynı koduyla buraya eklendi.
Tek fark: elemeden sonra ORNEK_UST (600) alan adından fazlası kalırsa sabit tohumla
(TOHUM=20261002) tekrarlanabilir rastgele örneklem alınır; değilse hepsi taranır.
Kullanım: python olcum/sehir-tarama/tara.py İstanbul   (çıktı: veri/<sehir>-tarama.json)
Site adları yayınlanmaz; yalnızca toplu oranlar (bkz. strateji/arastirma-uc-sehir-2026-10.md).
"""
import json,re,ssl,urllib.request,urllib.parse,concurrent.futures as cf,html,time,sys,os,random
SEHIR=sys.argv[1]
ANAHTAR={'Ankara':'ankara','İstanbul':'istanbul','İzmir':'izmir'}[SEHIR]
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'veri')
ORNEK_UST=600; TOHUM=20261002
siteler=json.load(open(S+'/'+ANAHTAR+'-siteler.json',encoding='utf-8'))
HARIC_TUR={'political_party','diplomatic','government','hospital','embassy','yes','ngo','association','religion','educational_institution','research'}
siteler=[s for s in siteler if s['tur'] not in HARIC_TUR and not s['alan'].endswith(('.k12.tr','.bel.tr','.gov.tr','.edu.tr','.pol.tr','.tsk.tr','.org.tr'))]
uygun=len(siteler)
if uygun>ORNEK_UST:
    siteler=random.Random(TOHUM).sample(sorted(siteler,key=lambda s:s['alan']),ORNEK_UST)
print(SEHIR,'elemeden sonra',uygun,'alan adı → taranacak',len(siteler),flush=True)
UA='Mozilla/5.0 (compatible; FlatiniumArastirma/1.0; +https://flatinium.com/ucretsiz-seo-analizi)'
ctx=ssl.create_default_context()
AI=['GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','PerplexityBot','Google-Extended','CCBot']
def getir(u,limit=1_500_000):
    r=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'text/html,*/*'})
    with urllib.request.urlopen(r,timeout=15,context=ctx) as y:
        return y.status,y.geturl(),y.read(limit).decode('utf-8','replace'),dict(y.headers)
def robots_engel(txt):
    gruplar={}; ua=[]; son_ua=False
    for l in txt.splitlines():
        l=l.split('#')[0].strip()
        if ':' not in l: continue
        k,v=[x.strip() for x in l.split(':',1)]; k=k.lower()
        if k=='user-agent':
            if not son_ua: ua=[]
            ua.append(v.lower()); son_ua=True
        else:
            son_ua=False
            for a in ua: gruplar.setdefault(a,[]).append((k,v))
    def engelli(bot):
        kurallar=gruplar.get(bot.lower(),gruplar.get('*',[]))
        return any(k=='disallow' and v=='/' for k,v in kurallar)
    return {b:engelli(b) for b in AI}
def tara(s):
    o={'alan':s['alan'],'tur':s['tur']}
    try:
        t0=time.time(); st,son,h,bas=getir('https://'+s['alan']+'/'); o['sure']=round(time.time()-t0,2)
    except Exception:
        try: t0=time.time(); st,son,h,bas=getir('http://'+s['alan']+'/'); o['sure']=round(time.time()-t0,2)
        except Exception as e: o['hata']=type(e).__name__; return o
    o['durum']=st; o['https']=son.startswith('https://'); o['boyut_kb']=round(len(h)/1024)
    hl=h.lower()
    o['viewport']='name="viewport"' in hl or "name='viewport'" in hl
    m=re.search(r'<title[^>]*>(.*?)</title>',h,re.S|re.I); t=html.unescape(m.group(1)).strip() if m else ''
    o['title_uzunluk']=len(t)
    o['description']=bool(re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'][^"\']{20,}',h,re.I))
    o['h1_sayisi']=len(re.findall(r'<h1[\s>]',hl))
    jl=re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',h,re.S|re.I)
    o['jsonld']=bool(jl)
    tipler=' '.join(re.findall(r'"@type"\s*:\s*"?\[?"?([A-Za-z]+)',' '.join(jl)))
    o['isletme_semasi']=bool(re.search(r'LocalBusiness|Organization|Restaurant|Dentist|Store|MedicalBusiness|LegalService|ProfessionalService|RealEstateAgent|Corporation|Physician|Cafe',tipler))
    o['og']='property="og:title"' in hl or "property='og:title'" in hl
    o['tel_link']='href="tel:' in hl or "href='tel:" in hl
    o['whatsapp']='wa.me/' in hl or 'api.whatsapp.com' in hl
    duz=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S|re.I); duz=re.sub(r'<[^>]+>',' ',duz)
    o['kelime']=len(html.unescape(duz).split())
    o['cms']='wordpress' if 'wp-content' in hl else 'wix' if 'wix.com' in hl or '_wixcss' in hl else 'shopify' if 'cdn.shopify' in hl else 'ideasoft' if 'ideasoft' in hl else 'ticimax' if 'ticimax' in hl else 'diğer'
    kok=('https://' if o['https'] else 'http://')+s['alan']
    try: _,_,rb,_=getir(kok+'/robots.txt',200_000); o['robots']=True; o['ai_engel']=robots_engel(rb); o['sitemap_robots']='sitemap:' in rb.lower()
    except Exception: o['robots']=False; o['ai_engel']={}
    try: st2,son2,lt,hd=getir(kok+'/llms.txt',100_000); o['llms']=st2==200 and '<html' not in lt.lower()[:500] and len(lt)>20
    except Exception: o['llms']=False
    try: st3,_,sm,_=getir(kok+'/sitemap.xml',300_000); o['sitemap']=st3==200 and ('<urlset' in sm or '<sitemapindex' in sm)
    except Exception: o['sitemap']=False
    return o
sonuc=[]
with cf.ThreadPoolExecutor(6) as ex:
    for i,o in enumerate(ex.map(tara,siteler)):
        sonuc.append(o)
        if i%50==0: print(i,flush=True)
# llms.txt doğrulama geçişi (Ankara'da tarama sonrası uygulanan kodun aynısı)
def llms(o):
    if not o.get('llms'): return False
    u=('https://' if o.get('https') else 'http://')+o['alan']+'/llms.txt'
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=10,context=ctx)
        t=r.read(3000).decode('utf-8','replace').lstrip('﻿ \r\n\t'); ct=r.headers.get('content-type','').lower()
        return 'text/plain' in ct and not t.startswith('<')
    except Exception: return False
with cf.ThreadPoolExecutor(8) as ex: dog=list(ex.map(llms,sonuc))
for o,v in zip(sonuc,dog): o['llms_gercek']=v
json.dump(sonuc,open(S+'/'+ANAHTAR+'-tarama.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump({'sehir':SEHIR,'elemeden_sonra':uygun,'taranan':len(sonuc),'ornekleme':uygun>ORNEK_UST,'tohum':TOHUM,'tarih':time.strftime('%Y-%m-%d')},open(S+'/'+ANAHTAR+'-tarama-meta.json','w',encoding='utf-8'),ensure_ascii=False)
print('bitti',len(sonuc),'erişilemeyen',sum(1 for o in sonuc if 'hata' in o))
