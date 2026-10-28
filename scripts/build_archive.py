#!/usr/bin/env python3
"""Build the static archive from the source-checked NRHA roster; no runtime service."""
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://reininghalloffame.com'
ROSTER = 'https://nrha.com/hall-fame/'
NEWS = 'https://nrha.com/news/'
HOF26 = NEWS + 'national-reining-horse-association-announces-2026-hall-of-fame-inductees/'
HOF25 = NEWS + 'national-reining-horse-association-announces-2025-hall-of-fame-inductees-and-dale-wilkinson-lifetime-achievement-award-honorees/'
AWARD26 = NEWS + 'national-reining-horse-association-honors-dan-huss-and-duane-latimer-with-dale-wilkinson-lifetime-achievement-award/'
MILESTONES = 'https://nrha.com/milestones/'
DATA = json.loads((ROOT / 'data/honorees.json').read_text())
ROWS = DATA['honorees']
BY_SLUG = {r['slug']: r for r in ROWS if r['category'] != 'award'}
for r in ROWS:
    r['path'] = ('lifetime-achievement/' if r['category'] == 'award' else 'hall-of-fame/') + r['slug'] + '/'

# Brief biographies paraphrase the linked NRHA announcements. Financial figures
# are deliberately dated to the announcement, rather than presented as live totals.
BIOS = {
 'cheryl-cody': (HOF25, 'A writer, photographer and event professional, Cheryl Cody has served the reining community for more than four decades. The lifetime NRHA member co-founded Rein In Cancer and leads Pro Management Inc., supporting major reining events and programs for exhibitors and young people.', ['NRHA Hall of Fame, Class of 2025.', 'Co-founder and president of Rein In Cancer.', 'President of Pro Management Inc.']),
 'best-stop': (HOF25, 'Best Stop, by Custom Crome out of Rest Stop, combines an influential pedigree with a proven production record. NRHA’s August 2025 announcement credited the Wagman Ranch mare with offspring earnings exceeding $1 million and 19 NRHA money earners, including Best Shine.', ['NRHA Hall of Fame, Class of 2025.', 'Sire: Custom Crome. Dam: Rest Stop.', 'Dam of Best Shine; granddam of Gunnastop.']),
 'chexanicki': (HOF25, 'Chexanicki earned more than $86,000 in NRHA competition and won multiple Non Pro titles. NRHA’s August 2025 announcement recognized both her show record and offspring earnings exceeding $1 million. The mare was owned by Toyon Ranch LLC at the time of that announcement.', ['NRHA Hall of Fame, Class of 2025.', 'Successful Non Pro competitor and producing mare.', 'Offspring include Alpha Jac Sparrow, Chexi Chic and Rufanicki.']),
 'mike-hancock': (HOF26, 'Mike Hancock’s contribution to reining spans competition, volunteer leadership and philanthropy. A two-term NRHA president, he has supported youth development, scholarships and the Reining Horse Foundation while helping guide the association through periods of change and growth.', ['Selected for the NRHA Hall of Fame Class of 2026.', 'Two-term NRHA president.', 'Reining Horse Foundation Double Platinum Lifetime Donor.']),
 'tom-mccutcheon': (HOF26, 'Tom McCutcheon has helped shape reining as a competitor, breeder, mentor and industry organizer. His contributions include helping establish the National Reining Breeders Classic and Legacy Sale, serving NRHA in leadership roles, and supporting development of its Foal Nomination Program.', ['Selected for the NRHA Hall of Fame Class of 2026.', 'World Equestrian Games team gold medalist and individual world champion.', 'NRHA Two Million Dollar Rider and Two Million Dollar Owner at the August 2026 announcement.']),
 'bob-santagata': (HOF26, 'Robert “Bob” Santagata has supported reining through horse ownership, philanthropy and investment in its future. His involvement includes the NRHA Futurity Impact Group, support for affiliates and the Reining Horse Foundation, and educational opportunities at Santa Hill Ranch.', ['Selected for the NRHA Hall of Fame Class of 2026.', 'Founding member of the NRHA Futurity Impact Group.', 'NRHA Two Million Dollar Owner at the August 2026 announcement.']),
 'americasnextgunmodel': (HOF26, 'Americasnextgunmodel, by Gunner out of Cee Dun It Do It, won the 2012 NRHA Open Futurity with Casey Deary. Her influence continued through offspring including Belissimo and Americasnexttopgun, with production earnings exceeding $1.7 million in NRHA’s August 2026 announcement.', ['Selected for the NRHA Hall of Fame Class of 2026.', '2012 NRHA Open Futurity champion.', 'Owned by Arcese Quarter Horses USA; bred by David Silva Jr.']),
 'this-chicsdundreamin': (HOF26, 'This Chicsdundreamin, known as “Lexi,” succeeded in both Open and Non Pro competition before becoming an influential producer. By Magnum Chic Dream out of Hermosa Dun It, she was bred by Joe Hayes and owned by Rhodes River Ranch. NRHA recognized offspring earnings exceeding $1 million.', ['Selected for the NRHA Hall of Fame Class of 2026.', 'Offspring include Tinker With Dreams and Trashinyurdreams.', 'Recognized for competitive ability, disposition and production.']),
 'jeff-petska': (HOF25, 'Jeff Petska combined a lifetime in horsemanship with leadership of United States reining teams. As chef d’équipe, he helped guide five consecutive World Equestrian Games team gold medals. His work also included NRHA committee service, mentoring riders and founding Whitesboro Equine Therapy with his wife, Lisa.', ['2025 Dale Wilkinson Lifetime Achievement Award recipient.', 'Served on NRHA’s board and committees.', 'Recognized posthumously; Petska died in 2022.']),
 'larry-kasten': (HOF25, 'Larry Kasten’s career brings together competition, judging and education. After teaching at West Texas State University, he joined the University of Wisconsin–River Falls in 1973. His horses and students have achieved national success, reflecting a lasting commitment to horsemanship and mentorship.', ['2025 Dale Wilkinson Lifetime Achievement Award recipient.', 'NRHA Futurity finalist and Super Stakes Limited Open winner.', 'AQHA and NRHA judge and longtime educator.']),
 'dan-huss': (AWARD26, 'Dan Huss has spent more than four decades developing horses and riders. A student of Dale Wilkinson at Findlay College, he later spent 19 years on its faculty. His accomplishments include the 2018 World Equestrian Games team gold and individual silver medals, alongside a lasting reputation as a teacher.', ['2026 Dale Wilkinson Lifetime Achievement Award recipient.', '1987 NRHA Futurity Limited Open champion.', 'His bridleless 2018 AQHA World Show run followed an equipment malfunction.']),
 'duane-latimer': (AWARD26, 'Canadian horseman Duane Latimer has influenced reining across North America and Europe as a competitor and mentor. An NRHA Futurity champion, AQHA world champion and World Equestrian Games medalist, he has helped develop riders and professionals while strengthening the sport’s international reach.', ['2026 Dale Wilkinson Lifetime Achievement Award recipient.', 'NRHA Two Million Dollar Rider at the August 2026 announcement.', 'Recognized for horsemanship, mentorship and international impact.']),
}

