"""Isolated supplementary-only rendering; main files are hash-guarded."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, shutil, sys
from pathlib import Path
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import PowerNorm, LinearSegmentedColormap
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT.parents[1]
WORK=Path(__file__).resolve().parent
OUT=WORK/'figures'
QA=WORK/'qa'
DATA=WORK/'source_data'
for p in [OUT,QA,DATA]: p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,r'C:\Users\junse\.codex\skills\nature-figure\scripts')
from audit_panel_alignment import require_matplotlib_panel_alignment
from v19_build_figures23 import configure
BLUE,SLATE,PLUM='#386A8B','#7B8794','#8A6B98'
COLORS=dict(zip(['svm_l1','xgboost','boruta_rf'],[BLUE,SLATE,PLUM]))
LABELS=dict(zip(COLORS,['SVM-L1','XGBoost','Boruta-RF']))
SHAPES=dict(zip(COLORS,['o','s','^']))
ALLOWED={'figure_s17','figure_s18','figure_s15','figure_s16','figure_s25_repeat_1','figure_s25_repeat_2','figure_s26','figure_s27','figure_s_matched_comparator_strengthened','figure_s21','figure_s24'}
AUDIT={}
SOURCES={}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frozen():
    names=['figure_2','figure_4_strengthened','figure_3_strengthened','figure_5_strengthened']
    return {str(p):sha(p) for p in (ROOT/'figures').iterdir() if p.is_file() and (p.name.startswith('figure_1') or p.stem in names)}
def read(path):
    path=Path(path); f=pd.read_csv(path,float_precision='round_trip')
    target=DATA/(path.parent.name+'__'+path.name)
    shutil.copy2(path,target)
    SOURCES[str(path)]={'sha256':sha(path),'rows':len(f),'copy':str(target.relative_to(WORK))}
    return f
def style():
    configure()
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
        'font.size':6.7,'axes.labelsize':6.7,'axes.titlesize':7.2,'xtick.labelsize':6.3,'ytick.labelsize':6.3,
        'legend.fontsize':6.3,'svg.fonttype':'none','pdf.fonttype':42,'savefig.bbox':None})
def label(ax,l):
    ax.annotate(l,(0,1),xycoords='axes fraction',xytext=(-24,8),textcoords='offset points',
                fontsize=9,fontweight='bold',ha='left',va='bottom',annotation_clip=False)
def clean(ax):
    ax.grid(False);ax.spines[['top','right']].set_visible(False)
def branch_handles():
    return [Line2D([],[],marker=SHAPES[b],color=COLORS[b],linestyle='none',markersize=4,label=LABELS[b]) for b in COLORS]
def geometry(fig):
    parts=[]
    for ax in fig.axes:
        for l in ax.lines:
            parts.append(('line',np.asarray(l.get_xydata()).tolist()))
        for c in ax.collections:
            parts.append(('collection',np.asarray(c.get_offsets()).tolist()))
            if hasattr(c,'get_segments'):parts.append(('segments',[np.asarray(s).tolist() for s in c.get_segments()]))
    return hashlib.sha256(json.dumps(parts,sort_keys=True,allow_nan=True).encode()).hexdigest()
def save(fig,stem,counts,groups=None,exemptions=None):
    assert stem in ALLOWED
    before=geometry(fig)
    for ax in fig.axes:
        clean(ax)
        for t in ax.get_xticklabels()+ax.get_yticklabels():
            if t.get_rotation():t.set_rotation_mode('anchor')
    for t in fig.findobj(mpl.text.Text):
        text=t.get_text()
        if not text: continue
        t.set_color('black')
        if re.fullmatch('[a-d]\\)?',text):t.set_text(text[0]);t.set_fontweight('bold')
        else:t.set_fontweight('normal');t.set_fontsize(max(6.3,min(t.get_fontsize(),8)))
    after=geometry(fig);assert before==after
    fig.set_size_inches(170/25.4,fig.get_figheight(),forward=True)
    fig.canvas.draw()
    for i,ax in enumerate(fig.axes):
        if not ax.get_label():ax.set_label(f'p{i}')
    if groups is None:groups=[[ax.get_label() for ax in fig.axes]]
    require_matplotlib_panel_alignment(fig,json_out=QA/f'{stem}.alignment.json',
        overlay_svg=QA/f'{stem}.alignment.svg',tolerance_pt=1.5,gutter_tolerance_pt=1.5,
        row_groups=groups,exemptions=exemptions or [],strict=True)
    fig.savefig(OUT/f'{stem}.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(OUT/f'{stem}.svg')
    fig.savefig(OUT/f'{stem}.png',dpi=600)
    fig.savefig(QA/f'{stem}_review.png',dpi=300)
    AUDIT[stem]={'width_mm':170,'height_mm':fig.get_figheight()*25.4,'data':counts,
        'artist_geometry_preserved_during_style':before==after,'native_vector':True,'png_role':'600dpi preview, not claimed as production line art',
        'source_geometry_hash':before,'pdf_sha256':sha(OUT/f'{stem}.pdf')}
    plt.close(fig)
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.FIGURES=OUT
    for k in ['DARK','BLACK']:setattr(m,k,'#000000')
    for k in ['MID','ORIGINAL','GRAY']:setattr(m,k,SLATE)
    for k in ['COLORS','BRANCH_COLORS']:setattr(m,k,COLORS)
    return m

def s1():
    f=read(REPO/'analysis/regret_revision/figure4_penalty_flattening_plot_data.csv');style()
    fig,axs=plt.subplots(1,3,figsize=(170/25.4,76/25.4));fig.subplots_adjust(left=.09,right=.98,bottom=.20,top=.88,wspace=.65)
    for b in COLORS:
        r=f[f.branch==b];axs[0].scatter(r.target_deviation,r.fraction_zero_legacy_fitness,s=20,marker=SHAPES[b],color=COLORS[b],edgecolors='white',linewidths=.4)
    r=f[f.known_failure_mode]
    axs[0].scatter(r.target_deviation,r.fraction_zero_legacy_fitness,s=55,marker='*',facecolor='black',edgecolor='black')
    axs[0].axhline(.5,color='black',ls='--',lw=.7);axs[0].set(xlabel='Absolute target deviation',ylabel='Zero run-best fraction')
    axs[0].legend(handles=branch_handles(),loc='lower right',handletextpad=.4)
    ds={'AMP-AD':(BLUE,'o'),'CGGA':(PLUM,'s'),'ADNI':(SLATE,'^')}
    for dataset,(col,mark) in ds.items():
        r=f[f.dataset==dataset]
        if len(r):axs[1].scatter(r.target_deviation,r.number_all_zero_generations,s=19,marker=mark,facecolors='white' if dataset=='CGGA' else col,edgecolors=col,label=dataset)
    axs[1].set(xlabel='Absolute target deviation',ylabel='All-zero generations (of 250)');axs[1].legend(loc='upper left')
    datasets=sorted(f.dataset.unique());values=[100*f[f.dataset==d].warning_status.ne('none').mean() for d in datasets]
    axs[2].bar(range(len(datasets)),values,color=[ds[d][0] for d in datasets],width=.55)
    axs[2].set_xticks(range(len(datasets)),datasets);axs[2].set(ylabel='Configurations warned (%)',ylim=(0,105))
    for a,l in zip(axs,'abc'):label(a,l)
    save(fig,'figure_s17',{'conditions':len(f),'warning_percent':dict(zip(datasets,values)),'stress_conditions':len(f[f.known_failure_mode])})

def s2():
    f=read(ROOT/'revision_outputs/S16_CONDITION_LEVEL_PAIRED.csv');style()
    fig=plt.figure(figsize=(170/25.4,190/25.4));cmap=LinearSegmentedColormap.from_list('lightblue',['#f6f8fa','#a7c2d4','#6d99b5'])
    centers=['Emory','Mayo','Mount Sinai','Rush'];branches=['SVM-L1','XGBoost','Boruta-RF'];caps=['Small-cap','Reference-cap']
    conds=[(b,c) for b in branches for c in caps];labels=[b+'\n'+('Small' if c=='Small-cap' else 'Reference') for b,c in conds]
    groups=[]
    for row,(fields,y,title) in enumerate([(('original_target_deviation','updated_target_deviation'),.77,'Absolute target deviation'),(('original_all_zero_generations','updated_all_zero_generations'),.48,'Legacy-zero diagnostic generations')]):
        mats=[np.array([[f[(f.Center==center)&(f.Branch==b)&(f.Cap==cap)].iloc[0][field] for b,cap in conds] for center in centers],float) for field in fields]
        rowids=[]
        for j,(x,mat) in enumerate(zip([.12,.57],mats)):
            ax=fig.add_axes([x,y,.34,.16],label=f'heat{row}{j}');rowids.append(ax.get_label())
            im=ax.pcolormesh(np.arange(7),np.arange(5),mat,cmap=cmap,norm=PowerNorm(.52,vmin=0,vmax=max(m.max() for m in mats)),shading='flat',rasterized=False)
            ax.set_ylim(4,0);ax.set_xticks(np.arange(6)+.5,['S','R']*3);ax.set_yticks(np.arange(4)+.5,centers if j==0 else [])
            for xpos,branch in zip([1,3,5],branches):ax.text(xpos,-.20,branch,transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=6.3)
            ax.tick_params(length=0);ax.set_title('Original' if j==0 else 'Updated',pad=6)
            for rr in range(4):
                for cc in range(6):ax.text(cc+.5,rr+.5,str(int(mat[rr,cc])),ha='center',va='center',fontsize=6.3)
            for spine in ax.spines.values():spine.set_visible(False)
        cax=fig.add_axes([.945,y,.012,.16],label=f'cb{row}');cb=fig.colorbar(im,cax=cax);cb.solids.set_rasterized(False);cb.outline.set_visible(False)
        fig.text(.12,y+.205,title,fontsize=7.4,ha='left');fig.text(.035,y+.205,'ab'[row],fontsize=9,fontweight='bold')
        groups.append(rowids)
    for i,(metric,y) in enumerate([('target_deviation',.255),('all_zero_generations',.075)]):
        ids=[]
        for j,(group,order,x) in enumerate([('Center',centers,.12),('Branch',branches,.57)]):
            ax=fig.add_axes([x,y,.34,.12],label=f'agg{i}{j}');ids.append(ax.get_label())
            a=f.groupby(group)['original_'+metric].sum().reindex(order);b=f.groupby(group)['updated_'+metric].sum().reindex(order);xx=np.arange(len(order))
            ax.bar(xx-.18,a,width=.34,color='white',edgecolor=SLATE,lw=.8);ax.bar(xx+.18,b,width=.34,color=BLUE,edgecolor=BLUE,lw=.5)
            ax.set_xticks(xx,['Sinai' if z=='Mount Sinai' else z for z in order]);ax.tick_params(axis='x',length=0)
            if j==0:ax.set_ylabel('Absolute target deviation' if i==0 else 'Legacy-zero generations')
        groups.append(ids)
    fig.text(.035,.39,'c',fontsize=9,fontweight='bold')
    fig.legend(handles=[Patch(facecolor='white',edgecolor=SLATE,label='Original'),Patch(facecolor=BLUE,label='Updated')],loc='center',bbox_to_anchor=(.53,.415),ncol=2)
    save(fig,'figure_s18',{'conditions':24,'heatmap_cells':96,'target_totals':[216,137],'diagnostic_totals':[673,333],'normalization':'PowerNorm gamma0.52 preserved'},groups=groups)

def s3():
    f=read(REPO/'analysis/regret_revision/figure2_compression_regret_plot_data.csv');style()
    rules=['highest_development_cv_run','legacy_top_three_medoid','all_run_medoid','regret_constrained_medoid_abs_0.01']
    names=['Highest score','Legacy top-three','Full-bank medoid','Regret medoid'];marks=['o','s','^','v'];colors=[BLUE,SLATE,PLUM,'black']
    assert set(f.selection_rule)==set(rules)
    fig,axs=plt.subplots(1,2,figsize=(170/25.4,88/25.4));fig.subplots_adjust(left=.1,right=.98,bottom=.27,top=.88,wspace=.38)
    summary=[]
    for i,(rule,name,mark,col) in enumerate(zip(rules,names,marks,colors)):
        r=f[f.selection_rule==rule];q=np.quantile(r.development_cv_regret,[.25,.5,.75]);summary.append(q.tolist())
        axs[0].scatter(100*r.compression_ratio,r.development_cv_regret,s=18,marker=mark,facecolors='white' if i==0 else col,edgecolors=col,linewidths=.5,alpha=.8,label=name)
        axs[1].vlines(i,q[0],q[2],color=col,lw=3);axs[1].scatter(i,q[1],s=26,marker=mark,facecolors='white' if i==0 else col,edgecolors=col,zorder=3)
    axs[0].set(xlabel='Compression relative to Direct (%)',ylabel='Development-CV regret',xlim=(-3,100),ylim=(-.0015,max(.045,f.development_cv_regret.max()*1.08)))
    axs[1].set_xticks(range(4),['Highest\nscore','Legacy\ntop-three','Full-bank\nmedoid','Regret\nmedoid']);axs[1].set_ylabel('Development-CV regret');axs[1].set_title('Median and interquartile range')
    for a,l in zip(axs,'ab'):a.axhline(.01,color='black',ls='--',lw=.7);label(a,l)
    fig.legend(*axs[0].get_legend_handles_labels(),loc='lower center',ncol=4,bbox_to_anchor=(.53,.035),columnspacing=1,handletextpad=.4)
    save(fig,'figure_s15',{'records':len(f),'per_rule':f.selection_rule.value_counts().to_dict(),'quartiles':summary,'shape_change':'regret diamond to down-triangle'})

def s4():
    m=module('build_revision_figures');m.DATASET_COLORS={'AMP-AD':BLUE,'CGGA':PLUM};style()
    read(ROOT/'revision_outputs/S16_LOCKING_SENSITIVITY_PLOT_DATA.csv')
    def captured(fig,stem):
        fig.set_figheight(76/25.4);fig.subplots_adjust(left=.095,right=.98,bottom=.24,top=.84,wspace=.62)
        return save(fig,stem,{'dataset_tolerance_rows':8,'undefined_singleton_Jaccard':2,'data_source':'S16_LOCKING_SENSITIVITY_PLOT_DATA.csv'})
    m.save_figure=captured;m.build_s16()

def s5():
    f=read(ROOT/'supplementary_data/tcga_nested_v1_v2/candidate_level_geometry.csv');style()
    for repeat in [1,2]:
        fig,axs=plt.subplots(3,5,figsize=(170/25.4,180/25.4),sharex=True,sharey=True)
        fig.subplots_adjust(left=.11,right=.98,bottom=.09,top=.88,wspace=.28,hspace=.45)
        for i,b in enumerate(COLORS):
            for fold in range(1,6):
                ax=axs[i,fold-1];r=f[(f.outer_repeat==repeat)&(f.outer_fold==fold)&(f.branch==b)];assert len(r)==5
                ax.axvspan(0,.01,color='#edf2f5');ax.scatter(r.absolute_regret,r.jaccard_distance_to_highest,s=16,color=COLORS[b],alpha=.7)
                high=r.sort_values(['locking_score','feature_count','stable_mask_hash'],ascending=[False,True,True]).iloc[[0]];chosen=r[r.selected]
                ax.scatter(high.absolute_regret,high.jaccard_distance_to_highest,s=32,marker='o',facecolors='none',edgecolors='black',lw=.9)
                ax.scatter(chosen.absolute_regret,chosen.jaccard_distance_to_highest,s=30,marker='s',facecolors='none',edgecolors=COLORS[b],lw=1.1)
                ax.axvline(.01,color='black',ls='--',lw=.6);ax.set_title(f'Fold {fold}');ax.set(xlim=(-.002,.041),ylim=(-.05,1.05));ax.set_xticks([0,.02,.04],['0','.02','.04']);ax.set_yticks([0,.5,1])
                if fold==1:ax.set_ylabel(LABELS[b]+'\nJaccard distance')
                if i==2:ax.set_xlabel('Score gap')
        fig.suptitle(f'Repeat {repeat}',fontsize=8,y=.975)
        fig.legend(handles=[Line2D([],[],marker='o',color=SLATE,linestyle='none',label='Saved candidate'),Line2D([],[],marker='o',mfc='none',mec='black',linestyle='none',label='Highest score'),Line2D([],[],marker='s',mfc='none',mec='black',linestyle='none',label='Selected medoid')],loc='upper center',bbox_to_anchor=(.53,.945),ncol=3)
        for i,ax in enumerate(axs.flat):ax.set_label(f'p{i}')
        save(fig,f'figure_s25_repeat_{repeat}',{'banks':15,'candidates':75,'selected':15,'shape_change':'selected diamond to open square'},groups=[[f'p{i*5+j}' for j in range(5)] for i in range(3)])

def s6s7():
    m=module('build_tcga_nested_figures');m.COLORS=COLORS;m.DARK='black';m.MID=SLATE;style()
    base=ROOT/'supplementary_data/tcga_nested_v1_v2'
    sel=read(base/'selected_feature_sets.csv');agree=read(base/'agreement_by_repeat_branch.csv');pairs=read(base/'outer_fold_pairwise_stability.csv')
    for n in ['oof_metrics.csv','paired_current_minus_comparator.csv','feature_counts_by_condition.csv']:read(base/n)
    def captured(fig,stem,manifest):
        name='figure_s26' if 'S26' in str(stem) else 'figure_s27'
        if name=='figure_s26':fig.set_figheight(83/25.4);fig.subplots_adjust(left=.09,right=.98,bottom=.25,top=.86,wspace=.6)
        else:
            fig.set_figheight(96/25.4);fig.subplots_adjust(left=.145,right=.985,bottom=.22,top=.86,wspace=.9)
            fig.axes[1].set_xlabel('Regret medoid −\ncomparator AUROC')
        return save(fig,name,{'agreement_summaries':6,'outer_pairs':60,'locked_sets':30} if name=='figure_s26' else {'AUROC_estimates':18,'paired_differences':15,'feature_count_means':18,'CI':'unchanged 95% participant-clustered bootstrap'})
    m.save_figure=captured;m.supplementary_stability(sel,agree,pairs,OUT,[]);m.supplementary_performance(base,OUT,[])

def s8():
    m=module('build_tcga_matched_comparator_figures');m.BRANCH_COLORS=COLORS;m.DARK='black';style();m.require_validated()
    metrics,diffs,pred,freq,runtime=m.load_frames()
    # Saved final means include the parent methods; the newer fold_metrics.csv
    # only contains added selector methods and cannot supply parent counts.
    counts=read(m.SOURCE/'mean_feature_counts.csv')
    required=['regret_constrained_medoid','elastic_net_native','elastic_net_matched','stability_native','stability_matched']
    assert len(counts[counts.method.isin(required)])==15
    for n in ['oof_metrics.csv','paired_regret_medoid_minus_comparator.csv','outer_fold_feature_frequency.csv','fold_metrics.csv']:read(m.SOURCE/n)
    def captured(fig,stem):
        fig.set_figheight(88/25.4);fig.subplots_adjust(left=.19,right=.98,bottom=.22,top=.86,wspace=.48)
        fig.axes[0].set_xlabel('Repeated-OOF\nmacro AUPRC');fig.axes[1].set_xlabel('Repeated-OOF\nbalanced accuracy')
        return save(fig,stem,{'AUPRC_estimates':15,'balanced_accuracy_estimates':15,'feature_count_means':15,'CI':'unchanged 95% participant-clustered bootstrap'})
    m.save_figure=captured;m.make_supplement(metrics,diffs,counts,runtime)

def s9():
    m=module('build_postfreeze_results');m.COLORS=COLORS;m.DARK='black';style()
    read(m.AMP/'condition_metrics.csv');read(m.AMP/'paired_condition_contrasts.csv')
    def captured(fig,stem):
        fig.set_figheight(90/25.4);fig.subplots_adjust(left=.09,right=.985,bottom=.25,top=.85,wspace=.95)
        fig.axes[0].set_xticks(range(4),['Emory','Mayo','Sinai','Rush'],rotation=45,rotation_mode='anchor',ha='right',fontsize=6.3)
        for ax in fig.axes[1:]:ax.set_xlabel('Macro AUROC\ndifference')
        return save(fig,stem,{'frozen_signatures':24,'paired_pooled_contrasts':12,'CI':'unchanged 95% paired stratified bootstrap'})
    m.save=captured;m.build_amp_s21()

def s28():
    base=ROOT/'supplementary_data/locking_rule_simulation';a=read(base/'figure_s24_panel_a.csv');b=read(base/'figure_s24_panel_b.csv');c=read(base/'figure_s24_panel_c.csv');style()
    fig,axs=plt.subplots(1,3,figsize=(170/25.4,87/25.4));fig.subplots_adjust(left=.10,right=.98,bottom=.29,top=.86,wspace=.65)
    topo=['aligned','competing','misleading']
    for name,col,mark in zip(topo,[BLUE,SLATE,PLUM],['o','s','^']):
        r=a[a.topology==name].sort_values('score_noise_ratio');axs[0].fill_between(r.score_noise_ratio,1000*r.q25,1000*r.q75,color=col,alpha=.14);axs[0].plot(r.score_noise_ratio,1000*r.mean_current_minus_highest,marker=mark,color=col,ms=3,lw=.9,label=name.capitalize())
    axs[0].axhline(0,color='black',lw=.6);axs[0].set(xlabel='Locking-score noise ratio',ylabel='Current − highest oracle regret\n(0.001 units)',ylim=(-1.4,5.5));axs[0].set_xticks([0,1,2,4]);axs[0].set_title('Noise and topology')
    b=b.sort_values('delta');axs[1].plot(1000*b.empirical_regret,b.full_bank_mean_jaccard,marker='o',color=BLUE,ms=3,lw=.9)
    for (_,r),offset in zip(b.iterrows(),[(6,-7),(6,4),(6,-12),(-4,6)]):axs[1].annotate('δ='+str(r.delta).rstrip('0').rstrip('.') if r.delta else 'δ=0',(1000*r.empirical_regret,r.full_bank_mean_jaccard),xytext=offset,textcoords='offset points',ha='right' if offset[0]<0 else 'left',fontsize=6.3)
    axs[1].set(xlabel='Mean empirical regret\n(0.001 units)',ylabel='Mean full-bank Jaccard',xlim=(-.2,5.2),ylim=(.414,.465));axs[1].set_title('Tolerance trade-off')
    for rule,name,col,mark in zip(['highest_score','legacy_top3_medoid','full_bank_medoid'],['Highest score','Legacy top-three','Full-bank medoid'],[BLUE,SLATE,PLUM],['o','s','^']):
        r=c[c.comparator==rule].sort_values('candidate_count');assert (r.candidate_count>0).all();axs[2].plot(r.candidate_count,1000*r.mean_current_minus_comparator,marker=mark,color=col,ms=3,lw=.9,label=name)
    axs[2].set_xscale('log');axs[2].set_xticks([3,5,10,20,50,100],['3','5','10','20','50','100']);axs[2].minorticks_off();axs[2].axhline(0,color='black',lw=.6)
    axs[2].set(xlabel='Retained candidates, R',ylabel='Current − comparator oracle regret\n(0.001 units)',ylim=(-.62,.25));axs[2].set_title('Candidate-bank size')
    fig.legend(*axs[0].get_legend_handles_labels(),loc='lower left',bbox_to_anchor=(.09,.005),ncol=1)
    fig.legend(*axs[2].get_legend_handles_labels(),loc='lower right',bbox_to_anchor=(.985,.005),ncol=1)
    for ax,l in zip(axs,'abc'):label(ax,l)
    save(fig,'figure_s24',{'topology_noise_rows':len(a),'tolerances':len(b),'bank_size_comparator_rows':len(c),'IQR':'all q25/q75 bands preserved','scale':'oracle regret multiplied by1000 as before; R logarithmic','shape_change':'full-bank diamond to triangle'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',default='all');args=parser.parse_args();guard=frozen()
    functions={'1':s1,'2':s2,'3':s3,'4':s4,'5':s5,'6':s6s7,'7':s6s7,'8':s8,'9':s9,'28':s28}
    todo=list(dict.fromkeys(functions.values())) if args.only=='all' else [functions[x] for x in args.only.split(',')]
    for fn in todo:fn();assert frozen()==guard,'Main figure hash changed'
    (QA/'data_integrity.json').write_text(json.dumps({'figures':AUDIT,'sources':SOURCES,'main_before':guard,'main_after':frozen(),'main_unchanged':frozen()==guard},indent=2),encoding='utf-8')
    print(json.dumps(AUDIT,indent=2))
if __name__=='__main__':main()
