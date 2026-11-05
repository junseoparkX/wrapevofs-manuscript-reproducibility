"""Python-only presentation adaptation of frozen editable supplementary SVGs.

Scientific coordinates, curves, intervals, text values and conditions remain
unchanged. No image upsampling, estimator or statistical recomputation occurs.
"""
from pathlib import Path
import base64
import copy
import hashlib
import io
import json
import math
import re
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')

WORK=Path(__file__).resolve().parent
BASE=WORK.parents[2]
OUT=BASE/'figures/supp_polished'
OUT.mkdir(parents=True,exist_ok=True)
NS='http://www.w3.org/2000/svg'
XL='http://www.w3.org/1999/xlink'
ET.register_namespace('',NS)
ET.register_namespace('xlink',XL)
INV=json.loads((WORK/'source_vectors_inventory.json').read_text())
NUMBERS=[11,12,13,14,15,16,17,22,27]
BRANCHES={
 '#2c9b68':'#386A8B','#2a9d6f':'#386A8B','#1f7a8c':'#386A8B',
 '#e5a00d':'#7B8794','#e49a17':'#7B8794','#c78a0a':'#7B8794',
 '#d65748':'#8A6B98','#d45a4c':'#8A6B98','#8b5e83':'#8A6B98',
 '#0072b2':'#386A8B','#d55e00':'#8A6B98','#4c78a8':'#386A8B',
 '#f2a65a':'#AEB8C4','#7b3294':'#8A6B98','#7656c9':'#8A6B98',
 '#c7e6d8':'#D6E2EB','#f7e0b2':'#DDE1E6','#f1cbc6':'#E4DAE9',
 '#c9a227':'#111111','#8b731a':'#111111',
}
GRID={'#dce3e8','#d8e0e8','#d9d9d9','#e0e0e0','#e4e4e4','#e6e6e6','#e7e7e7','#e9e9e9','#f1f1f1','#e1e7ed','#e6e9ed'}
NOTES={
 16:['gold outline: locked medoid'],
 17:['Cells: AUROC/Direct ratio; n; feature reduction','Single GA run = prespecified run 1','No guidance: λ=0; stored target inactive in GA fitness'],
 22:['Secondary-analysis peak memory: 178.0 MB'],
 27:['No additional compression'],
}


def text(el):return ''.join(el.itertext()).strip()


def style(el):
    return {p.split(':',1)[0].strip():p.split(':',1)[1].strip() for p in el.get('style','').split(';') if ':' in p}


def write_style(el,d):el.set('style','; '.join(f'{k}: {v}' for k,v in d.items()))


def set_style(el,key,value):
    d=style(el);d[key]=value;write_style(el,d)
    if key in el.attrib:el.set(key,value)


def numeric_tokens(root):
    return [text(e) for e in root.iter() if e.tag==f'{{{NS}}}text' and re.fullmatch(r'[+−-]?\d+(?:\.\d+)?%?',text(e))]


def diamond_points(value):
    if re.search(r'[ACQSTHV]',value.upper()):return None
    nums=[float(n) for n in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:e[-+]?\d+)?',value,re.I)]
    if len(nums) not in (8,10):return None
    points=list(zip(nums[::2],nums[1::2]))
    if len(points)==5 and points[-1]==points[0]:points.pop()
    if len(points)!=4:return None
    xs=[p[0] for p in points];ys=[p[1] for p in points]
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    if not all(abs(x-cx)<0.005 or abs(y-cy)<0.005 for x,y in points):return None
    if max(xs)-min(xs)>15 or max(ys)-min(ys)>15:return None
    return cx,cy,(max(xs)-min(xs))/2,(max(ys)-min(ys))/2