def esc(s): return html.escape(str(s), quote=True)

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')

def label(r):
    return 'Dale Wilkinson Lifetime Achievement Award' if r['category'] == 'award' else 'NRHA Hall of Fame'

def initials(name):
    return ''.join(w[0] for w in re.findall(r'[A-Za-z]+', name)[:2]).upper()

def header():
    return '''<header class="site-header"><a href="/" class="header-brand"><div class="header-logo" aria-hidden="true">&#127943;</div><div class="header-title">Reining Hall of Fame<span>Editorial Archive</span></div></a><a href="https://bridleandbit.com" class="header-bb"><img src="https://imagedelivery.net/9VlM7Y9GaQMXOu5Ypg50yA/bb-hp-0/public" alt="Bridle &amp; Bit" height="26"></a></header>'''

def footer():
    return '''<footer class="site-footer"><div class="footer-logo">Reining Hall of Fame</div><nav class="footer-nav" aria-label="Site navigation"><a href="/">Home</a><a href="/hall-of-fame/">Hall of Fame</a><a href="/horses/">Horses</a><a href="/riders/">People</a><a href="/lifetime-achievement/">Lifetime Achievement</a><a href="/history/">History</a></nav><p class="footer-disc">An independent editorial archive presented by Bridle &amp; Bit. Not affiliated with or officially endorsed by NRHA.</p><p class="footer-copy">&copy; 2026 Bridle &amp; Bit. All rights reserved.</p></footer>'''

