#!/usr/bin/env python3
"""Generuje content/youtube.html (graf + tabulka zhlédnutí záznamů zastupitelstva).

Videa bere z odkazů na YouTube v jednani/pecky-jednani.json (jen zastupitelstvo),
počty zhlédnutí čte z veřejných stránek videí. Po běhu: python3 scripts/build.py
a přepsat lastmod 'youtube' v EXTRA_PAGES ve scripts/build.py.
Použití: python3 jednani/update-youtube.py
"""
import json,re,datetime,urllib.request,sys,os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TODAY=datetime.date.today()
data=json.load(open('jednani/pecky-jednani.json',encoding='utf-8'))
rows=[]
for mm in data['meetings']:
    if mm['type']!='Zastupitelstvo': continue
    ln=mm['links']
    url=ln.get('youtube') or ln.get('livestream') or ''
    m=re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})',url)
    if not m: continue
    i=m.group(1)
    h=urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/watch?v='+i,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'cs'}),timeout=30).read().decode()
    vm=re.search(r'"viewCount":"(\d+)"',h)
    if not vm: print('CHYBA: nelze přečíst zhlédnutí',mm['label'],i,file=sys.stderr); continue
    d=datetime.date.fromisoformat(mm['date'])
    rows.append((d,int(vm.group(1)),str(mm['number'])+'/'+str(mm['year']),i))
rows.sort()
ust=next(r for r in rows if r[0].isoformat()=='2022-10-20')
W,H,L,R,T,B=960,330,44,950,22,50
mx=max(1000,-(-max(r[1] for r in rows)//200)*200);pl=H-B-T;n=len(rows);step=(R-L)/n;bw=step*0.7
s=[]
for v in range(0,mx+1,200):
    y=T+pl*(1-v/mx)
    s.append(f'        <line x1="{L}" x2="{R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>\n        <text x="{L-6}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{v}</text>')
s.append('        <text x="2" y="12" text-anchor="start" font-size="11" fill="var(--ink-soft)">zhlédnutí</text>')
for k,(d,v,lab,i) in enumerate(rows):
    x=L+k*step+(step-bw)/2;h=pl*v/mx;y=T+pl-h
    u=d==ust[0];col='var(--gold)' if u else 'var(--burgundy)'
    extra=' – ustavující zasedání po volbách' if u else ''
    ttl=f'ZM {lab} ({d.day}. {d.month}. {d.year}){extra}: {v} zhlédnutí'
    s.append(f'        <a class="fb-bar" href="https://www.youtube.com/watch?v={i}" target="_blank" rel="noopener"><title>{ttl}</title><rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}"/><rect x="{x:.1f}" y="{T}" width="{bw:.1f}" height="{pl}" fill="transparent"/></a>')
    s.append(f'        <text x="{x+bw/2:.1f}" y="{y-3:.1f}" text-anchor="middle" font-size="9.5" fill="var(--ink-soft)">{v}</text>')
    s.append(f'        <text transform="translate({x+bw/2+3:.1f},{T+pl+8}) rotate(-60)" text-anchor="end" font-size="10" fill="var(--ink-soft)">{lab}</text>')
tot=sum(r[1] for r in rows)
MES=['ledna','února','března','dubna','května','června','července','srpna','září','října','listopadu','prosince']
od=MES[rows[0][0].month-1]+' '+str(rows[0][0].year);do=MES[rows[-1][0].month-1]+' '+str(rows[-1][0].year)
dnes=f'{TODAY.day}. {TODAY.month}. {TODAY.year}'
top=sorted(rows,key=lambda r:-r[1])
t1=f'ZM {top[0][2]} ({top[0][1]})';t2=f'ZM {top[1][2]} ({top[1][1]})'

svg='\n'.join(s)
html=f'''  <style>
    .fb-chart{{margin:18px 0 4px;}}
    .fb-chart svg{{display:block; max-width:100%; height:auto;}}
    .fb-legend{{list-style:none; margin:0 0 6px; padding:0; display:flex; flex-wrap:wrap; gap:4px 16px; font-size:12.5px; color:var(--ink-soft);}}
    .fb-legend li{{display:inline-flex; align-items:center; gap:6px;}}
    .fb-sw{{display:inline-block; width:12px; height:12px; border-radius:2px;}}
    .fb-bar{{cursor:pointer;}}
    .fb-bar:hover rect,.fb-bar:focus-visible rect{{opacity:.78;}}
    .fb-bar:focus-visible{{outline:2px solid var(--gold); outline-offset:1px;}}
  </style>
  <section class="panel active" id="panel-youtube">
    <h2 class="title display">Zhlédnutí záznamů zastupitelstva</h2>
    <p class="lede">Počet zhlédnutí videozáznamů jednání zastupitelstva na YouTube. Přehled obsahuje {len(rows)} záznamů od {od} do {do}, dohromady {format(tot,',').replace(',',' ')} zhlédnutí.</p>

    <figure class="fb-chart">
      <ul class="fb-legend" aria-label="Legenda grafu">
        <li><span class="fb-sw" style="background:var(--burgundy)"></span>Řádné zasedání</li>
        <li><span class="fb-sw" style="background:var(--gold)"></span>Ustavující zasedání po volbách (20. 10. 2022)</li>
      </ul>
      <svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="yt-t yt-d">
        <title id="yt-t">Zhlédnutí záznamů zastupitelstva</title>
        <desc id="yt-d">Sloupcový graf: osa x jednotlivá zasedání zastupitelstva v časovém pořadí, osa y počet zhlédnutí videozáznamu na YouTube. Nejvíc zhlédnutí má {t1}, druhé {t2}.</desc>
{svg}
      </svg>
    </figure>

    <p class="meta-note">Počty zhlédnutí jsou čtené z veřejných stránek videí na YouTube k {dnes} a u novějších záznamů dál rostou. Zahrnuta jsou jen videa, na která odkazuje sekce Jednání. Sloupce odkazují na videa; číslování zasedání odpovídá sekci Jednání.</p>
  </section>
'''
open('content/youtube.html','w',encoding='utf-8').write(html)

print(f'OK: {len(rows)} záznamů, celkem {tot} zhlédnutí; nejvíc {t1}; stav k {dnes}')
