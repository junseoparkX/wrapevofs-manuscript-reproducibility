"""Redraw main Figures 4 and 5 from frozen aggregate tables only.

No estimator fitting, candidate reselection, bootstrap recomputation, or source
mutation. Figure letters alone are bold. All exports have a natural width170mm.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import ScaledTranslation
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
WORK = BASE / 'v19_work' / 'figures45'
OUT = BASE / 'figures'
from audit_panel_alignment import require_matplotlib_panel_alignment

COLORS = {'svm_l1':'#386A8B', 'xgboost':'#7B8794', 'boruta_rf':'#8A6B98'}
SHAPES = {'svm_l1':'o', 'xgboost':'s', 'boruta_rf':'^'}
BRANCHES = list(COLORS)
NAMES = {'svm_l1':'SVM-L1', 'xgboost':'XGBoost', 'boruta_rf':'Boruta-RF'}
BLACK = '#111111'
OFFSETS = {'svm_l1':-.22, 'xgboost':0, 'boruta_rf':.22}
METHOD_NAMES = {'direct':'Direct', 'rfecv_only':'RFECV-only',
 'regret_constrained_medoid':'WrapEvoFS', 'elastic_net_matched':'Elastic Net\nmatched',
 'stability_matched':'Stability\nmatched', 'random_mean':'Random banks',
 'elastic_net_native':'Elastic Net native', 'stability_native':'Stability native'}
plt.rcParams.update({'font.family':'sans-serif', 'font.sans-serif':['Arial','DejaVu Sans'],
 'font.size':7, 'font.weight':'normal', 'axes.labelweight':'normal', 'axes.titleweight':'normal',
 'axes.labelsize':7, 'axes.titlesize':7, 'xtick.labelsize':7, 'ytick.labelsize':7,
 'legend.fontsize':7, 'text.color':BLACK, 'axes.labelcolor':BLACK, 'xtick.color':BLACK,
 'ytick.color':BLACK, 'axes.edgecolor':BLACK, 'axes.linewidth':.6,
 'xtick.major.width':.6, 'ytick.major.width':.6, 'xtick.major.size':2.5, 'ytick.major.size':2.5,
 'axes.spines.top':False, 'axes.spines.right':False, 'axes.grid':False,
 'pdf.fonttype':42, 'ps.fonttype':42, 'svg.fonttype':'none',
 'svg.hashsalt':'WrapEvoFS-v19-figures45'})
SOURCE_HASHES = {}


def load(folder, name):
    p = BASE / 'supplementary_data' / folder / name
    SOURCE_HASHES[str(p.relative_to(BASE))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return pd.read_csv(p)


def load_review(name):
    p = BASE / 'supplementary_data' / 'ampad_center_sensitivity' / name
    SOURCE_HASHES[str(p.relative_to(BASE))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return pd.read_csv(p)


def panel(ax, letter, xoff=-28):
    transform = ax.transAxes + ScaledTranslation(-30/72, 9/72, ax.figure.dpi_scale_trans)
    ax.text(0,1,letter,transform=transform,ha='left',va='bottom',
            fontweight='bold',fontsize=8,color=BLACK,clip_on=False)
    ax.set_gid(letter)


def errorpoint(ax, x, y, low, high, color, marker='o', filled=True, ms=4.4):
    assert np.isfinite([x,y,low,high]).all() and low <= x <= high
    ax.errorbar(x,y,xerr=[[x-low],[high-x]],fmt=marker,ms=ms,
       mfc=color if filled else 'white',mec=color,mew=.9,
       color=color,ecolor=color,elinewidth=.8,capsize=1.5,zorder=3)


def branch_legend(fig, y):
    handles=[Line2D([],[],marker=SHAPES[b],ls='',ms=4.5,color=COLORS[b],label=NAMES[b]) for b in BRANCHES]
    fig.legend(handles=handles, loc='center',bbox_to_anchor=(.52,y),ncol=3,
       frameon=False,handletextpad=.45,columnspacing=1.7)


def export(fig, stem, panels):
    WORK.mkdir(parents=True,exist_ok=True)
    # Fixed figure canvas: no tight cropping/rescaling at manuscript placement.
    assert abs(fig.get_figwidth()*25.4-170)<1e-7
    fig.canvas.draw()
    report=require_matplotlib_panel_alignment(fig,json_out=WORK/(stem+'.alignment.json'),
        overlay_svg=WORK/(stem+'.alignment.svg'),tolerance_pt=1.5,gutter_tolerance_pt=1.5,
        axes=[a for a in fig.axes if a.get_gid() in panels],
        panel_ids=panels,require_panel_labels=True,strict=True)
    fig.savefig(OUT/f'{stem}.pdf',facecolor='white',metadata={'Creator':'WrapEvoFS v19 frozen-data redraw','CreationDate':None,'ModDate':None})
    fig.savefig(OUT/f'{stem}.svg',facecolor='white',metadata={'Creator':'WrapEvoFS v19 frozen-data redraw','Date':None})
    fig.savefig(OUT/f'{stem}.png',dpi=600,facecolor='white',metadata={'Software':'WrapEvoFS v19 frozen-data redraw'})
    fig.savefig(WORK/f'{stem}_preview.png',dpi=300,facecolor='white')
    plt.close(fig)
    return report


def make_figure4():
    folder='tcga_matched_comparator'
    primary=load(folder,'oof_metrics.csv').query("metric=='macro_ovr_auroc'")
    diffs=load(folder,'paired_regret_medoid_minus_comparator.csv').query("metric=='macro_ovr_auroc'")
    counts=load(folder,'mean_feature_counts.csv')
    randomdiff=load(folder,'random_bank_paired_difference_summary.csv').query("metric=='macro_ovr_auroc'")
    locking=load('tcga_nested_v1_v2','paired_current_minus_comparator.csv').query("metric=='macro_ovr_auroc'")
    assert set(primary.branch)==set(BRANCHES)
    assert (primary.participants==491).all()
    fig,axes=plt.subplots(2,2,figsize=(170/25.4,154/25.4),
                          gridspec_kw={'height_ratios':[.75,1]})
    fig.subplots_adjust(left=.147,right=.976,bottom=.20,top=.85,hspace=.53,wspace=.43)
    branch_legend(fig,.955)
    source_rows=[]
    # a: Full-pipeline grouped bars with an unbroken zero-based AUROC axis.
    methods=['direct','rfecv_only','regret_constrained_medoid']
    for b in BRANCHES:
        for x,m in enumerate(methods):
            r=primary.loc[(primary.branch==b)&(primary.method==m)].iloc[0]
            axes[0,0].bar(x+OFFSETS[b],r.estimate,width=.20,bottom=0,
                          color=COLORS[b],edgecolor='white',linewidth=.4,zorder=2)
            axes[0,0].errorbar(x+OFFSETS[b],r.estimate,
                yerr=[[r.estimate-r.ci_low],[r.ci_high-r.estimate]],fmt='none',
                ecolor=BLACK,elinewidth=.65,capsize=1.3,zorder=3)
            source_rows.append({'panel':'a',**r.to_dict()})
    axes[0,0].set_xticks(range(3),['Direct','RFECV-only','WrapEvoFS'])
    axes[0,0].set_xlim(-.55,2.55);axes[0,0].set_ylim(0,1)
    axes[0,0].set_yticks([0,.25,.5,.75,1]);axes[0,0].set_ylabel('Repeated-OOF macro AUROC')
    axes[0,0].set_title('Full-pipeline performance',pad=15,loc='left',fontsize=7)
    panel(axes[0,0],'a')
    # b: Isolate locking using already-evaluated choices from the same banks.
    methods=['highest_locking_score','legacy_top3_medoid','unrestricted_medoid']
    for b in BRANCHES:
        for y,m in enumerate(methods):
            r=locking.loc[(locking.branch==b)&(locking.comparator==m)].iloc[0]
            errorpoint(axes[0,1],r.difference,y+OFFSETS[b],r.ci_low,r.ci_high,COLORS[b],
                       marker=SHAPES[b],filled=True,ms=4)
            source_rows.append({'panel':'b',**r.to_dict()})
    axes[0,1].axvline(0,color=BLACK,lw=.65,zorder=0)
    axes[0,1].set_yticks(range(3),['Highest\nlocking score','Legacy\ntop-three','Full-bank\nmedoid'])
    axes[0,1].set_ylim(2.65,-.65);axes[0,1].set_xlim(-.017,.020)
    axes[0,1].set_xticks([-.01,0,.01,.02])
    axes[0,1].set_xlabel('WrapEvoFS − comparator AUROC')
    axes[0,1].set_title('Paired locking-rule comparison',pad=15,loc='left',fontsize=7)
    panel(axes[0,1],'b')
    # c: Matched paired differences retain their original positive/negative values.
    methods=['elastic_net_matched','stability_matched']
    for b in BRANCHES:
        for y,m in enumerate(methods):
            r=diffs.loc[(diffs.branch==b)&(diffs.comparator==m)].iloc[0]
            errorpoint(axes[1,0],r.difference,y+OFFSETS[b],r.ci_low,r.ci_high,COLORS[b],marker=SHAPES[b])
            source_rows.append({'panel':'c',**r.to_dict()})
        r=randomdiff.loc[randomdiff.branch==b].iloc[0];y=2+OFFSETS[b]
        axes[1,0].plot([r.min_difference_across_random_banks,r.max_difference_across_random_banks],
                      [y,y],color=COLORS[b],lw=.85,ls=(0,(2,1.8)),zorder=2)
        axes[1,0].plot(r.mean_difference_across_random_banks,y,marker=SHAPES[b],ms=4.5,ls='',
                       mfc='white',mec=COLORS[b],mew=.9,zorder=3)
        source_rows.append({'panel':'c_random',**r.to_dict()})
    axes[1,0].axvline(0,color=BLACK,lw=.65,zorder=0)
    axes[1,0].set_yticks(range(3),[METHOD_NAMES[m] for m in methods]+['Random banks'])
    axes[1,0].set_ylim(2.65,-.65);axes[1,0].set_xlim(-.03,.05)
    axes[1,0].set_xticks([-.02,0,.02,.04])
    axes[1,0].set_xlabel('WrapEvoFS − comparator AUROC')
    axes[1,0].set_title('Paired size-matched comparison',pad=15,loc='left',fontsize=7)
    panel(axes[1,0],'c',-55)
    # d: Every native-support trade-off, including saved AUROC uncertainty.
    methods=['direct','rfecv_only','elastic_net_native','stability_native','regret_constrained_medoid']
    shapes={'direct':'o','rfecv_only':'s','elastic_net_native':'^','stability_native':'v',
            'regret_constrained_medoid':'o'}
    for m in methods:
        for b in BRANCHES:
            r=primary.loc[(primary.branch==b)&(primary.method==m)].iloc[0]
            x=float(counts.loc[(counts.branch==b)&(counts.method==m),'mean_n_features'].iloc[0])
            wrap=m=='regret_constrained_medoid'
            axes[1,1].errorbar(x,r.estimate,yerr=[[r.estimate-r.ci_low],[r.ci_high-r.estimate]],
                fmt=shapes[m],ms=5.3 if wrap else 4.6,mfc=COLORS[b] if wrap else 'white',
                mec=COLORS[b],mew=.9,ecolor=COLORS[b],elinewidth=.75 if wrap else .4,
                alpha=1 if wrap else .68,capsize=0,zorder=4 if wrap else 2)
            source_rows.append({'panel':'d','mean_n_features':x,**r.to_dict()})
    axes[1,1].set_xlabel('Mean selected features')
    axes[1,1].set_ylabel('Repeated-OOF macro AUROC')
    axes[1,1].set_xlim(4,106);axes[1,1].set_xticks([20,40,60,80,100])
    axes[1,1].set_ylim(.795,.868);axes[1,1].set_yticks([.80,.82,.84,.86])
    axes[1,1].set_title('Native-support trade-off',pad=15,loc='left',fontsize=7)
    panel(axes[1,1],'d',-55)
    # Separate uncertainty and method keys, all black regular text.
    interval_handles=[Line2D([],[],color=BLACK,lw=.8,label='95% CI'),
        Line2D([],[],color=BLACK,lw=.8,ls=(0,(2,1.8)),label='Range across five random banks')]
    fig.legend(handles=interval_handles,loc='center',bbox_to_anchor=(.55,.115),ncol=2,
               frameon=False,handlelength=2,handletextpad=.5,columnspacing=1.8)
    handles=[Line2D([],[],ls='',marker=shapes[m],ms=4.5,mec=BLACK,
        mfc=BLACK if m=='regret_constrained_medoid' else 'white',label=METHOD_NAMES[m])
        for m in ['regret_constrained_medoid','direct','rfecv_only','elastic_net_native','stability_native']]
    fig.legend(handles=handles,loc='center',bbox_to_anchor=(.52,.045),ncol=3,
               frameon=False,handletextpad=.45,columnspacing=1.3,labelspacing=.7)
    pd.DataFrame(source_rows).to_csv(WORK/'figure4_plotted_source.csv',index=False)
    return export(fig,'figure_3_strengthened',['a','b','c','d'])


def make_figure5():
    metrics=load('strengthened_main','figure_5_condition_metrics.csv')
    contrasts=load('strengthened_main','figure_5_paired_contrasts.csv')
    sensitivity=load_review('ampad_center_equal_weight_sensitivity.csv')
    assert len(metrics)==24 and len(contrasts)==len(sensitivity)==12
    assert not metrics.duplicated(['center','branch','cap']).any()
    assert not contrasts.duplicated(['branch','cap','comparator']).any()
    centers=['emory','mayo','mount_sinai','rush']
    capnames={'low':'Small','reference':'Reference'}
    assert not sensitivity.duplicated(['branch','cap','comparator']).any()
    assert (sensitivity.n_fixed_centers==4).all()
    assert (sensitivity.n_participants==527).all()
    fig=plt.figure(figsize=(170/25.4,148/25.4))
    gs=fig.add_gridspec(2,2,height_ratios=[.75,1.25],left=.165,right=.98,
                        bottom=.15,top=.90,hspace=.95,wspace=.52)
    axes=[fig.add_subplot(gs[0,:]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1])]
    # a: A 4-center by 6-observed-condition matrix, not a train/test matrix.
    # Fill encodes AUROC, labels preserve exact displayed values; no invented CI.
    conditions=[(b,cap) for b in BRANCHES for cap in ['low','reference']]
    indexed=metrics.set_index(['center','branch','cap'])
    values=np.array([[indexed.loc[(center,b,cap),'macro_auroc'] for b,cap in conditions] for center in centers])
    assert values.shape==(4,6) and np.isfinite(values).all()
    assert values.min()>=.60 and values.max()<=.90
    cmap=LinearSegmentedColormap.from_list('muted_auroc',['#F3F5F8','#B9CBD9','#6B91AB'])
    hm=axes[0].pcolormesh(np.arange(7)-.5,np.arange(5)-.5,values,
                         cmap=cmap,vmin=.60,vmax=.90,shading='flat',rasterized=False)
    axes[0].set_xlim(-.5,5.5);axes[0].set_ylim(3.5,-.5)
    for y in range(4):
        for x in range(6):axes[0].text(x,y,f'{values[y,x]:.3f}',ha='center',va='center',fontsize=7,color=BLACK)
    axes[0].set_yticks(range(4),['Emory','Mayo','Mount Sinai','Rush'])
    axes[0].set_xticks(range(6),['Small','Ref.']*3)
    axes[0].tick_params(axis='both',length=0,pad=5)
    for edge in [.5,1.5,2.5]:axes[0].axhline(edge,color='white',lw=1)
    for edge in [.5,1.5,2.5,3.5,4.5]:axes[0].axvline(edge,color='white',lw=1.5 if edge in [1.5,3.5] else .7)
    for j,b in enumerate(BRANCHES):
        axes[0].text((j*2+1)/6,1.07,NAMES[b],transform=axes[0].transAxes,
                     ha='center',va='bottom',fontsize=7,color=BLACK)
    for spine in axes[0].spines.values():spine.set_visible(False)
    axes[0].set_xlabel('RFECV feature-count cap',labelpad=7)
    # Colorbar is a secondary key, not an analytical panel.
    colorbar_ax=fig.add_axes([.405,.59,.30,.017]);colorbar_ax.set_gid('auroc_colorbar')
    cb=fig.colorbar(hm,cax=colorbar_ax,orientation='horizontal',ticks=[.60,.70,.80,.90])
    cb.solids.set_rasterized(False)
    cb.outline.set_linewidth(.4);cb.ax.tick_params(labelsize=7,length=2,pad=2)
    cb.set_label('Held-out macro AUROC',fontsize=7,labelpad=3)
    panel(axes[0],'a',-33)
    # b,c: Identical contrast ordering and axes, distinct aggregation estimands.
    roworder=[(b,cap) for b in BRANCHES for cap in ['low','reference']]
    specs=[('archived_rfecv_only','o',-.16),('archived_locked_medoid','^',.16)]
    for ax,frame,estimate,low,high,title,letter in [
        (axes[1],contrasts,'updated_minus_comparator','ci_low','ci_high','Pooled participants','b'),
        (axes[2],sensitivity,'equal_center_difference','equal_center_ci_low','equal_center_ci_high','Equal-center mean','c')]:
        for comparator,shape,offset in specs:
            rows=frame.loc[frame.comparator==comparator].set_index(['branch','cap'])
            for y,(b,cap) in enumerate(roworder):
                r=rows.loc[(b,cap)]
                errorpoint(ax,r[estimate],y+offset,r[low],r[high],
                           COLORS[b],marker=shape,filled=(cap=='reference'),ms=4.3)
        ax.axvline(0,color=BLACK,lw=.65,zorder=0)
        ax.set_yticks(range(6),[NAMES[b]+'  '+capnames[cap] for b,cap in roworder])
        ax.set_ylim(5.6,-.6);ax.set_xlim(-.075,.075)
        ax.set_xticks([-.06,-.03,0,.03,.06])
        ax.set_xlabel('WrapEvoFS − comparator AUROC')
        ax.set_title(title,pad=15,loc='left',fontsize=7)
        panel(ax,letter,-68)
    comphandles=[Line2D([],[],ls='',marker='o',ms=4.2,mfc='white',mec=BLACK,label='RFECV-only'),
                Line2D([],[],ls='',marker='^',ms=4.2,mfc='white',mec=BLACK,label='Top-three medoid')]
    fig.legend(handles=comphandles,loc='center',bbox_to_anchor=(.56,.035),ncol=2,
        frameon=False,handletextpad=.5,labelspacing=.65)
    metrics.to_csv(WORK/'figure5_plotted_condition_source.csv',index=False)
    contrasts.to_csv(WORK/'figure5_plotted_contrast_source.csv',index=False)
    sensitivity.to_csv(WORK/'figure5_plotted_center_sensitivity_source.csv',index=False)
    return export(fig,'figure_5_strengthened',['a','b','c'])


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    reports={'figure4':make_figure4(),'figure5':make_figure5()}
    manifest={'source_sha256':SOURCE_HASHES,'width_mm':170,'no_refits':True,'unchanged_source_data':True,
       'design_round':4,'row_counts':{'figure4_a':9,'figure4_b':9,'figure4_c':6,'figure4_c_random':3,'figure4_d':15,'figure5_a':24,'figure5_b':12,'figure5_c':12},
       'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for stem in ['figure_3_strengthened','figure_5_strengthened'] for ext in ['pdf','svg','png'] for p in [OUT/(stem+'.'+ext)]}}
    for rel,expected in SOURCE_HASHES.items():
        assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==expected, rel
    (WORK/'render_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'rendered':list(reports),'sources_unchanged':True}))

if __name__=='__main__':main()