def document(title, description, path, body, schema=None):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{esc(title)} | Reining Hall of Fame</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#3D2414"><link rel="canonical" href="{BASE}/{path}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}/{path}"><meta name="robots" content="index, follow">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;800;900&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/archive.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-S5J3LDH3T8"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-S5J3LDH3T8');</script>
{('<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('<','\\u003c')+'</script>') if schema else ''}</head><body>{header()}<div class="back-bar"><a href="/hall-of-fame/">&#8592; Hall of Fame</a><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a></nav></div><main>{body}</main>{footer()}</body></html>'''

def source_note(url=ROSTER):
    return f'<p class="verified-note">Checked October 28, 2026. <a href="{esc(url)}">Read the official NRHA source</a>.</p>'

def profile(r):
    award = r['category'] == 'award'
    record = BIOS.get(r['slug'])
    source = record[0] if record else ROSTER
    if record:
        bio, highlights = record[1:]
    else:
        verb = 'is listed by NRHA as a recipient of the Dale Wilkinson Lifetime Achievement Award' if award else 'is listed on NRHA’s official Hall of Fame roster'
        bio = f'{r["name"]} {verb} for {r["year"]}. This archive follows NRHA’s published recognition year and award category.'
        highlights = [f'{label(r)}, {r["year"]}.', 'Recognition confirmed against NRHA’s official published roster.']
    notice = ''
    if r['year'] == 2026:
        notice = '<p class="detail-narrative" style="margin-bottom:20px">Announced for 2026. Formal recognition is scheduled for December 2, 2026, at Sliders’ Night Out presented by Toyon Ranch in Oklahoma City.</p>'
    if r['previous_year']:
        notice += '<p class="detail-narrative" style="margin-bottom:20px">NRHA marks this listing with an asterisk indicating the award was made in a previous year. The year shown here follows the official roster listing.</p>'
    peers = [x for x in ROWS if x['year'] == r['year'] and (x['category'] == 'award') == award and x['path'] != r['path']]
    badge = ('Award ' if award else 'HOF ') + str(r['year'])
    body = f'''<article><div class="detail-hero"><div class="detail-photo-container"><div class="detail-initials" aria-hidden="true">{initials(r['name'])}</div><div class="detail-photo-overlay"><div class="detail-year-badge">{badge}</div><h1 class="detail-name">{esc(r['name'])}</h1><div class="detail-tagline">{label(r)}</div></div></div></div><div class="detail-cat-bar"><span class="detail-cat-label">{('Lifetime Achievement' if award else ('Horse' if r['category']=='horse' else 'Person / organization'))} &middot; {r['year']}</span></div><div class="detail-content">{notice}<section class="detail-section"><h2 class="detail-section-title">About {esc(r['name'])}</h2><div class="detail-narrative">{esc(bio)}</div></section><section class="detail-section"><h2 class="detail-section-title">Recognition &amp; Highlights</h2><ul class="hl-list">{''.join('<li class="hl-item">'+esc(h)+'</li>' for h in highlights)}</ul></section>{source_note(source)}<a class="hof-link-btn" href="/{'lifetime-achievement/' if award else 'hall-of-fame/'}">Browse {'Lifetime Achievement recipients' if award else 'the Hall of Fame archive'} &#8594;</a><section class="class-section"><h2 class="detail-section-title">{'Award recipients' if award else 'Hall of Fame class'} of {r['year']}</h2><div class="peers-grid">{''.join('<a class="peer-link" href="/'+p['path']+'">'+esc(p['name'])+'</a>' for p in peers) or '<span class="peer-link">'+esc(r['name'])+'</span>'}</div></section></div></article>'''
    schema = {'@context':'https://schema.org','@type':'WebPage','name':r['name']+' — '+label(r)+' '+str(r['year']),'url':BASE+'/'+r['path'],'description':bio,'citation':source,'dateModified':DATA['verified_on']}
    write(r['path']+'index.html', document(r['name']+' — '+label(r)+' '+str(r['year']),bio,r['path'],body,schema))

def rows_html(rows):
    return ''.join(f'<a class="archive-row" data-search="{esc(r["name"].lower())} {r["year"]}" href="/{r["path"]}"><strong>{esc(r["name"])}</strong><span>{r["year"]} &middot; {"Lifetime Achievement" if r["category"]=="award" else "Horse" if r["category"]=="horse" else "Person / organization"}</span></a>' for r in rows)

NAV = '<nav class="archive-nav" aria-label="Archive categories"><a href="/hall-of-fame/">All inductees</a><a href="/horses/">Horses</a><a href="/riders/">People &amp; organizations</a><a href="/lifetime-achievement/">Lifetime Achievement</a><a href="/hall-of-fame/2026-inductees/">2026 class</a><a href="/hall-of-fame/2025-inductees/">2025 class</a></nav>'

def listing(path, title, intro, rows, extra=''):
    body = f'<div class="detail-hero"><div class="detail-photo-container" style="height:210px"><div class="detail-photo-overlay"><h1 class="detail-name">{esc(title)}</h1></div></div></div><div class="detail-content"><div class="detail-narrative">{intro}</div>{NAV}{extra}<label for="archive-search">Find a name or year</label><input id="archive-search" class="archive-search" type="search" placeholder="Search names or years" aria-controls="archive-results"><p id="result-count" class="verified-note" aria-live="polite">{len(rows)} records</p><div id="archive-results">{rows_html(rows)}</div>{source_note()}</div><script>const input=document.getElementById("archive-search");input.addEventListener("input",()=>{{const q=input.value.toLowerCase().trim();let count=0;document.querySelectorAll(".archive-row").forEach(row=>{{row.hidden=!row.dataset.search.includes(q);if(!row.hidden)count++}});document.getElementById("result-count").textContent=count+" records";}});</script>'
    write(path+'index.html',document(title,html.unescape(re.sub('<[^>]+>','',intro)),path,body))

def article_page(path,title,intro,sections):
    body=f'<div class="detail-hero"><div class="detail-photo-container" style="height:210px"><div class="detail-photo-overlay"><h1 class="detail-name">{esc(title)}</h1></div></div></div><div class="detail-content"><div class="detail-narrative">{intro}</div>{NAV}'
    for heading,text,url in sections:
        body+=f'<section class="detail-section" style="margin-top:24px"><h2 class="detail-section-title">{esc(heading)}</h2><div class="detail-narrative">{text}</div>{source_note(url)}</section>'
    write(path+'index.html',document(title,intro,path,body+'</div>'))

def build():
    for r in ROWS: profile(r)
    hall = sorted([r for r in ROWS if r['category'] != 'award'],key=lambda r:(-r['year'],r['name']))
    awards = sorted([r for r in ROWS if r['category'] == 'award'],key=lambda r:(-r['year'],r['name']))
    yearnav = '<nav class="archive-nav" aria-label="Browse by year">'+''.join(f'<a href="/hall-of-fame/{y}-inductees/">{y}</a>' for y in sorted({r['year'] for r in hall},reverse=True))+'</nav>'
    listing('hall-of-fame/','NRHA Hall of Fame Archive','Explore the people, organizations and horses on NRHA’s official Hall of Fame roster, from the first class in 1986 through the announced class of 2026. The Dale Wilkinson Lifetime Achievement Award is recorded separately.',hall,yearnav)
    listing('horses/','Hall of Fame Horses','Explore the horses recognized on NRHA’s official Hall of Fame roster. Each record links to its recognition year and an official source.',[r for r in hall if r['category']=='horse'])
    listing('riders/','Hall of Fame People & Organizations','Explore the horsemen, horsewomen and organizations recognized by NRHA. Hall of Fame membership honors contributions across competition, breeding, leadership and service; it does not imply that every honoree is a rider or trainer.',[r for r in hall if r['category']=='person'])
    listing('trainers/','Hall of Fame Horsemen & Horsewomen','NRHA’s people and organizations roster includes competitors, trainers, breeders and contributors. Browse the official recognition records below.',[r for r in hall if r['category']=='person'])
    listing('lifetime-achievement/','Dale Wilkinson Lifetime Achievement Award','This NRHA honor recognizes lasting contributions to reining. It is a distinct award, separate from induction into the NRHA Hall of Fame. Some recipients have received both honors in different years.',awards)
    for year in sorted({r['year'] for r in hall} | {2021,2022,2023,2024,2025,2026}):
        intro=f'The {year} NRHA Hall of Fame class, following NRHA’s official roster. Lifetime Achievement recipients are listed separately.'
        if year==2026: intro+=' The class was announced August 28, 2026; formal recognition is scheduled for December 2, 2026, at Sliders’ Night Out presented by Toyon Ranch in Oklahoma City.'
        listing(f'hall-of-fame/{year}-inductees/',f'NRHA Hall of Fame — Class of {year}',intro,[r for r in hall if r['year']==year])
    article_page('history/','Reining History','Key dates in NRHA history, checked against the association’s published milestones.',[
      ('1966 — NRHA is formed','The National Reining Horse Association was formed in 1966 and incorporated on November 30 of that year.',MILESTONES),
      ('1966 — The first NRHA Futurity','The first Futurity took place in Columbus, Ohio. Dale Wilkinson rode Pocorochie Bo to the championship in a field of 24 entries.',MILESTONES),
      ('1986 — Oklahoma City and the Hall of Fame','The Futurity moved to Oklahoma City in 1986. NRHA also established its Hall of Fame that year, with Dale Wilkinson as the first inductee.',MILESTONES),
      ('2026 — Sixty years of reining','NRHA and its Futurity mark their 60th anniversaries in 2026. The latest Hall of Fame class includes three people and two horses. <a href="/hall-of-fame/2026-inductees/">Meet the 2026 class.</a>',NEWS+'nrha-celebrates-60-years-of-excellence-in-2026/')])
    article_page('bloodlines/','Hall of Fame Bloodlines','Explore a selection of documented family connections among influential reining horses.',[
      ('Best Stop','By Custom Crome out of Rest Stop, Best Stop joined the Hall of Fame in 2025. NRHA’s announcement highlights five Hall of Fame horses in her pedigree. <a href="/hall-of-fame/best-stop/">Read her record.</a>',HOF25),
      ('Americasnextgunmodel','The 2026 honoree is by Gunner out of Cee Dun It Do It. Her offspring include Belissimo and Americasnexttopgun. <a href="/hall-of-fame/americasnextgunmodel/">Read her record.</a>',HOF26),
      ('This Chicsdundreamin','By Magnum Chic Dream out of Hermosa Dun It, this 2026 honoree produced Tinker With Dreams and Trashinyurdreams. <a href="/hall-of-fame/this-chicsdundreamin/">Read her record.</a>',HOF26)])
    article_page('champions/','Champions & Official Records','Selected championship milestones and primary sources for further research.',[
      ('The first Futurity champion','Dale Wilkinson and Pocorochie Bo won the first NRHA Futurity in Columbus, Ohio, in 1966.',MILESTONES),
      ('Americasnextgunmodel — 2012','Casey Deary rode Americasnextgunmodel to the 2012 NRHA Open Futurity championship. She was selected for the 2026 Hall of Fame class.',HOF26),
      ('NRHA championship records','Consult NRHA’s published Futurity champions and reserve champions record for year-by-year results.', 'https://nrha.com/wp-content/uploads/2025/07/Futurity_Champions.pdf')])
    article_page('million-dollar-sires/','NRHA Million Dollar Earners','Official NRHA recognition records provide the reference for earnings milestones.',[
      ('Keep earnings tied to an official source','Sire, rider and owner milestones are different measures. They should not be combined with earnings reported by other associations. Visit NRHA’s Million Dollar Earners page for its published records.','https://nrha.com/million-dollar-earners/')])
    article_page('legendary-runs/','Hall of Fame Stories & Records','Read official accounts of the people and horses who shaped reining.',[
      ('The 2026 Hall of Fame class','NRHA’s announcement recounts the careers of Mike Hancock, Tom McCutcheon, Bob Santagata, Americasnextgunmodel and This Chicsdundreamin.',HOF26),
      ('Horsemanship and mentorship','Read NRHA’s account of Dan Huss and Duane Latimer, including Huss’s bridleless 2018 AQHA World Show performance.',AWARD26),
      ('Championship results','Explore NRHA’s published Futurity champions and reserve champions record.','https://nrha.com/wp-content/uploads/2025/07/Futurity_Champions.pdf')])
    # Consolidate misspellings and misclassified old URLs without losing inbound links.
    aliases={'stretch-bradley':'bailey-stretch-bradley','ct-fuller':'c-t-tom-fuller','rd-baker':'r-d-baker','fleuterio-arcese':'eleuterio-arcese','custom-chrome':'custom-crome','n-keith-bradley':'keith-bradley','jodieann':'nifty-jodieann','wimpy-chic':'wimpys-little-chic'}
    redirects=['/hall-of-fame /hall-of-fame/ 301']
    for old,new in aliases.items():
        redirects.append(f'/hall-of-fame/{old}/* /hall-of-fame/{new}/ 301')
    for r in awards:
        if not any(x['slug']==r['slug'] for x in hall): redirects.append(f'/hall-of-fame/{r["slug"]}/* /{r["path"]} 301')
    # Gabriel Diano is absent from NRHA's published roster. Do not preserve a false induction claim.
    redirects.append('/hall-of-fame/gabriel-diano/* /hall-of-fame/2015-inductees/ 301')
    for line in redirects[1:]:
        old=line.split()[0].removesuffix('*')+'index.html'
        p=ROOT/old.lstrip('/')
        if p.exists(): p.unlink()
    write('_redirects','\n'.join(redirects)+'\n')
    update_home(hall,awards)
    paths=sorted('/'+str(p.relative_to(ROOT)).removesuffix('index.html') for p in ROOT.rglob('index.html') if '.git' not in p.parts)
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+esc(p)+'</loc><lastmod>'+DATA['verified_on']+'</lastmod></url>' for p in paths)+'</urlset>\n')
    write('robots.txt','User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')

