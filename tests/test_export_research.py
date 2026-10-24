import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from test_evaluate_baselines import TMP, contract, snapshot
from export_research import export


class ExportTests(unittest.TestCase):
    def test_export_preserves_bytes_and_refuses_overwrite_or_bad_provenance(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            root=Path(tmp)
            p=contract()
            source,path=snapshot(root,p)
            (source/'quality.json').write_text('{}')
            run=root/'run'
            run.mkdir()
            (run/'protocol.json').write_bytes(path.read_bytes())
            manifest={'source_csv_sha256':p['expected_csv_sha256'],
                      'protocol_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                      'holdout_scored':False}
            for name in ['predictions.csv','metrics.csv','tuning.csv']:
                (run/name).write_text('synthetic\n')
            (run/'manifest.json').write_text(json.dumps(manifest))
            out=root/'published'
            export(source,run,out)
            self.assertEqual((out/'snapshot/cpi.csv').read_bytes(),(source/'cpi.csv').read_bytes())
            sums=json.loads((out/'checksums.json').read_text())
            self.assertEqual(sums['snapshot/cpi.csv'],p['expected_csv_sha256'])
            with self.assertRaises(FileExistsError): export(source,run,out)
            manifest['holdout_scored']=True
            (run/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(ValueError): export(source,run,root/'bad')
            self.assertFalse((root/'bad').exists())
