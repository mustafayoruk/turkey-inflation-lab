# İlerleme ve kabul

25 Ekim 2026 — veri, baseline ve Ridge geliştirme değerlendirmesi tamamlandı; GitHub yayın paketi hazırlandı.

| İş | Durum | Kabul kanıtı |
|---|---|---|
| Yerel proje ve sohbet bağlantısı | Tamamlandı | Kullanıcı arayüzü/screenshot doğrulaması; çalışma kökü turkey-inflation-lab |
| Yerel Git başlangıcı | Tamamlandı | main; ilk yayın hazırlığı |
| Vizyon ve entegrasyon hipotezleri | Taslak hazır | VIZYON.md; gerçek kurum/kullanıcı kabulü yok |
| inflation-research becerisi | Oluşturuldu ve uygulanıyor | Proje beceri kataloğunda; AGENTS.md yönlendirmesi |
| Beceri yapısal kontrolü | Önceki dilimde başarılı | skill-creator quick_validate.py; izole PyYAML 6.0.3 |
| İlk TCMB snapshot | Başarılı | 261 gözlem, 2005-01–2026-09; eksik/tekrar ay 0 |
| İlk yayım örneği | Kısmen doğrulandı | Eylül 2026 bülteni: 5 Ekim 2026 10:00; sonraki tarih 3 Kasım 2026; YAYIM-TAKVIMI.md |
| Tarihsel takvim/vintage | Açık | Tek örnek tüm geçmişe genellenmedi; latest-vintage-only |
| Metadata/baz yılı tutarlılığı | Açık | Haber bülteni ve metadata/HTML etiketleri farklı; endeks seviyeleri birleştirilmedi |
| Deney protokolü | Sonuçlar hesaplanmadan yazıldı | configs/baseline-development-v1.json; SHA e518453d...953b57c |
| İlk baseline karşılaştırması | Başarılı, geliştirme kanıtı | 108 ay × 3 yöntem = 324 tahmin; koşu reports/runs/baseline-development-v1 |
| Nihai dönem | Ayrıldı, skorlanmadı | 2024-01–2026-09; 33 ay; holdout_scored=false |
| Kod kontrolleri | Başarılı | unittest 25/25; veri, baseline, Ridge ve dışa aktarma kontrolleri |
| Ridge | Geliştirme tamamlandı | 108 origin, 1.728 fit; genel MAE 1,1397; DENEY-002.md |
| Dashboard/API/CI/gerçek kurum kabulü | Başlanmadı | Yerel araştırma kanıtı, yayın kabulü değil |
| Veri yeniden dağıtım koşulları | Atıflı araştırma kapsamında doğrulandı | DATA-NOTICE.md; TCMB ticari kullanım için yazılı izin istiyor |
| CSV araştırma paketi | Hazır | data/published/research-v1; 261 gözlem, 432 tahmin, 12 ölçüm, 540 tuning kaydı; SHA-256 listesi |
| Lisans | Hazır | Orijinal kod/belgeler MIT; üçüncü taraf veri ayrı koşullarda |

## İş açısından sonuç
2015–2023 genel MAE: son 12 ay ortalaması 1,1692; son ay 1,2427; geçen yıl aynı ay 1,5235 yüzde puan.
RMSE ölçütünde son ay yöntemi 1,9463 ile son 12 ay ortalamasından (2,0740) daha düşük.
2020–2023 bölümünde son ay yöntemi MAE 1,6027; son 12 ay ortalaması 1,7192. Tek genel skor, her döneme ve her hata maliyetine uygun yöntem demek değil.
Bunlar geliştirme sonuçları; anlamlı üstünlük, gerçek zamanlı başarı veya şirket bütçe faydası iddiası yok.

## Bilimsel ve teknik sınır
Yalnız hedef serinin geçmiş değerleri kullanıldı; önceki ayın yayımlanmış olduğu varsayımı açık. Tarihsel first-release vintage kullanılmadı.
Nihai dönem CSV'de bulunur, fakat geliştirme tahmin tarihçesine ve skoruna girmez; kriptografik körleme yok.
Şok/negatif aylık oranlar silinmedi. Alt dönemler önceden belirlenmiş takvim parçalarıdır.
Testlerde gelecekteki/hedefteki/holdout'taki değerleri değiştirmenin önceki tahminleri etkilemediği kontrol edildi.
Ölçümler, protokol/veri/kod hash'leri ve ortam bilgisi koşu manifestinde. Hesaplama zamanı dosya yazımı dahil olmayan yerel süre; hız optimizasyonu iddiası yok.

## Ridge sonrası iş kararı
Ridge genel MAE'de 12 aylık ortalamaya göre yaklaşık %2,5 daha düşük hata verdi; RMSE 2,2001 ve bias −0,4880. 2020–2023 MAE'si 1,7227; son ay yöntemi 1,6027. Bu kanıtla otomatik bütçe entegrasyonu veya canlı model üstünlüğü kabul edilmedi. Önce kırılma dönemlerinde yetersiz kalan bilgi setini incelemek gerekiyor.

## Sıradaki kabul
Kur, üretici fiyatları ve beklenti gibi az sayıda ekonomik aday için yayım takvimi, veri sürümü ve kullanım koşulları sözleşmesi. Sonraki deney sonuç görülmeden sabitlenecek; final holdout model tasarımı dondurulmadan açılmayacak. Analistin kullanabileceği rapor biçimi ayrı kullanıcı kabulü gerektirir.