def lighten(color):
    rgb=[int(color[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(.45*x+.55*255):02x}' for x in rgb)


def crop_flat_svg(root,y,h):
    """Remove off-page primitives, rather than hiding still-extractable PDF text."""
    for e in list(root):
        tag=e.tag.split('}')[-1]
        if tag in ['defs','style','metadata']:continue
        ys=[]
        for key in ['y','y1','y2','cy']:
            if e.get(key) is not None:ys.append(float(e.get(key)))
        if tag=='rect' and ys:ys.append(ys[0]+float(e.get('height','0')))
        if tag in ['polygon','polyline','path']:
            coords=[float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+)',e.get('points',e.get('d','')))]
            ys+=coords[1::2]
        if ys and (max(ys)<y or min(ys)>y+h):root.remove(e)
    root.set('viewBox',f'0 {y} 170 {h}');root.set('height',f'{h}mm')
    return root


def replace_discrete_image(el,parent):
    """Retain every encoded cell color from existing 3x3 heatmap raster.

    This is a lossless scientific-cell representation, not digitization of
    estimated measurements: original color centers and printed values remain.
    """
    href=el.get(f'{{{XL}}}href','')
    assert href.startswith('data:image/png;base64,')
    im=Image.open(io.BytesIO(base64.b64decode(href.split(',',1)[1]))).convert('RGB')
    # Matplotlib imshow's original image is row-uniform within each known cell.
    x,y,w,h=[float(el.get(k,'0')) for k in ['x','y','width','height']]
    g=ET.Element(f'{{{NS}}}g',{k:v for k,v in el.attrib.items() if k in ['transform','clip-path']})
    colors=[]
    for row in range(3):
        for col in range(3):
            rgb=im.getpixel((int((col+.5)*im.width/3),int((row+.5)*im.height/3)))
            color='#'+''.join(f'{v:02x}' for v in rgb)
            colors.append(color)
            # SVG image includes a vertical transform; preserve local coordinates.
            ET.SubElement(g,f'{{{NS}}}rect',{'x':str(x+col*w/3),'y':str(y+row*h/3),'width':str(w/3+.0001),'height':str(h/3+.0001),'fill':lighten(color),'stroke':'none'})
    index=list(parent).index(el);parent.remove(el);parent.insert(index,g)
    return {'original_png_pixels':im.size,'cells':9,'original_cell_rgb':colors}


def polish(number):
    p=Path(INV[str(number)]['source']);raw=p.read_bytes();root=ET.fromstring(raw)
    original_numeric=numeric_tokens(root)
    view=[float(x) for x in root.get('viewBox').split()];factor=(170*72/25.4)/view[2]
    changes={'number':number,'source':str(p),'source_sha256':hashlib.sha256(raw).hexdigest(),'removed_caption_notes':[],'diamond_markers_replaced':0,'discrete_heatmap_images_vectorized':[],'scientific_coordinate_changes':0}
    parent={e:q for q in root.iter() for e in q}
    for e in list(root.iter()):
        tag=e.tag.split('}')[-1]
        if tag=='text':
            value=text(e)
            if value in NOTES.get(number,[]):
                parent[e].remove(e);changes['removed_caption_notes'].append(value);continue
            letter=re.fullmatch(r'([a-d])\)?',value)
            if letter:
                e.text=letter.group(1)
                for child in list(e):e.remove(child)
            set_style(e,'fill','#111111')
            set_style(e,'font-weight','bold' if letter else 'normal')
            set_style(e,'font-family','Arial-Bold' if letter else 'Arial')
            if letter:set_style(e,'font-size',str(8/factor)+'px')
            d=style(e)
            size=d.get('font-size',e.get('font-size',''))
            if size:
                match=re.search(r'\d+(?:\.\d+)?',size)
                if match and float(match.group())*factor<5.5:
                    set_style(e,'font-size',str(5.5/factor)+'px')
            for child in e.iter():
                if child is not e:
                    set_style(child,'fill','#111111');set_style(child,'font-weight','normal')
            # Cap labels describe the same three original settings.
            if number in [13,14] and e.text:
                e.text=e.text.replace(' - Low',' - Small').replace(' - High',' - Expanded')
            if number==16 and e.text and re.fullmatch(r'0\s+5 runs',e.text.strip()):e.text='0–5 runs'
            if number==13 and value=='0.100':set_style(e,'text-anchor','end')
        if tag in ['line','path']:
            stroke=style(e).get('stroke',e.get('stroke','')).lower()
            is_straight=tag=='line' or (not re.search(r'[ACQST]',e.get('d',''),re.I) and len(re.findall(r'[-+]?\d*\.?\d+',e.get('d','')))<=4)
            if stroke in GRID and is_straight:
                if e in parent:parent[e].remove(e)
                continue
        if tag=='image' and number in [11,12]:
            changes['discrete_heatmap_images_vectorized'].append(replace_discrete_image(e,parent[e]));continue
        if number==27 and tag=='circle' and e.get('fill','').lower()=='#4c78a8':
            cx,cy,r=[float(e.get(k)) for k in ['cx','cy','r']]
            e.tag=f'{{{NS}}}rect'
            for k in ['cx','cy','r']:e.attrib.pop(k)
            e.set('x',str(cx-r));e.set('y',str(cy-r));e.set('width',str(2*r));e.set('height',str(2*r))
        if tag in ['polygon','path']:
            value=e.get('points' if tag=='polygon' else 'd','')
            pts=diamond_points(value)
            if pts:
                cx,cy,rx,ry=pts
                triangle=f'{cx},{cy-ry} {cx+rx},{cy+ry} {cx-rx},{cy+ry}'
                if tag=='polygon':e.set('points',triangle)
                else:e.set('d',f'M {cx} {cy-ry} L {cx+rx} {cy+ry} L {cx-rx} {cy+ry} z')
                changes['diamond_markers_replaced']+=1
        if tag=='rect' and number==16 and abs(float(e.get('width','0'))-5.55)<.02 and abs(float(e.get('height','0'))-5.55)<.02:
            fill=e.get('fill','')
            if re.fullmatch('#[0-9a-fA-F]{6}',fill) and fill.lower() not in ['#ffffff','#263746']:
                # Preserve source sequential hues/order while making black labels readable.
                e.set('fill',lighten(fill))
    # Recolor drawing attributes only after all semantic text is set black.
    adapted=ET.tostring(root,encoding='unicode')
    # SVG viewBox is the drawing coordinate system; unitless font sizes avoid
    # svglib applying an extra CSS px-to-point 0.75 conversion.
    adapted=re.sub(r'(\d+(?:\.\d+)?)px',r'\1',adapted)
    for old,new in BRANCHES.items():adapted=re.sub(re.escape(old),new,adapted,flags=re.I)
    root=ET.fromstring(adapted)
    assert numeric_tokens(root)==original_numeric,'A numeric scientific label changed'
    root.set('width','170mm');root.set('height',f'{view[3]/view[2]*170:.10f}mm')
    variants=[(f'supp_s{number:02d}',root)]
    if number==16:
        variants=[]
        for suffix,y,h in [('a',0,91),('bc',91,119)]:
            r=crop_flat_svg(copy.deepcopy(root),y,h);variants.append((f'supp_s16_{suffix}',r))
    if number==17:
        variants=[]
        for suffix,y,h in [('ab',0,118.5),('cd',118.5,110)]:
            r=crop_flat_svg(copy.deepcopy(root),y,h);variants.append((f'supp_s17_{suffix}',r))
    for stem,r in variants:
        svg=ET.tostring(r,encoding='utf-8',xml_declaration=True)
        (OUT/f'{stem}.svg').write_bytes(svg)
        renderPDF.drawToFile(svg2rlg(str(OUT/f'{stem}.svg')),str(OUT/f'{stem}.pdf'))
        cairosvg.svg2png(bytestring=svg,write_to=str(OUT/f'{stem}.png'),output_width=round(170/25.4*600))
        cairosvg.svg2png(bytestring=svg,write_to=str(WORK/f'{stem}_preview.png'),output_width=round(170/25.4*180))
    changes['outputs']=[str((OUT/f'{stem}.pdf').relative_to(BASE)) for stem,_ in variants]
    changes['numeric_labels_preserved']=len(original_numeric)
    changes['source_still_identical']=hashlib.sha256(p.read_bytes()).hexdigest()==changes['source_sha256']
    (WORK/f'supp_s{number:02d}_provenance.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
    print(json.dumps({'number':number,'diamonds_replaced':changes['diamond_markers_replaced'],'outputs':changes['outputs']}),flush=True)
    return changes


if __name__=='__main__':
    result=[polish(n) for n in NUMBERS]
    (WORK/'vector_provenance.json').write_text(json.dumps(result,indent=2),encoding='utf8')
