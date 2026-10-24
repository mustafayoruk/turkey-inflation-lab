# Ridge geliştirme deneyi

## Karar ve ekonomik gerekçe
Amaç: yalnız geçmiş aylık TÜFE ile düzenlileştirilmiş doğrusal bir modelin basit referanslara ek değer sağlayıp sağlamadığını değerlendirmek. Hedef bir sonraki aylık değişim, hata birimi yüzde puan. Lag katsayıları tahmin ilişkileridir; politika etkisi değildir.

## Sonuç öncesinde sabitlenen tasarım
- configs/ridge-development-v1.json SHA-256: 3ef4252494150e5fbe2fc8980a1a92ed4f6f628f5bdcbb94f908ac79383b44ac.
- İlk tarihçe 2005–2014; dış geliştirme origin'leri 2015–2023, 108 ay. 2024-01–2026-09 nihai dönem skorlanmaz.
- Özellikler son 12 aylık aylık TÜFE değişimi; özellik araması yok.
- Her dış origin'de yalnız önceki aylardan eğitim satırları kurulur. StandardScaler ve Ridge tek pipeline içindedir.
- Beş alpha: 0.1, 1, 10, 100, 1000. Üç genişleyen iç eğitim fold'u, her birinde takip eden 12 ay doğrulama. Başlangıçta 72/84/96 eğitim hedefi; toplam dış eğitim 108 hedef.
- İç fold boyunca model parametreleri sabittir. Her doğrulama ayının lag'leri, o ayın bir adım öncesinde gözlenen gerçekleşmelerden oluşturulur; 12 adım rekürsif tahmin yapılmaz. Bu, dıştaki aylık yeniden eğitim sıklığının birebir kopyası değildir; önceden belirlenmiş sınırlı tuning yaklaşımıdır.
- İç MAE ortalaması en düşük alpha; tam eşitlikte büyük alpha. Seçilen pipeline tüm dış eğitimde yeniden kurulur. Ridge kare kayıp optimizasyonu kullanır; MAE ile seçim yapmak mutlak kayıp regresyonu anlamına gelmez.
- İç/dış tüm ön işleme eğitim fold'una özeldir. Gap=0, yalnız geçmiş hedef lag'leri ve önceki ay verisinin bilindiği varsayımı nedeniyle seçilmiştir. Başka ufuk/veri için otomatik genellenmez.
- 108 × (5 × 3 + 1) = 1.728 fit; tek işçi/BLAS thread. Rastgele algoritma yok, SVD çözümü.

## Kanıt ve tekrar üretme
CSV, protokol ve manifest: data/published/research-v1/. Kaynak hash'i önceki deneyle aynıdır. Tahminler dört yöntem için eşleşen aylarda üretilir; final holdout'a göre özellik/parametre seçilmez. Sonuç tablosu README'dedir; sayıların asıl kaydı metrics.csv'dir.

## Bilimsel dayanak
[Hewamalage vd. (2023)](https://doi.org/10.1007/s10618-022-00894-5) operasyonel zamanlama ve benchmark değerlendirmesine; [REFORMS (2024)](https://doi.org/10.1126/sciadv.adk3452) raporlanabilirliğe dayanak olur. DNB 828/2025 farklı ülke/ufukta düzenlileştirilmiş modellerin karşılaştırılması için motivasyondur; Türkiye'de üstünlük kanıtı değildir. Uygulama API'leri: [Ridge](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.Ridge.html), [TimeSeriesSplit](https://scikit-learn.org/1.7/modules/generated/sklearn.model_selection.TimeSeriesSplit.html), [Pipeline ve sızıntı](https://scikit-learn.org/1.7/common_pitfalls.html). Tam kaynak okuma kapsamı becerinin sources.md dosyasında.

## Sınır ve sonraki kabul
Latest-vintage pseudo-out-of-sample değerlendirmesidir; tarihsel first-release veri ve yayım takvimi yok. Şirket bütçe yararı, istatistiksel üstünlük veya canlı tahmin kabulü göstermez. Bir sonraki araştırma tasarımı ekonomik ek değişkenlerin açıklanma tarihini ve erişilebilirliğini doğrulamalı; final dönem bir kez, model tasarımı dondurulduktan sonra açılmalı.
