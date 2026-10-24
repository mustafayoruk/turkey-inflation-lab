import ast
import base64
import gzip
import hashlib
import json
import unittest
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_notebook import ROOT, FUNCTIONS, build, code_from


class NotebookTests(unittest.TestCase):
    def test_embedded_source_matches_canonical_functions(self):
        for name,names in FUNCTIONS.items():
            original={node.name:ast.dump(node) for node in ast.parse((ROOT/'scripts'/name).read_text(encoding='utf-8')).body
                      if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names}
            embedded={node.name:ast.dump(node) for node in ast.parse(code_from(name)).body
                      if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
            self.assertEqual(original,embedded)
            self.assertEqual(set(embedded),names)

    def test_self_contained_assets_preserve_hashes(self):
        notebook=build()
        self.assertIn('Copyright (c) 2026 Mustafa Yörük',notebook['cells'][-1]['source'])
        cell=notebook['cells'][3]['source']
        assignment=next(node for node in ast.parse(cell).body if isinstance(node,ast.Assign)
                        and node.targets[0].id=='BUNDLE_B64')
        assets=json.loads(gzip.decompress(base64.b64decode(ast.literal_eval(assignment.value))))
        for name,encoded in assets.items():
            original=(ROOT/'data/published/research-v1'/name).read_bytes()
            self.assertEqual(base64.b64decode(encoded),original)
        for source in notebook['cells']:
            if source['cell_type']=='code': compile(source['source'],'<notebook>','exec')
        self.assertEqual(notebook['metadata']['source_sha256']['evaluate_ridge.py'],
                         hashlib.sha256((ROOT/'scripts/evaluate_ridge.py').read_bytes()).hexdigest())
