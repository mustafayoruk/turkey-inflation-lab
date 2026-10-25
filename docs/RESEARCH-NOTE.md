# Ridge neden MAE'de iyileşirken büyük hatalarda geride kalıyor?

25 Ekim 2026. Bu not, önceden hesaplanmış 2015–2023 geliştirme tahminlerinin sonuç sonrası betimsel incelemesidir. Yeni model seçilmedi; nihai test dönemi kullanılmadı.

## Bulgudan karara
Ridge genel MAE'yi son 12 ay ortalamasına göre %2,5 azaltıyor. Buna karşılık RMSE'si 2,2001; son ay yönteminin RMSE'si 1,9463. Bir ekonomistin ortalama ay hatasıyla, bütçe hazırlayan bir ekibin büyük sapma riski aynı öncelik olmayabilir. Bu yüzden yöntem seçimini tek bir genel skorla kapatmak uygun görünmüyor.

Ridge 108 ayın 65'inde son ay yönteminden daha küçük mutlak hata veriyor. Bu, genel RMSE'de kaybetmesiyle çelişmiyor: RMSE, az sayıdaki büyük hatayı kareleri üzerinden daha fazla ağırlıklandırıyor. Bu sayım bir anlamlılık testi değildir; aylık hatalar bağımsız kabul edilmedi.

## Hatalar nerede yoğunlaşıyor?
Ridge'in en büyük üç mutlak hatası, toplam karesel hatasının **%57,04'ünü** oluşturuyor. Bu oran model performansının bu üç ay çıkarılarak yeniden sunulması için kullanılmıyor; tüm aylar skorda kalıyor.

| Hedef ay | Aylık TÜFE (%) | Ridge tahmini (%) | Tahmin−gerçekleşen (yüzde puan) |
|---|---:|---:|---:|
| Aralık 2021 | 13,58 | 1,01 | −12,57 |
| Ocak 2022 | 11,10 | 2,04 | −9,06 |
| Temmuz 2023 | 9,49 | 1,87 | −7,62 |

![Gerçekleşme ve tahminler](../reports/figures/development-v1/forecast-path.svg)

Grafikte yalnız geçmiş aylık TÜFE'ye dayalı Ridge'in ani artışların öncesinde düşük tahmin ürettiği görülüyor. Son ay yöntemi de dönüşleri gecikmeyle izliyor; grafikteki her ay, önceki gerçekleşmenin sonraki ayın tahminine taşınmasıyla oluşuyor.

Hatalar yalnız aşağı yönde değil: Aralık 2022'de Ridge 7,46 tahmin ederken gerçekleşme 1,18; hata +6,28 yüzde puan. Bu örnek, genel negatif bias'ın her ay düşük tahmin anlamına gelmediğini gösteriyor.

## Ekonomik yorumun sınırı
Gözlenen sonuç, geçmiş TÜFE bilgisinin bu sıçramaları karşılamadığıdır. Kur hareketleri, maliyetler, beklentiler, fiyat ayarlama takvimi veya ilişkinin zaman içinde değişmesi araştırılabilecek açıklamalardır. Bu veri seti bunlardan hangisinin hatayı yarattığını ayırt etmiyor. Ridge cezasının etkisini de bu sonuçlardan tek başına teşhis edemeyiz.

2015–2019 ve 2020–2023 önceden belirlenmiş takvim bölmeleridir; burada nedensel bir ekonomik rejim testi yapılmadı. Sonradan bulunan hata ayları hipotez üretmek içindir; yeni yöntemleri bu aylara uyarlayarak başarı iddiası kurulmamalı.

![Dönem ve ölçüt karşılaştırması](../reports/figures/development-v1/period-errors.svg)

## Bir sonraki ekonomik araştırma
Önce birkaç ek değişkenin hangi tarihte bilinebildiğini belgelemek gerekiyor. Kur, üretici fiyatları ve beklenti serileri bu nedenle adaydır; bu not eklenmeleri halinde performansın artacağını kanıtlamaz. Yeni özellik ve değerlendirme tasarımı sonuç görülmeden yazılmalı, nihai dönem bu tasarım tamamlanana kadar kapalı tutulmalıdır.

İlk kullanım alanı bir analistin aylık ekonomi notudur. Şirket bütçesine geçiş için şirketin maliyet sepeti, planlama ufku ve büyük hataların maliyeti ayrıca tanımlanmalıdır. Manşet TÜFE tahmini doğrudan satın alma fiyatı önerisi değildir.

## Hesaplama izi
Kaynak: TÜİK, TCMB üzerinden alınan snapshot; kullanım koşulları DATA-NOTICE.md. Sayılar [yayımlanmış tahmin CSV'sinden](../data/published/research-v1/results/predictions.csv) ve [ölçüm CSV'sinden](../data/published/research-v1/results/metrics.csv) gelir. Tam sayısal hata kaydı [diagnostics.json](../reports/figures/development-v1/diagnostics.json), kod `scripts/plot_diagnostics.py`. Kaynak/protokol sınırlılıkları DENEY-002.md ve VERI.md'dedir. Bu inceleme canlı tahmin ya da kurumsal fayda kabulü değildir.