def replace_section(s, marker, content):
    return re.sub(r'<!-- '+re.escape(marker)+r' -->.*?</section>',lambda m:'<!-- '+marker+' -->\n'+content,s,count=1,flags=re.S)

def home_card(r,kind):
    name=esc(r['name']); year=r['year']; url='/'+r['path']
    desc=esc(BIOS[r['slug']][1]) if r['slug'] in BIOS else f'NRHA Hall of Fame, Class of {year}. Recognition confirmed by NRHA’s official roster.'
    if kind=='legend': return f'<a class="legend-card" role="listitem" href="{url}" style="text-decoration:none"><div class="legend-photo" aria-hidden="true"><div class="legend-initials">{initials(r["name"])}</div></div><div class="legend-right"><span class="legend-badge">HOF {year}</span><h3 class="legend-name">{name}</h3><div class="legend-type">{r["category"]} &middot; Hall of Fame</div><p class="legend-desc">NRHA Hall of Fame, Class of {year}.</p><div class="legend-arrow" aria-hidden="true">&#8594;</div></div></a>'
    if kind=='horse': return f'<a class="horse-card" role="listitem" href="{url}" style="text-decoration:none"><div class="horse-photo"><div class="horse-initials" aria-hidden="true">&#128052;</div><div class="horse-photo-overlay"><div class="horse-era">Hall of Fame &middot; {year}</div></div></div><div class="horse-card-body"><h3 class="horse-name">{name}</h3><div class="horse-tag">NRHA Hall of Fame horse</div><span class="horse-achievement">Class of {year}</span></div></a>'
    return f'<a class="trainer-card" role="listitem" href="{url}" style="text-decoration:none"><div class="trainer-avatar" aria-hidden="true">{initials(r["name"])}</div><h3 class="trainer-name">{name}</h3><div class="trainer-role">NRHA Hall of Fame</div><p class="trainer-stat">Class of {year}. Explore this honoree’s official recognition record.</p><span class="trainer-badge">HOF {year}</span></a>'

