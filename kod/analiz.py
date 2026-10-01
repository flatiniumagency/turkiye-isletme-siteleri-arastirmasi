"""
Şehir taraması — 3. adım: toplu oranlar. Ankara olgu kartını üreten analiz kodunun aynısı
(süzgeç: HTTP 200 ve 30'dan fazla kelime; segment eşlemesi ve ölçüt tanımları birebir).
Kullanım: python olcum/sehir-tarama/analiz.py   (veri/<sehir>-tarama.json dosyalarını okur,
ozet-2026-10.json yazar, olgu kartı tablolarını ekrana basar)
"""
import json,os,collections,sys
K=os.path.dirname(os.path.abspath(__file__)); V=os.path.join(K,'veri')
SEG={'Yeme-içme':{'restaurant','cafe','fast_food','bar','bakery','pub','ice_cream','confectionery','pastry'},
'Hizmet (profesyonel + sağlık)':{'lawyer','estate_agent','accountant','tax_advisor','insurance','notary','architect','consulting','engineer','financial','travel_agent','employment_agency','advertising_agency','it','clinic','dentist','doctors','veterinary','pharmacy','physiotherapist','optician','medical','hearing_aids'}}
BUYUK={'supermarket','mall','department_store','company','telecommunication','energy_supplier','car'}
def seg(o):
    for k,v in SEG.items():
        if o['tur'] in v: return k
    return 'Büyük şirket / zincir' if o['tur'] in BUYUK else 'Perakende ve zanaat'
OL=[('HTTPS ile açılıyor',lambda o:o['https']),('Mobil uyum etiketi var',lambda o:o['viewport']),('Meta açıklama yok',lambda o:not o['description']),('H1 başlığı yok',lambda o:o['h1_sayisi']==0),('Birden fazla H1',lambda o:o['h1_sayisi']>1),('İşletme şeması (yapısal veri) yok',lambda o:not o['isletme_semasi']),('Sosyal paylaşım önizlemesi (og) yok',lambda o:not o['og']),('Telefon tıklanınca aranmıyor',lambda o:not o['tel_link']),('WhatsApp bağlantısı yok',lambda o:not o['whatsapp']),('Site haritası yok',lambda o:not o['sitemap']),('llms.txt var',lambda o:o['llms_gercek']),('Yapay zekâ botlarından birini engelliyor',lambda o:any(o.get('ai_engel',{}).values())),('Ana sayfa 3 sn üstünde yanıt veriyor',lambda o:o['sure']>3)]
gr=['Tümü','Yeme-içme','Hizmet (profesyonel + sağlık)','Perakende ve zanaat','Büyük şirket / zincir']
ozet={}
for ad,an in [('Ankara','ankara'),('İstanbul','istanbul'),('İzmir','izmir')]:
    f=os.path.join(V,an+'-tarama.json')
    if not os.path.exists(f): print(ad,'veri yok'); continue
    d=json.load(open(f,encoding='utf-8'))
    ok=[o for o in d if 'hata' not in o and o.get('durum')==200 and o.get('kelime',0)>30]
    for o in ok: o['seg']=seg(o)
    hata=collections.Counter(o.get('hata') for o in d if 'hata' in o)
    cms=collections.Counter(o['cms'] for o in ok)
    llms_t=sum(1 for o in ok if o['llms_gercek']); wp_llms=sum(1 for o in ok if o['llms_gercek'] and o['cms']=='wordpress')
    sehir={'taranan':len(d),'acilmayan':sum(hata.values()),'acilmayan_yuzde':round(100*sum(hata.values())/len(d)),'hata_turleri':dict(hata),
           'analiz_edilen':len(ok),'cms':dict(cms),'llms_var':llms_t,'llms_wordpress':wp_llms,
           'sure_medyan_sn':sorted(o['sure'] for o in ok)[len(ok)//2],
           'okul_turu_perakende_icinde':sum(1 for o in ok if o['tur']=='school'),
           'tur_ilk15':collections.Counter(o['tur'] for o in ok).most_common(15),'segmentler':{}}
    print(f'\n### {ad}  taranan={len(d)} açılmayan={sum(hata.values())} (%{sehir["acilmayan_yuzde"]}) {dict(hata)} analiz={len(ok)}')
    satir=['| Ölçüt | '+' | '.join(f'{g} (n={len(ok) if g=="Tümü" else sum(1 for o in ok if o["seg"]==g)})' for g in gr)+' |','|'+'---|'*(len(gr)+1)]
    for g in gr:
        L=ok if g=='Tümü' else [o for o in ok if o['seg']==g]
        sehir['segmentler'][g]={'n':len(L),'olcutler':{a:(round(100*sum(1 for o in L if fn(o))/len(L)) if L else None) for a,fn in OL}}
    for a,fn in OL:
        satir.append(f'| {a} | '+' | '.join(f"%{sehir['segmentler'][g]['olcutler'][a]}" if sehir['segmentler'][g]['n'] else '-' for g in gr)+' |')
    print('\n'.join(satir))
    print('cms',dict(cms),'llms',llms_t,'wp',wp_llms,'medyan',sehir['sure_medyan_sn'],'okul',sehir['okul_turu_perakende_icinde'])
    ozet[ad]=sehir
meta={an:json.load(open(os.path.join(V,an+'-osm-meta.json'),encoding='utf-8')) for an in ['istanbul','izmir'] if os.path.exists(os.path.join(V,an+'-osm-meta.json'))}
tm={an:json.load(open(os.path.join(V,an+'-tarama-meta.json'),encoding='utf-8')) for an in ['istanbul','izmir'] if os.path.exists(os.path.join(V,an+'-tarama-meta.json'))}
for ad,an in [('İstanbul','istanbul'),('İzmir','izmir')]:
    if ad in ozet: ozet[ad]['osm']=meta.get(an); ozet[ad]['ornekleme']=tm.get(an)
if 'Ankara' in ozet: ozet['Ankara']['osm']={'osm_oge':885,'tekil_alan':666,'not':'Ankara olgu kartından'}; ozet['Ankara']['ornekleme']={'ornekleme':False,'not':'tümü tarandı (1 Ekim 2026)'}
cikti={'aciklama':'Ankara, İstanbul, İzmir işletme siteleri taraması (Ekim 2026). Yüzdeler tam sayı, her segmentin analiz edilen siteleri içinde. Site adları yer almaz. Kaynak: strateji/arastirma-uc-sehir-2026-10.md','sehirler':ozet}
if '--yaz' in sys.argv: json.dump(cikti,open(os.path.join(K,'ozet-2026-10.json'),'w',encoding='utf-8',newline='\n'),ensure_ascii=False,indent=1); print('ozet yazıldı')
