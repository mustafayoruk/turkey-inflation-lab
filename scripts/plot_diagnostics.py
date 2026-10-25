"""Describe published development errors without fitting or selecting new models."""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

def load_predictions(path):
    with path.open(newline='',encoding='utf-8') as handle:
        rows=list(csv.DictReader(handle))
    for row in rows:
        for key in ['actual','prediction','error']:
            row[key]=float(row[key])
            if not math.isfinite(row[key]): raise ValueError('Non-finite value')
        if not math.isclose(row['prediction']-row['actual'],row['error'],abs_tol=1e-12):
            raise ValueError('Inconsistent forecast error')
        if not '2015-01' <= row['target_period'] <= '2023-12':
            raise ValueError('This diagnostic slice excludes the final holdout')
    return rows


def describe(rows):
    ridge=sorted((r for r in rows if r['method']=='ridge'),
                 key=lambda r:abs(r['error']),reverse=True)
    naive={r['target_period']:r for r in rows if r['method']=='naive'}
    if len(ridge)!=108 or len(naive)!=108 or len({r['target_period'] for r in ridge})!=108:
        raise ValueError('Expected 108 paired development origins')
    if set(naive)!={r['target_period'] for r in ridge}:
        raise ValueError('Origins do not match')
    squared=math.fsum(r['error']**2 for r in ridge)
    return {'n':len(ridge), 'largest_errors':ridge[:8],
            'top3_squared_error_share':math.fsum(r['error']**2 for r in ridge[:3])/squared,
            'ridge_lower_absolute_error_months':sum(abs(r['error'])<abs(naive[r['target_period']]['error']) for r in ridge),
            'analysis_status':'post-hoc descriptive development diagnostics; no new model selection',
            'holdout_scored':False}


def plot(input_dir,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    rows=load_predictions(input_dir/'predictions.csv')
    diagnostic=describe(rows)
    with (input_dir/'metrics.csv').open(newline='',encoding='utf-8') as handle:
        metrics=list(csv.DictReader(handle))
    output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'axes.titleweight':'bold','svg.fonttype':'none'})
    colors={'ridge':'#146EAF','naive':'#9B6844','trailing_mean_12':'#4B8171'}
    labels={'ridge':'Ridge','naive':'Last month','trailing_mean_12':'12-month mean'}
    chronological=sorted((r for r in rows if r['method']=='ridge'),key=lambda r:r['target_period'])
    dates=[datetime.strptime(r['target_period'],'%Y-%m') for r in chronological]
    fig,ax=plt.subplots(figsize=(11,4.6),layout='constrained')
    ax.plot(dates,[r['actual'] for r in chronological],color='#202B34',label='Observed CPI',linewidth=1.8)
    for method in ['ridge','naive']:
        series=sorted((r for r in rows if r['method']==method),key=lambda r:r['target_period'])
        ax.plot(dates,[r['prediction'] for r in series],label=labels[method],color=colors[method],
                linewidth=1.4,linestyle='-' if method=='ridge' else '--',alpha=.9)
    ax.axhline(0,color='#ADB5BD',linewidth=.7)
    for row,offset in zip(diagnostic['largest_errors'][:3],[(0,18),(25,5),(0,22)]):
        date=datetime.strptime(row['target_period'],'%Y-%m')
        ax.annotate(row['target_period'],(date,row['actual']),xytext=offset,
                    textcoords='offset points',ha='center',fontsize=9,
                    arrowprops={'arrowstyle':'-','color':'#555555'})
    ax.set(title='Monthly CPI: abrupt rises exceed lag-only forecasts',ylabel='Monthly change (%)',
           xlabel='Target month | development only, latest-vintage data')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(axis='y',alpha=.18)
    ax.legend(loc='upper left',frameon=False,ncol=3)
    ax.margins(y=.22)
    fig.savefig(output/'forecast-path.svg')
    fig.savefig(output/'forecast-path.png',dpi=150)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    segments=['all_development','2015-2019','2020-2023']
    for ax,metric in zip(axes,['mae','rmse']):
        for i,method in enumerate(['naive','trailing_mean_12','ridge']):
            values=[float(next(r for r in metrics if r['method']==method and r['segment']==s)[metric]) for s in segments]
            bars=ax.bar([x+(i-1)*.24 for x in range(3)],values,width=.23,
                        color=colors[method],label=labels[method])
            ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=8)
        ax.set_xticks(range(3),['2015–2023','2015–2019','2020–2023'])
        ax.set(title=metric.upper(),ylabel='Forecast error (percentage points)',ylim=(0,3.6))
        ax.grid(axis='y',alpha=.15)
        ax.set_axisbelow(True)
    fig.suptitle('The ranking changes with the period and the error metric',fontsize=13,fontweight='bold')
    axes[0].legend(loc='upper left',frameon=False)
    fig.savefig(output/'period-errors.svg')
    fig.savefig(output/'period-errors.png',dpi=150)
    plt.close(fig)
    (output/'diagnostics.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
    manifest={'input_sha256':{name:hashlib.sha256((input_dir/name).read_bytes()).hexdigest()
                             for name in ['predictions.csv','metrics.csv']},
              'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'matplotlib_version':matplotlib.__version__,'holdout_scored':False}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return diagnostic


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(plot(a.input,a.output),indent=2))
