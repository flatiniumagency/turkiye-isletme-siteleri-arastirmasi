# Türkiye işletme siteleri araştırması — Ankara, İstanbul, İzmir (Ekim 2026)

Ankara, İstanbul ve İzmir'de OpenStreetMap'te web sitesi kayıtlı işletmelerin **937 ana sayfası**, aynı kod ve aynı ölçütlerle tarandı: tıklanır telefon, WhatsApp bağlantısı, işletme şeması (yapısal veri), H1, meta açıklama, Open Graph, site haritası, llms.txt, yapay zekâ botu engeli, HTTPS, mobil uyum ve yanıt süresi.

Hazırlayan: [Flatinium](https://flatinium.com) — Ankara merkezli SEO, yapay zekâ arama optimizasyonu (GEO) ve yazılım ajansı.

- Üç şehir karşılaştırması: https://flatinium.com/blog/ankara-istanbul-izmir-isletme-siteleri-arastirmasi-2026
- Ankara araştırması ve sektör kırılımı: https://flatinium.com/blog/ankara-isletme-siteleri-seo-arastirmasi-2026
- Kendi sitenizi aynı ölçütlerle kontrol edin (ücretsiz): https://flatinium.com/araclar/web-sitesi-kontrol

## Ana bulgular

| Ölçüt | Ankara (n=313) | İstanbul (n=416) | İzmir (n=208) |
|---|---|---|---|
| HTTPS ile açılıyor | %95 | %94 | %96 |
| Mobil uyum etiketi var | %97 | %97 | %96 |
| Meta açıklama yok | %35 | %31 | %38 |
| H1 başlığı yok | %42 | %47 | %44 |
| İşletme şeması (yapısal veri) yok | %63 | %62 | %69 |
| Open Graph yok | %41 | %42 | %41 |
| Telefon tıklanınca aranmıyor | %50 | %52 | %50 |
| WhatsApp bağlantısı yok | %76 | %65 | %68 |
| Site haritası yok | %37 | %36 | %38 |
| llms.txt var | %16 | %18 | %16 |
| Yapay zekâ botlarından birini engelliyor | %1 | %2 | %3 |
| Ana sayfa 3 sn üstünde yanıt veriyor | %10 | %7 | %7 |

%50 civarındaki bir oranın %95 güven aralığının yarı genişliği yaklaşık ±6 (Ankara), ±5 (İstanbul), ±7 (İzmir) puandır. Birkaç puanlık şehir farkları anlamlı fark olarak okunmamalıdır; belirgin tek fark WhatsApp bağlantısındadır.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `veri/uc-sehir-isletme-siteleri-2026-10.csv` | Üç şehir × beş segment (tümü, yeme-içme, hizmet, perakende/zanaat, büyük şirket/zincir) × 13 ölçüt, yüzde |
| `veri/ankara-isletme-siteleri-2026-10.csv` | Ankara özet tablosu (ilk yayın, 1 Ekim 2026) |
| `veri/ozet-2026-10.json` | Makine okunur özet: örneklem, açılmayan adresler, CMS dağılımı, segmentler |
| `kod/osm.py` | 1. adım — OpenStreetMap Overpass sorgusu, web sitesi kayıtlı işletmeler |
| `kod/tara.py` | 2. adım — ana sayfa, robots.txt, llms.txt ve sitemap.xml taraması |
| `kod/analiz.py` | 3. adım — süzgeç, segment eşlemesi ve toplu oranlar |

Site adları ve adresleri yayımlanmaz; depoda yalnızca toplu oranlar vardır.

## Yöntem

- **Kaynak:** OpenStreetMap, il sınırı (`admin_level=4`) içinde `website` etiketi taşıyan işletmeler (shop, office, craft, healthcare ve seçili amenity türleri).
- **Elenen:** sosyal medya ve pazaryeri adresleri; kamu (`.gov.tr`, `.bel.tr`, `.k12.tr`, `.edu.tr`, `.pol.tr`, `.tsk.tr`, `.org.tr`), siyasi parti, elçilik, hastane, dernek, dini kurum, eğitim ve araştırma kurumları, türü belirsiz kayıtlar.
- **Örneklem:** Ankara (439 adres) ve İzmir (293 adres) tamamen tarandı. İstanbul'da elemeden sonra kalan 2.502 adresten `random.Random(20261002)` ile 600 adres seçildi.
- **Analiz edilen:** HTTP 200 dönen ve ana sayfasında 30'dan fazla kelime olan siteler (Ankara 313, İstanbul 416, İzmir 208). Adreslerin %22–23'ü açılmadı.
- **İstemci:** `FlatiniumArastirma/1.0`, 6 eşzamanlı istek, 15 sn zaman aşımı, Türkiye'den tek deneme. Tarih: Ankara 1 Ekim 2026, İstanbul ve İzmir 2 Ekim 2026.

## Sınırlar

- Örneklem rastgele değildir; OpenStreetMap'e web sitesi girilmiş, görece kurumsal ve köklü işletmelere kayar. OSM doluluğu şehirden şehre değişir.
- Yalnızca ana sayfa ölçülmüştür. Yanıt süresi sunucu yanıtıdır, tarayıcıdaki yüklenme süresi değildir.
- Segmentler OSM etiketlerine dayanır; yanlış etiketlenmiş işletmeler yanlış segmente düşebilir. İzmir hizmet (n=27) ve büyük şirket (n=34) segmentleri küçüktür.

## Lisans ve atıf

| Ne | Nerede | Lisans |
|---|---|---|
| Ölçümler ve toplu tablolar | `veri/` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.tr) — `LICENSE-DATA` |
| Tarama ve analiz kodu | `kod/` | [MIT](LICENSE) |
| İşletme örneklemi | OpenStreetMap | © [OpenStreetMap katkıcıları](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) |

