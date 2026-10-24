# Ürün vizyonu — 25 Ekim 2026

## Değer önerisi
Türkiye enflasyon görünümünü, tahmin hatalarını ve belirsizliği izlenebilir biçimde açıklayan araştırma aracı. Sadece tek sayı üretmek yerine analistin hangi verinin ne zaman bilindiğini ve tahminin nerede zayıfladığını anlamasını sağlar.

## İlk kullanıcı ve iş akışı
Birincil kullanıcı hipotezi: aylık ekonomi notu hazırlayan ekonomist/veri analisti.
Akış: veri açıklaması → kaynak/kalite kontrolü → tahmin ve benchmark karşılaştırması → belirsizlik/hata notu → dışa aktarılabilir analiz.
İlk karar ihtiyacı: mevcut tahmin yöntemi basit yönteme göre yeterince fayda sağlıyor mu; hangi dönemlerde güven azaltılmalı?
Gerçek kullanıcı görüşmesi henüz yapılmadı; ürün-pazar uyumu iddiası yok.

## Entegrasyon hipotezleri
| Alan | Sunulacak çıktı | Gerekli ek kanıt / sınır |
|---|---|---|
| Ekonomi araştırması | Aylık kısa not, kaynak künyesi, tahmin/hata grafiği | Analistin rapor ihtiyacı ve kullanım testi |
| Şirket bütçeleme / FP&A | Farklı enflasyon senaryolarıyla gider duyarlılığı | Kurumun gider sepeti, uygun ufuk ve gerçekleşen bütçe hatası; TÜFE kurum maliyetiyle aynı değildir |
| Satın alma planlama | İlgili alt endekslerle fiyat riski senaryoları | Ürün/tedarikçi maliyet verisi; manşet TÜFE doğrudan sipariş/fiyat önerisine çevrilemez |
| BI / yönetim raporu | Kaynak tarihi ve sürümünü taşıyan CSV/rapor | Veri sözleşmesi, güncellik/SLA ve gerçek tüketici kabulü |
| Araştırma eğitimi | Tekrar üretilebilir deney ve yöntem notu | Veri sürümü, kod/ortam ve yöntem sınırları |

Bunlar planlanan kullanım alanlarıdır; hazır entegrasyon değildir. Önce CSV/araştırma raporu; gerçek tüketici ihtiyacı varsa daha sonra API. Canlı dış sistemlere bağlantı ayrı kapsamdır.

## İlk sürüm sınırı
Tek ülke, aylık TÜFE yüzde değişimi, bir sonraki açıklama. Önce gecikmeli hedef seriyle basit yöntemler; sonra ekonomik gerekçeli az sayıda özellik. Üç aylık/bir yıllık bütçe senaryosu için ufuk ve aylık bileşik dönüşüm ayrıca gerekir; tek aylık tahmin yıllık beklenti diye etiketlenmez.

## Başarı
Araştırma: veri sızması olmayan, benchmark'lı ve tekrar üretilebilir değerlendirme.
Ürün: bir analistin kaynak/sonuç/sınırı yardımsız okuyabildiğinin gözlenmesi; henüz ölçülmedi.
Performans: önceden seçilen hata ölçütünde eşleşen origin'lerde karşılaştırma; başarı eşiği sonuç görüldükten sonra değiştirilmez.
Karmaşık modelin kaybetmesi geçerli sonuçtur. Nedensel politika etkisi ve tahmin ilişkisi ayrı tutulur.

## Çalışma düzeni
Kullanıcı öncelik, kullanım alanı ve kabul kararlarına odaklanır. Asistan ekonomi metodolojisi, kaynak araştırması, uygulama ve testleri yürütür; kullanıcı teknik tarafı da izler.
Her dilim: iş ihtiyacı → ekonomik gerekçe → kod ve kabul kanıtı → sınırlılık → sonraki karar.
