"""Validate notebook schema and run its pure-Python cells in a fresh namespace.

This is local sequential execution, not acceptance on Colab's hosted runtime.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path

import nbformat


def verify(path, output):
    notebook=nbformat.read(path,as_version=4)
    nbformat.validate(notebook)
    namespace={'__name__':'__notebook_verification__'}
    count=0
    for cell in notebook.cells:
        if cell.cell_type!='code': continue
        count+=1
        captured=io.StringIO()
        with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
            exec(compile(cell.source,f'<notebook:{cell.id}>','exec'),namespace)
        cell.execution_count=count
        cell.outputs=[nbformat.v4.new_output('stream',name='stdout',text=captured.getvalue())]
    assert len(namespace['predictions'])==432
    nbformat.validate(notebook)
    output.parent.mkdir(parents=True,exist_ok=True)
    nbformat.write(notebook,output)
    print(json.dumps({'code_cells_executed':count,'predictions_verified':432,
                      'holdout_scored':False,'executed_notebook':str(output)}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    verify(a.input,a.output)
