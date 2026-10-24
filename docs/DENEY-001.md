# DENEY-001 — ilk referans tahmin karşılaştırması

Tasarım tarihi: 25 Ekim 2026. Protokol, gerçek veri üzerinde tahmin/metric hesaplanmadan önce configs/baseline-development-v1.json içine kaydedildi.
İlk protokol SHA-256: e518453d7575d74af556607b1b69819d3ac6aae7c07af034ebcddcb47953b57c

## İş kararı
Daha karmaşık modelin aşması gereken referans hata düzeyini belirlemek. Ekonomistin aylık raporuna hangi yöntem için hangi sınırların yazılması gerektiğini görmek.
Bu aşama şirket bütçeleme veya fiyatlama kararı için kabul değildir.

## Önceden belirlenen dönemler
- İlk tarihçe: 2005-01–2014-12 (120 ay).
- Geliştirme değerlendirmesi: 2015-01–2023-12 (108 origin).
- Ayrılan nihai dönem: 2024-01–2026-09 (33 ay); bu aşamada skorlanmadı.
- Alt dönemler: 2015–2019 ve 2020–2023. Bunlar önceden seçilmiş takvim parçalarıdır, istatistiksel olarak bulunmuş rejimler değildir.
- Her origin'de tarihçe genişler; yöntemlerin kullandığı gecikme pencereleri tanımları gereği sabittir.

## Hedef ve adaylar
Hedef: bir sonraki ayın manşet TÜFE aylık yüzde değişimi.
Birincil seçim ölçütü MAE; RMSE büyük hata duyarlılığı, bias tahmin eksi gerçekleşen ortalaması.
Adaylar: son ayın oranı; geçen yıl aynı ayın oranı; son 12 aylık oranların aritmetik ortalaması.
Son aday bir sonraki aylık oran için düzleştirme benchmark'ıdır; yıllık enflasyon hesabı değildir.
Üç yöntem, bir worker, sıfır hiperparametre araması; yeni bağımlılık yok.

## Bilgi ve veri sözleşmesi
Bu, güncel tablonun tarihsel değerleriyle latest-vintage pseudo-out-of-sample değerlendirmedir.
Önceki ayın TÜFE değerinin origin'de bilindiği varsayılır. Referans ayına bir yayım günü uydurulmaz.
Tek bültenin yayım zamanı doğrulandı; tarihsel takvim ve veri sürümleri tam değil. Bu nedenle gerçek zamanlı kabul iddiası yok.
Nihai dönem değerleri yüklenen CSV'de bulunur; geliştirme tahmin tarihçesine veya skor hesabına girmez. Erişim engeli veya kriptografik körleme kurulmadı.

## Sonuç ve sınırlılık
Sonuçlar elle düzenlenmez. Yeniden üretim komutu:
~~~text
python scripts/evaluate_baselines.py --snapshot data/processed/initial --contract configs/baseline-development-v1.json --output reports/runs/baseline-development-v1
~~~
Üretilmiş tablo, predictions.csv, metrics.json, report.md ve manifest.json aynı koşu klasöründe.
Aynı klasöre tekrar yazma reddedilir; yeni koşuda yeni klasör kullan.
Protokol, veri ve kod hash'leri kaydedilir. Şimdiki metrikler geliştirme kanıtıdır; final test sonucu veya anlamlı üstünlük değildir.
Hız ölçümü yalnız hesaplama süresidir; dosya yazımını ve kullanıcı iş akışını kapsamıyor.
