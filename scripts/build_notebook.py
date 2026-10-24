"""Generate a self-contained notebook from the canonical code and research bundle."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'notebooks/turkey_inflation_lab.ipynb'
FUNCTIONS = {
    'prepare_cpi.py': {'TableParser','parse_rate','parse_cpi'},
    'evaluate_baselines.py': {'month_number','validate_protocol','read_limited',
                             'load_snapshot','predict','walk_forward','summarize'},
    'evaluate_ridge.py': {'validate_model','supervised','estimator','forecast',
                         'ridge_walk_forward','write_csv'},
}


def code_from(name):
    source=(ROOT/'scripts'/name).read_text(encoding='utf-8')
    pieces=[]
    for node in ast.parse(source).body:
        if isinstance(node,ast.ImportFrom) and node.module in {'prepare_cpi','evaluate_baselines'}:
            continue
        if (isinstance(node,(ast.Import,ast.ImportFrom,ast.Assign))
                or isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in FUNCTIONS[name]):
            pieces.append(ast.get_source_segment(source,node))
    return '\n\n'.join(pieces)+'\n'


def build():
    cells=[]
    def cell(kind,source):
        item={'cell_type':kind,'id':f'cell-{len(cells):02d}','metadata':{},
              'source':source.strip()+'\n'}
        if kind=='code': item.update(execution_count=None,outputs=[])
        cells.append(item)
    cell('markdown', '''# Turkey Inflation Lab — tek dosyada araştırma

**Karar:** Geçmiş aylık TÜFE, bir sonraki açıklanacak aylık değişimi basit referanslardan daha iyi tahmin edebiliyor mu?

Bu dosya veri snapshot'ını, kaynak HTML'ini, deney protokolünü, hesaplama kodunu ve referans sonuçları içerir. Repo klonlama, Drive bağlama veya ayrıca CSV yükleme gerekmez. Colab'da **Runtime → Run all** ile sırayla çalıştırın; CPU yeterlidir. İlk hücre eksik/sürümü farklı paketleri kurabilir, bunun için internet gerekir. Python 3.12.14 ile yerelde doğrulandı; Colab hizmetinde canlı çalıştırma ayrıca doğrulanmalıdır.

**Hedef:** sonraki aylık TÜFE değişimi (%); hata birimi yüzde puan. İlk tarihçe 2005–2014, geliştirme 2015–2023 (108 ay). **2024-01–2026-09 nihai dönem skorlanmaz.** Güncel veri sürümüyle pseudo-out-of-sample değerlendirmesidir; tarihsel yayım/vintage bilgisi eksiktir. Önceki ayın verisinin bilindiği varsayılır.

Bu notebook scripts/build_notebook.py ile mevcut Python kaynaklarından üretilir. Kod değişikliğinde notebook'u elle değiştirmek yerine yeniden üretin. Kaynak kod ve notebook alternatif kullanım yollarıdır.''')
    requirements=(ROOT/'requirements.txt').read_text(encoding='utf-8-sig').splitlines()
    cell('code', '''import sys, subprocess, importlib.metadata
if sys.version_info < (3, 12):
    raise RuntimeError('Python 3.12+ seçin; yerel kabul Python 3.12.14 ile yapıldı.')
PINS = '''+repr(requirements)+'''
missing=[]
for pin in PINS:
    name,version=pin.split('==')
    try:
        installed=importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        installed=None
    if installed != version:
        missing.append(pin)
if missing:
    subprocess.check_call([sys.executable,'-m','pip','install',*PINS])
    # Yeni kurulumu önceden yüklenmiş numpy/sklearn ile karıştırmayın.
    if any(name in sys.modules for name in ['numpy','scipy','sklearn']):
        raise RuntimeError('Paketler güncellendi. Runtime → Restart session, sonra Run all yapın.')
print('Python:',sys.version.split()[0])
print('Paket sürümleri:', {p.split('==')[0]:importlib.metadata.version(p.split('==')[0]) for p in PINS})''')
    bundle=ROOT/'data/published/research-v1'
    assets={str(p.relative_to(bundle)).replace('\\','/'):base64.b64encode(p.read_bytes()).decode('ascii')
            for p in sorted(bundle.rglob('*')) if p.is_file()}
    payload=base64.b64encode(gzip.compress(json.dumps(assets).encode(),mtime=0)).decode()
    cell('markdown', '''## 1. Taşınabilir veri ve kaynak kontrolü
Sıkıştırılmış bölüm yalnız sabit araştırma dosyalarını taşır; internetten veri indirmez veya kod çalıştırmaz. Açılan CSV ve HTML dosyaları SHA-256 ile denetlenir. Her baştan çalıştırmada ayrı bir work/colab-runs klasörü oluşur. Nihai dönem CSV'de mevcuttur; körlenmiş değildir.''')
    cell('code', '''import base64, gzip, hashlib, json, tempfile
from pathlib import Path
BUNDLE_B64 = '''+repr(payload)+'''
base=Path.cwd()/'work'/'colab-runs'
base.mkdir(parents=True,exist_ok=True)
workspace=Path(tempfile.mkdtemp(prefix='inflation-',dir=base))
assets=json.loads(gzip.decompress(base64.b64decode(BUNDLE_B64)))
for name,encoded in assets.items():
    relative=Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Geçersiz dosya yolu')
    path=workspace/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(base64.b64decode(encoded))
checksums=json.loads((workspace/'checksums.json').read_text())
for name,expected in checksums.items():
    assert hashlib.sha256((workspace/name).read_bytes()).hexdigest()==expected,name
print('Doğrulanan paket dosyası:',len(checksums))''')
    cell('markdown','## 2. Veri okuma ve doğrulama kodu\nAşağıdaki fonksiyonlar mevcut veri hazırlama kodundan aynen alınır. Eksik/tekrar ay, bozuk oran ve belirsiz tablo kabul edilmez. Negatif aylık oranlar korunur.')
    cell('code',code_from('prepare_cpi.py'))
    cell('markdown','## 3. Referans yöntemler ve ölçüm\nSon ay, geçen yıl aynı ay ve son 12 ayın aritmetik ortalaması. MAE birincil ölçüt; RMSE büyük hataları, bias yönlü sapmayı gösterir. Yıllık enflasyon ile aylık oran ortalaması aynı kavram değildir.')
    cell('code',code_from('evaluate_baselines.py'))
    cell('code', '''protocol=json.loads((workspace/'results/protocol.json').read_text())
validate_protocol(protocol)
rows,source_manifest=load_snapshot(workspace/'snapshot',protocol)
parsed=parse_cpi((workspace/'snapshot/source.html').read_bytes().decode('utf-8-sig'))
assert len(parsed)==len(rows)==261
assert [r['observation_period'] for r in parsed]==[r['period'] for r in rows]
assert [float(r['monthly_pct']) for r in parsed]==[r['monthly_pct'] for r in rows]
print('Kaynak:',source_manifest['source_url'])
print('İndirme:',source_manifest['retrieved_at'])
print('Kapsam:',rows[0]['period'],rows[-1]['period'],'Gözlem:',len(rows))
print('Negatif aylık oran:',sum(r['monthly_pct']<0 for r in rows))
print('Tasarım:',protocol['evaluation_mode'],'Final dönem: skorlanmayacak')''')
    cell('markdown', '''## 4. Ridge — eğitim fold'una özel ön işleme
Son 12 aylık oran; alpha 0.1/1/10/100/1000; üç genişleyen iç zaman fold'u ve her birinde 12 doğrulama ayı. Ölçekleme yalnız eğitimde öğrenilir. İç fold boyunca parametreler sabittir; her doğrulama ayı bir-adım tahmini için önceki gerçekleşmeleri kullanır. Her dış ayda model yeniden eğitilir. Gap=0 önceki aylık verinin bilindiği varsayımına dayanır. 108 × (5 × 3 + 1) = 1.728 fit, tek thread. Ridge kare kayıp kullanır; seçim MAE ile yapılır. Katsayılar nedensel politika etkisi değildir.''')
    cell('code',code_from('evaluate_ridge.py'))
    cell('code', '''import time
started=time.perf_counter()
with threadpool_limits(limits=1):
    ridge_predictions,tuning=ridge_walk_forward(rows,protocol)
predictions=sorted(walk_forward(rows,protocol)+ridge_predictions,
                   key=lambda row:(row['target_period'],row['method']))
metrics=summarize(predictions,protocol['subperiods'],(*METHODS,'ridge'))
assert len(predictions)==432 and len(tuning)==540
assert max(r['target_period'] for r in predictions)=='2023-12'
print('Tahmin:',len(predictions),'Ridge fit:',len(ridge_predictions)*16)
print('Hesaplama süresi (yerel ortamınıza bağlı):',round(time.perf_counter()-started,3),'s')
for r in metrics:
    print(f"{r['segment']:16} {r['method']:18} n={r['n']:3} MAE={r['mae']:.4f} RMSE={r['rmse']:.4f} bias={r['bias']:.4f}")''')
    cell('markdown','## 5. Yayımlanan deneyle sonuç eşitliği\nAynı snapshot/protokol ve aynı hedef ayları karşılaştırılır. İşletim sistemi/BLAS farkları için 1e-10 sayısal tolerans kullanılır. Sadece eğitim/geliştirme çıktıları kontrol edilir; final holdout açılmaz.')
    cell('code', '''with (workspace/'results/predictions.csv').open(newline='',encoding='utf-8') as handle:
    reference=list(csv.DictReader(handle))
assert len(reference)==len(predictions)
for expected,actual in zip(reference,predictions):
    for key in ['target_period','origin_period','method']:
        assert expected[key]==actual[key],key
    for key in ['actual','prediction','error']:
        assert math.isclose(float(expected[key]),actual[key],rel_tol=1e-10,abs_tol=1e-10),key
print('432 tahmin yayımlanmış referansla eşleşti. Final holdout skorlanmadı.')''')
    cell('markdown', '''## 6. İş yorumu ve karar
Ridge genel geliştirme MAE'sinde küçük bir iyileşme verir; fakat 2020–2023'te son ay yöntemini geçemez ve genel RMSE/bias daha zayıftır. Bu sonuç canlı kullanım veya kurumsal bütçe entegrasyonu için yeterli kabul değildir. Sonraki araştırma kur/üretici fiyatı/beklenti gibi ekonomik girdilerin yayım tarihlerini doğrulamalıdır. Şirket gider sepeti ile manşet TÜFE ayrıdır; müşteri faydası henüz ölçülmedi.

## 7. CSV ve araştırma kaydı dışa aktarımı
Çıktılar yalnız bu çalıştırmanın klasörüne yazılır. Sonuç ZIP'inin yolu aşağıda görünür; Colab'ın soldaki Files panelinden indirilebilir. Drive erişimi veya GitHub yazma izni istenmez.''')
    cell('code', '''import platform, shutil
result_dir=Path(tempfile.mkdtemp(prefix='output-',dir=workspace))
write_csv(result_dir/'predictions.csv',predictions)
write_csv(result_dir/'metrics.csv',metrics)
write_csv(result_dir/'tuning.csv',tuning)
(result_dir/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
run_manifest={'holdout_scored':False,'evaluation_mode':protocol['evaluation_mode'],
              'source_csv_sha256':source_manifest['cpi_sha256'],
              'python_version':platform.python_version(),
              'dependencies':{p.split('==')[0]:importlib.metadata.version(p.split('==')[0]) for p in PINS},
              'generated_code_sha256':NOTEBOOK_CODE_SHA256}
(result_dir/'manifest.json').write_text(json.dumps(run_manifest,indent=2),encoding='utf-8')
archive=shutil.make_archive(str(result_dir),'zip',result_dir)
print('CSV/manifest ZIP:',Path(archive).relative_to(Path.cwd()))''')
    cell('markdown', (ROOT/'DATA-NOTICE.md').read_text(encoding='utf-8')+'\n\n## Kod lisansı ve yöntem kaynakları\nOrijinal kod/belgeler MIT; yukarıdaki üçüncü taraf veri kapsamı ayrıdır.\n\n'+(ROOT/'LICENSE').read_text(encoding='utf-8')+'''

Yöntem dayanağı: [Forecast evaluation (2023)](https://doi.org/10.1007/s10618-022-00894-5), [REFORMS (2024)](https://doi.org/10.1126/sciadv.adk3452); API: [scikit-learn 1.7](https://scikit-learn.org/1.7/). Ayrıntılı kaynak okuma kapsamı repodaki araştırma becerisinin sources.md dosyasındadır.

---
**Author:** [Mustafa YÖRÜK](https://github.com/mustafayoruk)  
*Statistics Student @ Hacettepe University*''')
    # Preserve the exact selected code used by the generated cells for run provenance.
    codes={name:hashlib.sha256(code_from(name).encode()).hexdigest() for name in FUNCTIONS}
    cells[1]['source']+='\nNOTEBOOK_CODE_SHA256 = '+repr(codes)+'\n'
    return {'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
             'language_info':{'name':'python','version':'3.12.14'},
             'colab':{'name':TARGET.name,'provenance':[]},
             'source_sha256':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in FUNCTIONS}},
            'nbformat':4,'nbformat_minor':5}


if __name__=='__main__':
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    TARGET.write_text(json.dumps(build(),ensure_ascii=False,indent=1)+'\n',encoding='utf-8',newline='\n')
    print(TARGET)
