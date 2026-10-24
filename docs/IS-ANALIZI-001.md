# İş analizi notu — ilk referans tahminler

25 Ekim 2026

## Karar
Ürünü tek bir tahmin skoruyla tanımlamamalıyız. Ekonomist için hem ortalama hata hem büyük hata ve dönem duyarlılığı görünür olmalı. İlk rapor ekranının bunları birlikte göstermesi öneriliyor; kullanıcı kabulü henüz yapılmadı.

## Elde edilen kanıt
Önceden belirlenen 2015–2023 geliştirme döneminde 108 aylık origin aynı üç yönteme uygulandı.
| Yöntem | MAE (yüzde puan) | RMSE (yüzde puan) |
|---|---:|---:|
| Son 12 ay ortalaması | 1,1692 | 2,0740 |
| Son ayın oranı | 1,2427 | 1,9463 |
| Geçen yıl aynı ay | 1,5235 | 2,7079 |

Son 12 ay ortalamasının geliştirme MAE'si son ay yönteminden yaklaşık %5,9 düşük. RMSE'de sıralama ters; büyük hataları daha fazla cezalandırınca son ay yöntemi daha iyi.
2020–2023 bölümünde MAE son ay için 1,6027, son 12 ay ortalaması için 1,7192. Bu dönem ayrımı önceden yazılmıştır; sonuçlara göre seçilmedi.
Bu karşılaştırmada istatistiksel anlamlılık testi yapılmadı ve gelecekte aynı sıralama garanti edilmiyor.

## Vizyona etkisi
- Ekonomi notu: ortalama skor yanında yakın dönem hata ve yöntem karşılaştırması sunulsun.
- Bütçe senaryosu: büyük hatalara duyarlılık ayrıca değerlendirilsin; headline CPI şirket gider sepetinin yerine konmasın.
- Yönetim raporu: tahminin yanında kaynak sürümü, değerlendirme dönemi, birim ve sınırlılık görünür olsun.
Bunlar ürün tasarım çıkarımlarıdır; gerçek kullanıcının faydası ölçülmedi.

## Kanıtın sınırı
Bu, güncel veri tablosuyla zaman sıralı geliştirme değerlendirmesi. Gerçek zamanlı/historical-vintage test değil.
2024–Eylül 2026 nihai dönemi skorlanmadı. Bu dilimde geleceğe dönük canlı tahmin verilmedi.
Bir resmî yayım örneği doğrulandı; tüm geçmişin takvimi tamamlanmadı.
Yeni veri, farklı bir ufuk veya şirket maliyetleri için ayrı tasarım gerekir.

## Teknik ilerleme
Veri ve protokol hash kontrolü; gelecekteki hedeflerin geçmiş tahmine girmemesi; nihai dönemin dışarıda tutulması; tekrar yazma reddi ve otomatik CSV/JSON/Markdown raporu eklendi.
19 yerel test başarılı. CI, API, dashboard ve kurum entegrasyonu yok.

## Sonraki karar
Küçük bir Ridge modeli bu referans hataları, aynı dönemlerde ve uygun iç zaman doğrulamasıyla aşabiliyor mu? Aşamayı bu soru üzerinden kabul edeceğiz; sırf karmaşıklık eklemek için yeni model seçmeyeceğiz.
