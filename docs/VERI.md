# Veri sözleşmesi — ilk dilim

Kaynak: TCMB, TÜİK verilerinden yayımlanan tüketici fiyatları tablosu.
URL: https://tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Main%2BMenu/Istatistikler/Enflasyon%2BVerileri

## Alanlar
| Alan | Anlam |
|---|---|
| observation_period | Gözlemin referans ayı, YYYY-MM; yayım tarihi değildir |
| annual_pct | Kaynağın yayımladığı yıllık yüzde değişim; ilk modelin hedefi değil |
| monthly_pct | Kaynağın yayımladığı aylık yüzde değişim; hedef adayı |
| retrieved_at | Kaynağın gerçekten indirildiği, timezone içeren zaman; manifestte |
| source_sha256 | Kaydedilmiş UTF-8 HTML dosyasının byte özeti |
| vintage_status | latest-vintage-only; geçmiş veri sürümleri yok |
| released_at | Şimdilik bilinmiyor; observation_period veya retrieved_at ile doldurulmaz |

## Dikkat
Kaynakta görünen başlık 2025=100 iken HTML table summary değeri 2003=100 ifadesini taşıyor. Oranlar ayrı alanlar olarak alınır; bunlardan farklı baz yıllı endeks seviyeleri birleştirilmez. Kaynak etiketi uyuşmazlığı metadata incelemesi olarak açık tutulur.
Veri yalnız tamamlanmış aylardan mı oluşuyor sorusu takvimle ayrıca doğrulanmalı. Kesin yayım tarihleri henüz çıkarılmadı.
İndirme zamanı geçmiş tarihlerde erişilebilirliği kanıtlamaz. Snapshot model için gerçek zamanlı vintage kabul edilmez.
Eksik ay, tekrar ay, hatalı sayısal hücre ve sütun değişimi çıktı üretimini durdurur. Şok değerler sırf büyük diye silinmez.
Kaynak tabloda gözlenen tarih aralığı kalite raporundan okunur; veri görülmeden kapsam iddiası yazılmaz.
25 Ekim 2026'da kaynak koşulları doğrulandı. Atıflı, ticari olmayan araştırma paketi data/published/research-v1 altında yayımlanır; ayrıntı DATA-NOTICE.md. TCMB ticari kullanım için yazılı izin istiyor; genel açık veri lisansı verilmedi.
