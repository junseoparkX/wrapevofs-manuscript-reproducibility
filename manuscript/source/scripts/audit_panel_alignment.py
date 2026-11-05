"""Portable geometry checks for the manuscript's Matplotlib renderers.

Checks are in physical points. This local helper removes a private editor-plugin
dependency; it does not change plot data, artists, fonts, or layout.
"""
from pathlib import Path
import html
import json
import math


def require_matplotlib_panel_alignment(fig, *, json_out, overlay_svg=None,
        tolerance_pt=1.5, gutter_tolerance_pt=1.5, axes=None, panel_ids=None,
        row_groups=None, column_groups=None, exemptions=None,
        require_panel_labels=False, strict=True):
    fig.canvas.draw()
    axes=list(fig.axes if axes is None else axes)
    ids=panel_ids or [a.get_gid() or a.get_label() or f'panel_{i}' for i,a in enumerate(axes)]
    if len(ids)!=len(axes) or len(set(ids))!=len(ids):
        raise ValueError('Panel IDs must be unique and match the axes.')
    width,height=fig.get_size_inches()*72
    boxes={n:[a.get_position().x0*width,a.get_position().y0*height,
              a.get_position().x1*width,a.get_position().y1*height] for n,a in zip(ids,axes)}
    failures=[];checks=[]
    exempt={(n,c) for e in exemptions or [] for n in e['panels'] for c in e['checks']}
    for n,b in boxes.items():
        if not all(math.isfinite(v) for v in b) or b[2]<=b[0] or b[3]<=b[1]:failures.append(f'{n}: invalid plot bounds')
        if b[0]<-tolerance_pt or b[1]<-tolerance_pt or b[2]>width+tolerance_pt or b[3]>height+tolerance_pt:failures.append(f'{n}: outside figure canvas')
    # Explicit groups override automatic GridSpec grouping.
    inferred_rows={};inferred_cols={}
    for n,a in zip(ids,axes):
        spec=a.get_subplotspec() if hasattr(a,'get_subplotspec') else None
        if spec is not None:
            grid=id(spec.get_gridspec())
            inferred_rows.setdefault((grid,spec.rowspan.start,spec.rowspan.stop),[]).append(n)
            inferred_cols.setdefault((grid,spec.colspan.start,spec.colspan.stop),[]).append(n)
    row_groups=list(inferred_rows.values()) if row_groups is None else row_groups
    column_groups=list(inferred_cols.values()) if column_groups is None else column_groups
    def spread(names,values,label,tol):
        if len(values)>1 and max(values)-min(values)>tol:failures.append(f'{label}: {names}')
        checks.append({'check':label,'panels':names,'spread_pt':max(values)-min(values) if values else 0})
    for names in row_groups:
        for n in names:
            if n not in boxes:raise ValueError(f'Unknown panel: {n}')
        for index,label in [(1,'row bottom'),(3,'row top')]:spread(names,[boxes[n][index] for n in names],label,tolerance_pt)
        eligible=[n for n in names if (n,'panel-width') not in exempt]
        if len(names)>=3:spread(eligible,[boxes[n][2]-boxes[n][0] for n in eligible],'panel width',tolerance_pt)
        eligible=sorted((n for n in names if (n,'horizontal-gutter') not in exempt),key=lambda n:boxes[n][0])
        if len(eligible)>=3:spread(eligible,[boxes[b][0]-boxes[a][2] for a,b in zip(eligible,eligible[1:])],'horizontal gutter',gutter_tolerance_pt)
    for names in column_groups:
        for index,label in [(0,'column left'),(2,'column right')]:spread(names,[boxes[n][index] for n in names],label,tolerance_pt)
    if require_panel_labels:
        for n,a in zip(ids,axes):
            if (n,'panel-label') not in exempt and not any(t.get_text().strip().rstrip(')')==n for t in a.texts):failures.append(f'{n}: missing panel label')
    report={'status':'FAIL' if failures else 'PASS','tolerance_pt':tolerance_pt,'panels':boxes,'checks':checks,'failures':failures,'exemptions':exemptions or []}
    p=Path(json_out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2))
    if overlay_svg:
        shapes=[]
        for n,(x0,y0,x1,y1) in boxes.items():shapes.append(f'<rect x="{x0}" y="{height-y1}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="black"/><text x="{x0}" y="{height-y1+10}">{html.escape(n)}</text>')
        Path(overlay_svg).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'+''.join(shapes)+'</svg>')
    if strict and failures:raise AssertionError('; '.join(failures))
    return report
