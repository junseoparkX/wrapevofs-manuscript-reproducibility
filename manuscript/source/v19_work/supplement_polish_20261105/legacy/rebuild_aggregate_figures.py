"""Presentation-only re-export from original aggregate tables and Python panels.

Only outputs in this isolated v19 supplementary-polish directory are written.
Original builders' save/manifest entrypoints are never executed.
"""
from pathlib import Path
import importlib.util, sys, json, hashlib, re
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text
import numpy as np
import pandas as pd
WORK=Path(__file__).resolve().parent
BASE=WORK.parents[2];ROOT=BASE.parents[1];OUT=BASE/'figures/supp_polished'
sys.path.insert(0,str(BASE/'scripts'))
sys.path.insert(0,'C:/Users/junse/.codex/skills/nature-figure/scripts')
from audit_panel_alignment import require_matplotlib_panel_alignment
COLORS={'svm_l1':'#386A8B','xgboost':'#7B8794','boruta_rf':'#8A6B98'}
MARKERS={'svm_l1':'o','xgboost':'s','boruta_rf':'^'}
LABELS={'svm_l1':'SVM-L1','xgboost':'XGBoost','boruta_rf':'Boruta-RF'}
BRANCHES=list(COLORS)
SOURCES={}
mpl.rcParams.update({'font.family':'Arial','font.size':7,'axes.labelsize':7,'axes.titlesize':8,'axes.titleweight':'normal','xtick.labelsize':6.5,'ytick.labelsize':6.5,'legend.fontsize':6.5,'pdf.fonttype':42,'svg.fonttype':'none','text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black','axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'supp-polish-legacy'})

def source(n,p):
    p=Path(p);SOURCES.setdefault(str(n),{})[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p

def read(n,p):return pd.read_csv(source(n,p))

def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def panel(ax,letter,title):
    ax.text(-.12,1.12,letter,transform=ax.transAxes,fontsize=8,fontweight='bold',va='bottom')
    ax.set_title(title,fontsize=8,pad=10,loc='left',fontweight='normal')
    ax.grid(False);ax.spines[['top','right']].set_visible(False)

def export(fig,n,exemptions=()):
    # Panel-letter offsets are physical, independent of a panel's grid span.
    for ax in fig.axes:
        for t in ax.texts:
            if re.fullmatch(r'([a-d])\)?',t.get_text()):
                x,y=t.get_position();t.set_x(-12/(ax.get_position().width*fig.get_figwidth()*72))
    for t in fig.findobj(Text):
        value=t.get_text();m=re.fullmatch(r'([a-d])\)?',value)
        if m:t.set_text(m.group(1));t.set_weight('bold');t.set_fontsize(8)
        else:t.set_weight('normal');t.set_fontsize(max(6,t.get_fontsize()))
        t.set_color('black');t.set_fontfamily('Arial');t.set_linespacing(1.4)
        t.set_text(t.get_text().replace('$p_W$','p(L)').replace('$p_{EN}$','p(EN)'))
    for ax in fig.axes:ax.grid(False)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=WORK/f'supp_s{n:02d}.alignment.json',tolerance_pt=1.5,exemptions=exemptions)
    fig.savefig(OUT/f'supp_s{n:02d}.pdf',facecolor='white',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(OUT/f'supp_s{n:02d}.svg',facecolor='white',metadata={'Date':None})
    fig.savefig(OUT/f'supp_s{n:02d}.png',dpi=600,facecolor='white')
    plt.close(fig);print('Built S'+str(n),flush=True)

def s10():
    n=10
    perf=read(n,ROOT/'data/plot_data/Figure_2/source_table_s1_all_performance_metrics.csv')
    dif=read(n,ROOT/'analysis/candidate_priority_1_4/tables/Supplementary_Table_S4B_ADNI_paired_differences.csv')
    fig=plt.figure(figsize=(170/25.4,148/25.4));g=fig.add_gridspec(2,3,left=.13,right=.985,top=.88,bottom=.09,hspace=.55,wspace=.40,height_ratios=[1,.97])
    metrics=[('balanced_accuracy','Balanced accuracy'),('f1_macro','Macro F1'),('auroc_macro','Macro OvR AUROC')]
    for k,(key,title) in enumerate(metrics):
        ax=fig.add_subplot(g[0,k]);col='test_'+key
        for i,b in enumerate(BRANCHES):
            for j,v in enumerate(['First stage','RFECV+GA']):
                r=perf.query('selector==@b and variant==@v').iloc[0];y=i+(-.12 if j==0 else .12)
                ax.errorbar(r[col],y,xerr=[[r[col]-r[col+'_ci_low']],[r[col+'_ci_high']-r[col]]],fmt=MARKERS[b],color=COLORS[b],mfc='white' if j==0 else COLORS[b],ms=4.4,capsize=1.8,lw=.9)
        ax.set_yticks(range(3),[LABELS[b] for b in BRANCHES] if k==0 else []);ax.invert_yaxis();ax.set_ylim(2.5,-.5)
        ax.set_xlabel('Held-out estimate');ax.set_xlim((.40,.90) if k<2 else (.69,.89));panel(ax,chr(97+k),title)
    ax=fig.add_subplot(g[1,:]);names=[]
    for i,b in enumerate(BRANCHES):
        for j,(_,metric) in enumerate(metrics):
            r=dif[(dif.Method==LABELS[b])&(dif.Metric==metric)].iloc[0];y=i*3+j;v=r['WrapEvoFS minus first stage']
            ax.errorbar(v,y,xerr=[[v-r['Paired CI low']],[r['Paired CI high']-v]],fmt=MARKERS[b],color=COLORS[b],ms=4.2,capsize=2,lw=1)
            names.append(LABELS[b]+' · '+metric)
    ax.set_yticks(range(9),names);ax.tick_params(axis='y',labelsize=6);ax.invert_yaxis();ax.axvline(0,color='black',lw=.7);ax.set_xlim(-.15,.17);ax.set_xlabel('Legacy top-3 medoid minus first stage');panel(ax,'d','Paired held-out differences')
    # Long contrast names need a separate left inset; upper panels retain equal widths.
    pos=ax.get_position();ax.set_position([.34,pos.y0,.645,pos.height])
    handles=[Line2D([],[],marker='o',ls='',mfc=c,mec='black',label=s) for c,s in [('white','First stage'),('black','Legacy top-3 medoid')]]
    fig.legend(handles=handles,ncol=2,loc='upper center',bbox_to_anchor=(.55,.995),frameon=False)
    export(fig,n,exemptions=[{'panels':['a','d'],'checks':['column','panel-label'],'reason':'Panel d contains nine descriptive contrast labels and has an intentional wider label gutter.'}])

def s18_19():
    m=module('legacy_post',BASE/'scripts/build_postfreeze_results.py');m.COLORS=COLORS;m.ORIGINAL='#7B8794';m.CURRENT='#386A8B';m.DARK='#111111'
    m.style=panel
    for f in ['benchmark_metrics.csv','benchmark_intervals.csv','paired_regret_medoid_contrasts.csv']:source(18,m.BENCH/f)
    def save18(fig,stem):
        from matplotlib.markers import MarkerStyle
        from matplotlib.colors import to_hex
        for line in fig.findobj(Line2D):
            if line.get_marker()=='o':
                color=to_hex(line.get_color())
                for b,c in COLORS.items():
                    if color.lower()==c.lower():line.set_marker(MARKERS[b])
        for collection in fig.axes[0].collections:
            colors=collection.get_facecolors()
            if len(colors):
                for b,c in COLORS.items():
                    if to_hex(colors[0]).lower()==c.lower():
                        ms=MarkerStyle(MARKERS[b]);collection.set_paths([ms.get_path().transformed(ms.get_transform())])
        fig.axes[2].set_xlabel('Regret medoid − comparator\nAUROC',fontsize=7)
        return export(fig,18,[{'panels':['a','b','c'],'checks':['panel-width'],'reason':'Original unequal widths reserve room for paired-comparator labels; plot heights and gutters retain common alignment.'}])
    m.save=save18
    m.build_benchmark_s22()
    for p in [m.NESTED/'fold_selection_comparison.csv',m.NESTED/'outer_fold_predictions.csv',m.NESTED/'summary.json',m.NESTED_OLD/'fold_metrics.csv',m.NESTED_OLD/'nested_validation_summary.json']:source(19,p)
    # Original implementation calculates the displayed fold AUROC from saved
    # predictions; no model, selection, bootstrap or participant data is changed.
    def save19(fig,stem):
        fig.axes[2].set_xlabel('OOF estimate\n(95% bootstrap CI)',fontsize=7)
        for ax in fig.axes:
            for t in ax.texts:
                if t.get_text() in ['a','b','c']:t.set_y(1.04)
        return export(fig,19)
    m.save=save19
    m.build_nested_s23()

def s20():
    n=20;m=module('legacy_rad',BASE/'scripts/build_radiomics_s20.py')
    m.COLORS={'full_1781':'#386A8B','stable_1346':'#8A6B98'};m.CURRENT='#386A8B';m.TERRACOTTA='#8A6B98';m.SAGE='#7B8794';m.DARK='#111111'
    fig=plt.figure(figsize=(170/25.4,184/25.4),layout='constrained');g=fig.add_gridspec(2,2,height_ratios=[.86,1.14],width_ratios=[.94,1.06]);a=[fig.add_subplot(g[i,j]) for i,j in [(0,0),(0,1),(1,0),(1,1)]]
    m.draw_cohort(a[0]);m.draw_compression(a[1],read(n,m.DATA/'compression_trajectory.csv'))
    original_scatter=a[2].scatter
    def scatter(*args,**kwargs):
        if kwargs.get('marker')=='D':kwargs['marker']='^'
        return original_scatter(*args,**kwargs)
    a[2].scatter=scatter
    m.draw_seed_agreement(a[2],read(n,m.DATA/'seed_stability_summary.csv'));m.draw_effects(a[3],read(n,m.DATA/'paired_heldout_effects.csv'))
    a[1].set_yticks([10,100,1000],['10','100','1,000'])
    a[2].set_xticks(range(6),[LABELS[b] for v in ['Full','Filtered'] for b in BRANCHES],rotation=0)
    a[2].tick_params(axis='x',labelsize=6)
    for x,label in [(1,'Full'),(4,'Filtered')]:a[2].text(x,-.12,label,transform=a[2].get_xaxis_transform(),ha='center',va='top',fontsize=6)
    export(fig,n)

def s21():
    n=21;m=module('legacy_tuned',BASE/'scripts/build_cgga_s9_clean.py');m.COLORS=COLORS;m.MARKERS=MARKERS;m.style=panel
    for f in ['nested_cv_auroc.csv','heldout_intervals.csv','primary_feature_importance.csv']:source(n,m.DATA/f)
    class ExportComplete(Exception):pass
    def save(fig):export(fig,n);raise ExportComplete()
    m.save=save
    try:m.main()
    except ExportComplete:pass

def s23():
    n=23;m=module('legacy_comparators',ROOT/'analysis/cgga_comparators/build_comparator_figure.py')
    m.COLORS=COLORS;m.LIGHT_COLORS={'svm_l1':'#D6E2EB','xgboost':'#DDE1E6','boruta_rf':'#E4DAE9'};m.MARKERS=MARKERS;m.METRIC_COLORS={'auroc':'#386A8B','auprc':'#7B8794','balanced_accuracy':'#8A6B98'};m.METRIC_MARKERS={'auroc':'o','auprc':'s','balanced_accuracy':'^'};m.NAVY='#111111';m.MUTED='#111111'
    performance=read(n,m.INPUT/'comparator_performance.csv');draws=read(n,m.INPUT/'random_null_draw_metrics.csv');null=read(n,m.INPUT/'random_null_summary.csv');dif=read(n,m.INPUT/'paired_bootstrap_differences.csv')
    fig=plt.figure(figsize=(170/25.4,181/25.4));g=fig.add_gridspec(3,1,height_ratios=[1.08,.78,.72],left=.15,right=.985,top=.91,bottom=.06,hspace=.77)
    a=[fig.add_subplot(g[i,0]) for i in range(3)];m.panel_a(a[0],draws,performance,null);m.panel_b(a[1],performance);m.panel_c(a[2],dif)
    a[0].set_ylim(.40,.735)
    for t in a[0].texts:
        if '$p_' in t.get_text():t.set_y(.412)
    a[2].set_ylim(-.11,.12)
    for ax in a:
        for t in ax.texts:
            if re.fullmatch(r'[a-c]\)',t.get_text()):t.set_position((-.11,1.12))
    # Separate metric legend from the panel title.
    a[1].get_legend().set_bbox_to_anchor((1,1.38))
    handles=[Line2D([],[],marker='o',ls='',mfc=c,mec='black',label=s) for c,s in [('#386A8B','Legacy top-3 medoid'),('white','Elastic Net')]]
    fig.legend(handles=handles,ncol=2,loc='upper right',bbox_to_anchor=(.985,.995),frameon=False)
    export(fig,n)

if __name__=='__main__':
    prior=WORK/'aggregate_source_provenance.json'
    if prior.exists():SOURCES.update(json.loads(prior.read_text()))
    tasks={10:s10,18:s18_19,20:s20,21:s21,23:s23}
    for n,fn in tasks.items():
        if len(sys.argv)==1 or str(n) in sys.argv[1:]:fn()
    (WORK/'aggregate_source_provenance.json').write_text(json.dumps(SOURCES,indent=2))
