# Yayım zamanı ve kaynak kontrolü — 25 Ekim 2026

## Doğrudan doğrulanan örnek
TÜİK Eylül 2026 bülteni tarayıcıda açıldı: referans dönemi Eylül; ekranda yayımlanma 5 Ekim 2026 saat 10:00, sonraki bülten tarihi 3 Kasım 2026 olarak görüldü.
Kaynak: https://veriportali.tuik.gov.tr/tr/press/58298
Bu tek örnek, 2005–2026 tarihsel yayım takviminin çıkarıldığı anlamına gelmez.

## Zamanlama riski
TÜİK'in 2 Ekim 2024 duyurusunda mevsim etkisinden arındırılmış göstergeler için ana TÜFE yayımından bir iş günü sonra saat 16:00 düzeni belirtiliyor.
Kaynak: https://www.tuik.gov.tr/media/announcements/Tufe_Mevsimsel_Tablo_TR.pdf
Bu duyuru farklı veri ailelerinin aynı anda bilinmediğini gösterir. Her tarihsel release için ayrı doğrulamanın yerini tutmaz.
İlk deney bu göstergeleri kullanmıyor; yalnız gecikmeli manşet aylık oran kullanılıyor.

## Metadata uyuşmazlığı
Eylül 2026 haber bülteni 2025=100 başlığı taşıyor; aynı sayfanın metaveri sekmesinde 2003=100 ve 2025 kapsam ifadeleri hâlâ görülebiliyor. TCMB HTML summary etiketiyle birlikte bu farklılık açık kaynak kalite notu olarak tutuldu.
Oran serileriyle çalışmak, baz/sınıflama/bağlama metodolojisinin tamamının doğrulandığı anlamına gelmez. Endeks düzeyleri birleştirilmedi.
Kaynak metaveri ekranı: https://veriportali.tuik.gov.tr/tr/press/58298/metadata

## Makinece okunabilir kayıt
data/catalog/release-evidence.json içinde kaynak, kontrol tarihi, gözlenen yayım bilgisi ve doğrulama kapsamı var. Yayım saati Türkiye yerel saati olarak yorumlanıyor; sayfa kendi timezone adını ayrıca göstermiyor.