def home_section(cls,id,title,subtitle,inside):
    return f'<section class="{cls}" aria-labelledby="{id}"><div class="section-header"><h2 id="{id}">{title}</h2><span class="gold-rule"></span><p>{subtitle}</p></div>{inside}</section>'

def update_home(hall,awards):
    s=(ROOT/'index.html').read_text()
    stats=[('60','Years of NRHA'),(str(len(hall)),'HOF Records'),(str(len(awards)),'Award Records'),(str(sum(r['category']=='horse' for r in hall)),'HOF Horses')]
    s=re.sub(r'<!-- STATS BAR -->.*?<!-- NAV BOXES -->','<!-- STATS BAR -->\n<div class="stats-bar" role="region" aria-label="Archive at a glance">'+''.join(f'<div><div class="stat-num">{num}</div><div class="stat-label">{text}</div></div>' for num,text in stats)+'</div>\n\n<!-- NAV BOXES -->',s,flags=re.S)
    featured=[BY_SLUG[x] for x in ['mike-hancock','tom-mccutcheon','bob-santagata','americasnextgunmodel','this-chicsdundreamin']]
    s=replace_section(s,'FEATURED LEGENDS',home_section('','legends-heading','Meet the Announced Class of 2026','Three people and two horses selected for NRHA’s highest honor. Formal recognition: December 2, 2026.', '<div class="legends-scroll"><div class="legends-track" role="list">'+''.join(home_card(r,'legend') for r in featured)+'</div></div>'))
    horses=[BY_SLUG[x] for x in ['shining-spark','hollywood-dun-it','gunner-colonels-smoking-gun','topsail-whiz','best-stop','chexanicki','americasnextgunmodel','this-chicsdundreamin']]
    s=replace_section(s,'HISTORIC HORSES',home_section('horses-section','horses-heading','Historic Reining Horses','Explore influential horses on NRHA’s official Hall of Fame roster.','<div class="horse-grid" role="list">'+''.join(home_card(r,'horse') for r in horses)+'</div><div style="text-align:center;padding:0 16px 24px"><a href="/horses/">View All Hall of Fame Horses &#8594;</a></div>'))
    people=[BY_SLUG[x] for x in ['dale-wilkinson','shawn-flarida','andrea-fappani','bill-horn','cheryl-cody','mike-hancock','tom-mccutcheon','bob-santagata']]
    s=replace_section(s,'RIDERS & TRAINERS',home_section('riders-section','riders-heading','Hall of Fame People','Horsemen, horsewomen and contributors whose achievements helped build reining.','<div class="trainer-grid" role="list">'+''.join(home_card(r,'trainer') for r in people)+'</div><div style="text-align:center;padding:0 16px 24px"><a href="/riders/">View All Hall of Fame People &#8594;</a></div>'))
    timeline=[('1966','NRHA Is Founded','The National Reining Horse Association is formed and incorporated.'),('1966','First NRHA Futurity','Dale Wilkinson and Pocorochie Bo win the first Futurity in Columbus, Ohio.'),('1986','The Futurity Moves to Oklahoma City','The Futurity moves from Columbus to Oklahoma City.'),('1986','The Hall of Fame Begins','Dale Wilkinson becomes the first NRHA Hall of Fame inductee.'),('2026','Sixty Years of NRHA','The association and its Futurity celebrate their 60th anniversaries.')]
    items=''.join(f'<div class="timeline-item" role="listitem"><div class="timeline-year">{y}</div><div class="timeline-dot" aria-hidden="true"></div><div class="timeline-content"><h3 class="timeline-title">{t}</h3><p class="timeline-desc">{d}</p></div></div>' for y,t,d in timeline)
    s=replace_section(s,'TIMELINE',home_section('timeline-section','timeline-heading','Timeline of Reining History','Milestones checked against NRHA’s published history.','<div class="timeline" role="list">'+items+'</div><div style="text-align:center;padding:0 16px 24px"><a href="/history/">Explore Full Reining History &#8594;</a></div>'))
    links=[('2026','Announced Hall of Fame Class of 2026','/hall-of-fame/2026-inductees/','Mike Hancock, Tom McCutcheon, Bob Santagata and two horses'),('2025','Hall of Fame Class of 2025','/hall-of-fame/2025-inductees/','Cheryl Cody, Best Stop and Chexanicki'),('2024','Hall of Fame Class of 2024','/hall-of-fame/2024-inductees/','Andrea Fappani, Snow Gun, Wind Her Up Chic and Wind Her Up Shiner'),('Award','Lifetime Achievement Recipients','/lifetime-achievement/','A separate honor: Dan Huss and Duane Latimer selected for 2026'),('All','Full Hall of Fame Archive','/hall-of-fame/','Browse every published class since 1986')]
    cards=''.join(f'<a class="inductee-row" role="listitem" href="{u}" style="text-decoration:none"><div class="inductee-year-badge">{y}</div><div class="inductee-info"><div class="inductee-name">{t}</div><div class="inductee-category">{d}</div></div><div class="inductee-arrow" aria-hidden="true">&#8250;</div></a>' for y,t,u,d in links)
    s=replace_section(s,'INDUCTEES',home_section('champions-section','inductees-heading','Latest Hall of Fame Honorees','Current classes and recognition records, checked October 28, 2026.','<div class="inductees-list" role="list">'+cards+'</div>'))
    stories=[('The 2026 Hall of Fame Class',HOF26,'Official NRHA announcement'),('The 2025 Hall of Fame Class',HOF25,'Official NRHA announcement'),('Dan Huss & Duane Latimer',AWARD26,'2026 Lifetime Achievement recipients')]
    cards=''.join(f'<a class="video-card" role="listitem" href="{u}" style="text-decoration:none"><div class="video-thumb" aria-hidden="true"><span class="video-label">NRHA Record</span><span style="color:var(--gold);font-size:40px">&#9733;</span></div><div class="video-body"><h3 class="video-title">{t}</h3><div class="video-meta">{d}</div></div></a>' for t,u,d in stories)
    s=replace_section(s,'VIDEOS',home_section('','videos-heading','Hall of Fame Stories & Records','Read the official accounts behind reining’s latest honors.','<div class="video-scroll"><div class="video-track" role="list">'+cards+'</div></div><div style="text-align:center;padding:0 16px 24px"><a href="/legendary-runs/">Explore Stories & Records &#8594;</a></div>'))
    s=s.replace('&copy; 2024 Bridle','&copy; 2026 Bridle').replace('>Legendary Runs</a>','>Stories &amp; Records</a>')
    s=s.replace('<!-- ABOUT BANNER -->','<p style="text-align:center;padding:12px 16px;font-size:13px;color:var(--text-light)">Roster checked October 28, 2026. <a href="'+ROSTER+'">Official NRHA Hall of Fame roster</a>. Lifetime Achievement is recorded separately.</p>\n<!-- ABOUT BANNER -->') if 'Roster checked October 28' not in s else s
    write('index.html',s)

if __name__=='__main__':
    build()
    print(f'Built {sum(r["category"]!="award" for r in ROWS)} Hall of Fame records and {sum(r["category"]=="award" for r in ROWS)} Lifetime Achievement records.')
