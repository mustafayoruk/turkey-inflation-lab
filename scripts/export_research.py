"""Export a fresh, attributed research bundle without changing generated files."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from evaluate_baselines import load_snapshot, read_limited, validate_protocol


def export(snapshot, run, output):
    protocol=json.loads(read_limited(run/'protocol.json'))
    validate_protocol(protocol)
    _, source=load_snapshot(snapshot,protocol)
    manifest=json.loads(read_limited(run/'manifest.json'))
    if (manifest['source_csv_sha256'] != source['cpi_sha256']
            or manifest['protocol_sha256'] != hashlib.sha256((run/'protocol.json').read_bytes()).hexdigest()
            or manifest['holdout_scored'] is not False):
        raise ValueError('Run and source provenance do not match.')
    files={'snapshot/cpi.csv':snapshot/'cpi.csv',
           'snapshot/manifest.json':snapshot/'manifest.json',
           'snapshot/quality.json':snapshot/'quality.json',
           'snapshot/source.html':snapshot/'source.html',
           **{f'results/{name}':run/name for name in
              ['predictions.csv','metrics.csv','tuning.csv','protocol.json','manifest.json']}}
    digests={name:hashlib.sha256(read_limited(path)).hexdigest() for name,path in files.items()}
    output.mkdir(parents=True,exist_ok=False)
    for name,path in files.items():
        target=output/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    (output/'checksums.json').write_text(json.dumps(digests,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    export(a.snapshot,a.run,a.output)
