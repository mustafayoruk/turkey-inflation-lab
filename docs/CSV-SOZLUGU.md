# CSV veri sözlüğü

Tüm dosyalar UTF-8, virgül ayırıcı, ondalık nokta kullanır. Kaynak/koşullar: kökteki DATA-NOTICE.md.

| Dosya | Alan | Açıklama |
|---|---|---|
| snapshot/cpi.csv | observation_period | YYYY-MM referans ayı; yayım zamanı değildir |
| snapshot/cpi.csv | annual_pct | Bir önceki yılın aynı ayına göre TÜFE değişimi, yüzde |
| snapshot/cpi.csv | monthly_pct | Önceki aya göre TÜFE değişimi, yüzde; model hedefi |
| results/predictions.csv | target_period | Tahmin edilen referans ayı |
| results/predictions.csv | origin_period | Bilindiği varsayılan son TÜFE referans ayı; gerçek açıklanma saati değildir |
| results/predictions.csv | method | naive / seasonal_naive / trailing_mean_12 / ridge |
| results/predictions.csv | actual, prediction | Gerçekleşen/tahmin edilen aylık değişim, yüzde |
| results/predictions.csv | error | prediction−actual, yüzde puan |
| results/metrics.csv | segment, method, n | Değerlendirme dönemi, yöntem, eşleşen ay sayısı |
| results/metrics.csv | mae, rmse, bias | Yüzde puan; bias tahmin−gerçekleşen ortalaması |
| results/tuning.csv | target_period, alpha | Dış origin hedef ayı ve denenen Ridge cezası |
| results/tuning.csv | inner_mae | Üç iç zaman fold'unda ortalama MAE, yüzde puan |
| results/tuning.csv | selected | En düşük iç MAE; tam eşitlikte büyük alpha seçilir |
| results/tuning.csv | training_targets | O origin'deki toplam eğitim hedefi sayısı; iç fold'lar daha küçüktür |

Dosya yolu kökü: `data/published/research-v1/`. checksums.json yayımlanan dosyaların SHA-256 kimliğini içerir. Yeni koşular farklı klasöre yazılır; CSV elle düzeltilmez.
