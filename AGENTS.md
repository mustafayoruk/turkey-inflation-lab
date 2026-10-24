# Turkey Inflation Lab çalışma ilkeleri

## Amaç ve raporlama
Kullanıcı iş analisti odağında ilerlemek istiyor. Türkçe raporla: karar/değer, ekonomik gerekçe, teknik kanıt, açık risk ve sıradaki kabul. Teknik ayrıntıyı görünür tut; kod ayrıntısının ürün vizyonunu bastırmasına izin verme.
Ekonomik değerlendirme ve yazılım geliştirmeyi birlikte yürüt; doğrulanmamış bir sonucu uzmanlık iddiasıyla güçlendirme.

## Projeye özel beceri
Veri, model, değerlendirme veya araştırma işinde önce .agents/skills/inflation-research/SKILL.md dosyasını oku. Yalnız gereken referansı yükle. Bu beceri bu proje içindir; başka projelerin ayarlarını değiştirme.
Güncel bilimsel kaynakları görevle ilgili olduğunda doğrula; her küçük kod değişikliğinde bütün literatürü tarama.

## Kapsam ve kanıt
İlk hedef bir sonraki açıklanacak aylık TÜFE değişimi. Vizyon: açıklanabilir araştırma ve karar desteği. Kamuya yayın, ücretli kaynak, gerçek kurum entegrasyonu veya finansal işlem bu yönergelerle yetkilendirilmez.
Private projelerin kodu/verisi bu repoya taşınmaz.
Ham veri, temiz veri, model ve rapor ayrı kalsın. Üretilmiş dosyaları elle düzeltme.
Test/yerel/CI/canlı kanıtını ayrı raporla. Henüz olmayan API, model veya müşteri kabulünü varmış gibi yazma.
Bir seriyle alınan sonucun tüm ekonomilere genellendiğini söyleme.

## Şimdiki komutlar
Python 3.12+; veri hazırlama adımı yalnız standart kütüphaneyi kullanır.
- python -m unittest discover -s tests -v
- python scripts/prepare_cpi.py --input data/raw/tcmb-cpi.html --retrieved-at <timezone içeren gerçek indirme zamanı> --output data/processed/<yeni snapshot klasörü>
Skill doğrulayıcı mevcutsa .agents/skills/inflation-research üzerinde quick_validate.py çalıştır.
Her tamamlanan dilimde docs/TAKIP.md içindeki kanıtları ve sonraki kabulü güncelle.