`veri/` klasöründe yalnızca toplu yüzdeler ve sayılar var. İşletme adı, adres, web sitesi, koordinat ya da OSM kimliği yok. Bu tablolar ODbL'de "Produced Work" sayılır; OSM için atıf yeterlidir. `kod/osm.py` çalıştırıldığında indirilen OpenStreetMap verisi ODbL 1.0'a tabidir.

**Atıf:** Işık, D. (2026). *Türkiye işletme siteleri araştırması — Ankara, İstanbul, İzmir (Ekim 2026).* Flatinium. https://flatinium.com/blog/ankara-istanbul-izmir-isletme-siteleri-arastirmasi-2026

Kısa biçim: *"Kaynak: Flatinium, Ankara–İstanbul–İzmir işletme siteleri taraması, Ekim 2026 (CC BY 4.0). İşletme listesi © OpenStreetMap katkıcıları."*

`CITATION.cff` dosyası GitHub'daki "Cite this repository" düğmesini besler. Ayrıntı: `NOTICE`.

---

## English summary

Open dataset: SEO and conversion signals on **937 business websites** in Ankara, Istanbul and İzmir (Türkiye), scanned with identical code in October 2026. Business list from OpenStreetMap. Key findings: about half of the sites have no click-to-call phone link, roughly two thirds lack LocalBusiness/Organization structured data, and 65–76% have no WhatsApp link. Fewer than 3% block AI crawlers. Data: CC BY 4.0. Code: MIT. Methodology and limitations above (in Turkish); full write-up at https://flatinium.com/blog/ankara-istanbul-izmir-isletme-siteleri-arastirmasi-2026

**License:** measurements in `veri/` CC BY 4.0 (`LICENSE-DATA`); code MIT (`LICENSE`); business sample © OpenStreetMap contributors, ODbL 1.0. The repository contains aggregate figures only (no names, URLs or coordinates). Citation: https://flatinium.com/en/turkey-business-websites-study-2026
