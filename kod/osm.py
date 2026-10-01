"""
Şehir işletme siteleri taraması — 1. adım: OpenStreetMap'ten web sitesi kayıtlı işletmeler.
Ankara betiğinin (olcum/ankara-tarama/osm.py) şehir parametreli kopyası; sorgu, etiketler,
eleme listesi ve User-Agent birebir aynı. Yalnızca il adı değişir.
Kullanım: python olcum/sehir-tarama/osm.py İstanbul   (çıktı: olcum/sehir-tarama/veri/<sehir>-siteler.json)
Yöntem ve sonuçlar: strateji/arastirma-uc-sehir-2026-10.md
"""
import json,urllib.request,urllib.parse,collections,re,os,sys,time
SEHIR=sys.argv[1]
ANAHTAR={'Ankara':'ankara','İstanbul':'istanbul','İzmir':'izmir'}[SEHIR]
q='''[out:json][timeout:180];
area["name"="%s"]["admin_level"="4"]->.a;
(nwr["website"](area.a)["shop"];nwr["website"](area.a)["office"];nwr["website"](area.a)["amenity"~"restaurant|cafe|clinic|dentist|doctors|veterinary|pharmacy|school|kindergarten"];nwr["website"](area.a)["craft"];nwr["website"](area.a)["healthcare"];);
out tags;'''%SEHIR
SUNUCU=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.private.coffee/api/interpreter']
d=None
for deneme in range(6):
    u=SUNUCU[deneme%len(SUNUCU)]
    try:
        r=urllib.request.Request(u,urllib.parse.urlencode({'data':q}).encode(),{'User-Agent':'flatinium-arastirma/1.0 (info@flatinium.com)'})
        d=json.load(urllib.request.urlopen(r,timeout=200))
        if d.get('remark'): print('uyarı:',d['remark'])
        print('sunucu',u); break
    except Exception as e:
        print('deneme',deneme+1,u,type(e).__name__,e); time.sleep(30)
if d is None: sys.exit('Overpass yanıt vermedi')
kayit={}
for e in d['elements']:
    t=e.get('tags',{}); w=t.get('website','').strip()
    if not w: continue
    if not w.startswith('http'): w='http://'+w
    try: h=urllib.parse.urlparse(w).hostname.lower().removeprefix('www.')
    except Exception: continue
    if not h or any(x in h for x in ['facebook','instagram','google','wix.com','business.site','linktr','twitter','youtube','.gov.tr','.edu.tr','trendyol','hepsiburada','yemeksepeti','getir','sahibinden']): continue
    tur=t.get('shop') or t.get('office') or t.get('amenity') or t.get('craft') or t.get('healthcare')
    kayit.setdefault(h,{'alan':h,'url':w,'tur':tur})
print(len(d['elements']),'öğe →',len(kayit),'tekil alan adı')
print(collections.Counter(v['tur'] for v in kayit.values()).most_common(15))
V=os.path.join(os.path.dirname(os.path.abspath(__file__)),'veri'); os.makedirs(V,exist_ok=True)
json.dump(list(kayit.values()),open(os.path.join(V,ANAHTAR+'-siteler.json'),'w',encoding='utf-8'),ensure_ascii=False)
json.dump({'sehir':SEHIR,'osm_oge':len(d['elements']),'tekil_alan':len(kayit),'osm_zaman':d.get('osm3s',{}).get('timestamp_osm_base')},open(os.path.join(V,ANAHTAR+'-osm-meta.json'),'w',encoding='utf-8'),ensure_ascii=False)
