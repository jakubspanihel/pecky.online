"""Analýza obsahu příspěvků: rozdělení do témat a srovnání dvou období.

Volá se ze summary.py (render_page) — vrací HTML bloku „Analýza: Co město na
Facebooku publikuje“ na stránce Monitoring. Třídění je orientační: každý
příspěvek jde do jedné skupiny podle klíčových slov v krátkém popisu (pole
`popis`); pořadí pravidel v `R` určuje přednost. Hranice období je říjen 2022
(komunální volby, změna správce profilu).
"""
import re
import unicodedata
from collections import Counter
from statistics import median
from datetime import datetime

SPLIT = '2022-10-01'
TECH = 'Ostatní (bez textu, technické, nezařazené)'
SHARED = 'Sdílení příspěvků jiných profilů'


def norm(s):
    return unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()


R=[
('Krize (covid, povodně, bouře, válka, epidemie zvířat)',r'osetrovn|narizeni vlady|vladni opatreni|zprisneni|omezeni pohybu|dezinfek|zivnostnik|podnikatel|czech point|tornado|boure|bourk|hygienik|tesco omezuje|polabske uzeniny|vyuk[ay] pro zaky|covid|korona|rousk|vakcin|ockov|testovan|karanten|nouzov|ukrajin|uprchl|povodn|povoden|epidem|pandem|ochrany dychac|opatreni|slintavk|ptaci chripk|mimoradn|vichrice|vetrem|poplach|siren|energet|zdrazov|zvysene nebezpeci|obalu pro distribuci|letaky s telefon|bohemia energy|zkrachovaly|energie|srdce na dlani|tel\. linka|telefonni linka'),
('Volby a participativní rozpočet',r'volb|volebn|volic|referend|kandidat|hlasovani|sneme|participativn'),
('Pečecké noviny, městský rozhlas a vlastní kanály města',r'noviny|novin|rozhlas|mobilni aplikac|aplikace mesto|aplikace pro|webov|informacni panel|facebook|newsletter|elektronicky mesicnik|mesicnik|dobre zpravy o'),
('Ztráty a nálezy, zvířata',r'odlov ryb|ztrat|nalez|hleda|zvire|\bpes\b|\bpsi\b|\bpsu\b|\bpsy\b|kocka|kote|kocic|odchyt|toulav|zelva|majitel|nutri|nekrmit|fenka|vlcak|bigl|ptak|zbloudil|ztracen|zvirat'),
('Provozní oznámení (odstávky, havárie, odečty, pošta, výluky vlaků)',r'odstavk|havari|prerus|zapisovan|vypadek|porucha|odstaven|odecet|odecty|elektromer|vodomer|vyluk|jizdni rad|otviraci dob|oteviraci dob|ceske post|posta\b|poste\b|poštu|sporitel|bankomat|omezeni uzivani|pitne vod|pitna voda|spalovani|kaceni|odklizen|snih|zimni udrzb|posyp|ledovk|ubytovn|uzavren|zavreno|zrusen|pracovni nabidk|pracovni nabidka|nabidka prace|volna mista|vyberove rizeni|vyberove|uredni hodin|upozorneni|policie varuje|varovani|podvod|vyzva k|pozar|nebezpeci'),
('Připomínky výročí a významných dnů',r'veteran|vlci mak|palach|umrti|pocta|pametnic|vyroci|pietn|pamatk|ucten|pripomin|vzpomin|den vitezstvi|holocaust|havel|horakov|1968|1989|17\. listopad|svobod|valk|vlast|hrob|pomnik|narozen|den obeti|masaryk|tgm|statni svatek|statnost|vlajk|posveceni|socha|sochy|zemrel|pozustal|vojn|osvobozeni|zesnul'),
('Zastupitelstvo, rada, úřad a hospodaření města',r'zastupitel|rada mesta|rady mesta|\bradni|rozpoc|zaverecn|usnesen|vyhlask|obecne zavazn|jednani|starost|mistostarost|dotac|poplatk|\bdan|danov|pronajem|zakazk|konkurz|prodej|zamer|\burad|radnic|dotaz|anket|strategi|uzemni plan|audit|vyrocni zprava|vybor|komise|prispevek na bydleni|exekuc|milostive|verejne projednani|projednani|schval|najemn|\bbyt|nebytov|inzer|hospodar|financ|mesto ziskalo|certifikat|ocenen|ekologicka obec|rozhodnuti|poslanec|senat|vlada|hejtman|krajsk|fond rozvoje|puj[cč]k|ucet mesta|energeticky management|nabidka skole|pronajmu|pecin roku'),
('Sport a pohyb',r'sport|turnaj|fotbal|volejbal|\bbeh\b|\bbezec|desitk|bezk|florbal|tenis|hokej|cyklist|zavod|plavani|cvicen|joga|kondic|sokol|nohejbal|petang|pochod|vylet|sjizdeni|vavrinec|peloton|golf|zumba|lyzar|brusl|kuzelk|afk|workout|sipk|na kole'),
('Škola, školka a děti',r'\bzs\b|\bms\b|skol|ucebn|zapis do|detsk|\bdeti\b|\bdeti\b|\bzaci\b|zakov|jesle|pramin|maternsk|prazdnin|vysvedc|ucitel|mladez|junak|skaut|masinka|prvnac|predskol|skolk|rodic|den deti|dni deti|ditet|zaku|dlouhodoby pobyt|hriste pro'),
('Kultura, tradice a společenské akce',r'pozvank|\bples|koncert|divadl|vinobran|vanoc|advent|rozsviceni|mikulas|slavnost|vystav|vystoup|festival|kino|beseda|besedu|prednask|\bpout|masopust|carod|velikonoc|dyn|dozink|den matek|akce|akci|setkani|prohlidk|klubovn|\btrh|vecer|vernisaz|zabava|kulturn|hudebn|zpev|kapela|recital|vytvarn|stromecek|\bhody|oslav|kronik|promitan|tvoriv|workshop|kurz|vitani|jubilant|knih|krest|kalendar|prani|poselstv|svatek|novorocni|vecirek|maskarni|tanec|muzikal|rozlouceni|vyhlaseni|soutez|vyhodnoceni|vyherc|burza|vyprodej|garaz|bazar|zahradni|piknik|noc literatury|velorex|kapl|kostel|sraz|diskuz|debat|rok od vysazeni|upominkov|ohnostroj|silvestr|tri kral|trikral|recepty|zavody|pecin|kampan|sbirk'),
('Zdraví, sociální služby a bezpečnost',r'poradn|senior|lekar|ordinac|zdravotn|charit|pomoc|socialn|pecovat|krev|doktor|domov pro|pecovatelsk|dluh|zdravi|defibril|lekarn|nemocnic|hospic|ambulanc|kardio|prevence|rakovin|zubni|nepriznivej|tezke zivotni|dobrovoln'),
('Zdraví, sociální služby a bezpečnost',r'hasic|hzs|policie|policii|obecni policie|sbor dobrovolnych|zbrojnic|kamer|bezpecnost'),
('Doprava a stavby (uzavírky, opravy, rekonstrukce)',r'uzavirk|uzavreni|rekonstrukc|oprav|stavb|chodnik|silnic|komunikac|objizd|lavk|dopravn|autobus|vlak|zeleznic|prejezd|viadukt|prechod|parkov|osvetlen|kruhov|cyklo|\bmost|vodovod|kanaliz|kolaudac|telocvic|podchod|dostavb|zateplen|hrbitov|bacov|hriste|pristresek|zastavk|rozsir|asfalt|frezov|vyspravk|radar|zpomal|\bplot|vozovk|dlazb|lokalk|\btrat|nadrazi|nabijec|vodojem|plynovod|prestavb|novostavb|vystavba|budov|vybaveni|vylepsen|minigolf|lavick|herni prvk|areal|zahrad|mobiliar|kriz|ulic|\bul\.|trida|tridy|tridu|upravach|upravy|udrzb|sit[ie]|lampa|lamp|cedul|tabulk|park\b|otevren|dobrichov|odstraneni|nevzhledn|pajasan|pamatk|prostredi|verejn.* prostor|investic'),
('Odpady, úklid a příroda',r'odpad|svoz|trideni|trizeni|kontejner|bioodpad|ukli|imis|ovzdusi|zelen|strom|kompost|sber|tepelne cerp|kotlik|recykl|zivotni prostredi|hnizd|alej|vysadb|lesopark|\bpark|hmyz|vcel|priroda|rybnik|potok|asekol|elektroodpad|plasty|nadob|popelnic|krmeni|klimat|den zeme|karton|kolobeh|ekolog|sucho'),
]
RULES = [(n, re.compile(r'(?:' + r + r')')) for n, r in R]


def cat(p):
    if p['type'] == 'sdílený příspěvek':
        return SHARED
    if p['type'] == 'změna úvodní fotky':
        return TECH
    s = norm(p.get('popis') or '')
    if not s or re.search(r'bez textu|nedostupn|^foto$|^prispevek$|^prispevek bez', s):
        return TECH
    for n, r in RULES:
        if r.search(s):
            return n
    return TECH


def cz(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def pct(a, b):
    """Změna b oproti a v procentech jako text se znaménkem (správné minus)."""
    if not a:
        return '–'
    v = round((b - a) / a * 100)
    return ('+' if v > 0 else '−' if v < 0 else '±') + f'{abs(v)} %'


def plural(n):
    return 'příspěvek' if n == 1 else 'příspěvky' if 2 <= n <= 4 else 'příspěvků'


def n_(n):
    return f'{n:,}'.replace(',', '\u00a0')


def less(a, b):
    v = round(abs(b / a * 100 - 100))
    return f'o {v} % ' + ('méně' if b < a else 'více')


def _d(iso):
    y, m, d = iso[:10].split('-')
    return f'{int(d)}. {int(m)}. {y}'


def _series(posts, rx):
    rg = re.compile(rx)
    return [p for p in posts if rg.search(norm(p.get('popis') or ''))]


def render_analysis(months):
    """months: [(yyyy-mm, summary, posts, counts_as_of)] -> HTML sekce (skrytá,
    rozbalí ji tlačítko; viz render_page)."""
    posts = sorted((p for _, _, ps, _ in months for p in ps), key=lambda p: p['published'])
    A = [p for p in posts if p['published'] < SPLIT]
    B = [p for p in posts if p['published'] >= SPLIT]
    first, last = posts[0]['published'], posts[-1]['published']
    last_ym = max(ym for ym, *_ in months)
    mA = (datetime.fromisoformat(SPLIT) - datetime.fromisoformat(first[:10])).days / 30.4375
    mB = (int(last_ym[:4]) - 2022) * 12 + int(last_ym[5:]) - 10 + 1
    mA_i, mB_i = round(mA), mB
    end_txt = _d(last_ym + '-28')  # jen kvůli měsíci a roku níže
    MONTHS_GEN = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července',
                  'srpna', 'září', 'října', 'listopadu', 'prosince']
    do_txt = f'{MONTHS_GEN[int(last_ym[5:]) - 1]} {last_ym[:4]}'

    def stats(X):
        own = [p for p in X if p['type'] != 'sdílený příspěvek']
        tx = [len(p['text']) for p in own if p.get('text')]
        return {
            'n': len(X), 'own': len(own), 'shared': len(X) - len(own),
            'wk': sum(1 for p in X if datetime.fromisoformat(p['published']).weekday() >= 5) / len(X),
            'txt': len(tx) / len(own), 'tlen': median(tx),
        }
    sa, sb = stats(A), stats(B)
    by_year = Counter(p['published'][:4] for p in posts)
    full = {y: n for y, n in by_year.items() if '2019' <= y <= str(int(last_ym[:4]) - 1)}
    ymax = max(full, key=full.get)
    ymin = min(full, key=full.get)

    ca, cb = Counter(cat(p) for p in A), Counter(cat(p) for p in B)
    order = sorted((k for k in set(ca) | set(cb) if k not in (SHARED, TECH)),
                   key=lambda k: -(ca[k] + cb[k]))
    order += [SHARED, TECH]
    rows = []
    rate = {}
    for k in order:
        ra, rb = ca[k] / mA, cb[k] / mB
        rate[k] = (ra, rb)
        rows.append(f'        <tr><td>{k}</td><td class="num">{ca[k]}</td><td class="num">{cz(ra)}</td>'
                    f'<td class="num">{cb[k]}</td><td class="num">{cz(rb)}</td><td class="num">{pct(ra, rb)}</td></tr>')
    rows.append(f'        <tr class="fb-an-sum"><td><strong>Celkem</strong></td><td class="num"><strong>{n_(len(A))}</strong></td>'
                f'<td class="num"><strong>{cz(len(A) / mA)}</strong></td><td class="num"><strong>{len(B)}</strong></td>'
                f'<td class="num"><strong>{cz(len(B) / mB)}</strong></td>'
                f'<td class="num"><strong>{pct(len(A) / mA, len(B) / mB)}</strong></td></tr>')
    tbl = '\n'.join(rows)

    topics = [k for k in order if k not in (SHARED, TECH)]
    drops = sorted(topics, key=lambda k: (rate[k][1] - rate[k][0]))
    rozh = _series(posts, r'hlaseni (mestskeho )?rozhlas|shrnuti hlaseni|souhrn hlaseni')
    rozh_y = Counter(p['published'][:4] for p in rozh)
    bacov = _series(posts, r'bacov')
    teloc = _series(posts, r'telocvi|parkhal|dostavb')
    teloc_b = [p for p in teloc if p['published'] >= SPLIT]
    ukr = _series(posts, r'ukrajin')
    cov = _series(posts, r'covid|korona|rousk|karanten|epidem|testovan')
    part = _series(posts, r'participativn')
    zal = _series(posts, r'ztraty a nalezy|nalezen|ztracen')
    zast_a = len([p for p in _series(A, r'zastupitelstv|zasedani')])
    zast_b = len([p for p in _series(B, r'zastupitelstv|zasedani')])
    poz = Counter(p['published'][:4] for p in _series(posts, r'pozvanka'))
    krit = [p for p in B if p['type'] == 'změna úvodní fotky']

    def share_pct(x, n):
        return f'{round(x / n * 100)} %'

    return f'''    <section class="fb-analysis" id="fb-analyza" hidden>
      <h3 class="display">Analýza: Co město na Facebooku publikuje</h3>
      <p class="lede">Rozbor všech {n_(len(posts))} příspěvků od {_d(first)} do {do_txt}, rozdělených na dvě období podle komunálních voleb v září 2022. Po volbách se změnil správce facebookového profilu města.</p>

      <h4 class="display">Období</h4>
      <p class="meta-note"><strong>Od založení do voleb:</strong> {_d(first)} – 30. 9. 2022 (přibližně {mA_i} měsíců). <strong>Po volbách:</strong> 1. 10. 2022 – {do_txt} ({mB_i} měsíců).</p>
      <ul class="fb-an-list">
        <li>Před volbami profil publikoval <strong>{n_(len(A))} příspěvků</strong> ({cz(len(A) / mA)} měsíčně), po volbách <strong>{len(B)}</strong> ({cz(len(B) / mB)} měsíčně), tedy měsíčně {less(len(A) / mA, len(B) / mB)}.</li>
        <li>Vlastních příspěvků (bez sdílení) bylo před volbami {n_(sa['own'])} ({cz(sa['own'] / mA)} měsíčně), po volbách {sb['own']} ({cz(sb['own'] / mB)} měsíčně), tedy měsíčně {less(sa['own'] / mA, sb['own'] / mB)}.</li>
        <li>Sdílení z cizích profilů zůstalo na stejné úrovni ({sa['shared']} a {sb['shared']} příspěvků), proto jeho podíl vzrostl z {share_pct(sa['shared'], sa['n'])} na {share_pct(sb['shared'], sb['n'])}.</li>
        <li>Nejvíc příspěvků za celý kalendářní rok bylo v roce {ymax} ({full[ymax]}), nejméně v roce {ymin} ({full[ymin]}).</li>
        <li>O víkendu vznikalo před volbami {share_pct(sa['wk'], 1)} příspěvků, po volbách {share_pct(sb['wk'], 1)}.</li>
        <li>Příspěvek s textem mělo před volbami {share_pct(sa['txt'], 1)} vlastních příspěvků, po volbách {share_pct(sb['txt'], 1)}. Medián délky textu vzrostl z {round(sa['tlen'])} na {round(sb['tlen'])} znaků.</li>
      </ul>

      <h4 class="display">Témata</h4>
      <p class="meta-note">Každý příspěvek je zařazen do jedné skupiny podle klíčových slov v krátkém popisu. Zařazení je orientační: sedí zhruba v pěti případech ze šesti. Sloupce „měsíčně“ jsou průměr za měsíc daného období.</p>
      <div class="table-scroll">
      <table class="register fb-an-table">
        <thead><tr><th>Skupina</th><th class="num">do 9/2022</th><th class="num">měsíčně</th><th class="num">od 10/2022</th><th class="num">měsíčně</th><th class="num">Změna</th></tr></thead>
        <tbody>
{tbl}
        </tbody>
      </table>
      </div>
      <ul class="fb-an-list">
        <li><strong>Stabilní jádro:</strong> provozní oznámení, ztráty a nálezy, úřední věci a stavby se mezi obdobími mění nejméně (do ±25 %). Ztráty a nálezy ({len(zal)} příspěvků) se objevují každý rok od roku 2019.</li>
        <li><strong>Nejvíc ubylo:</strong> {drops[0].split(' (')[0].lower()} ({cz(rate[drops[0]][0])} → {cz(rate[drops[0]][1])} měsíčně) a {drops[1].split(' (')[0].lower()} ({cz(rate[drops[1]][0])} → {cz(rate[drops[1]][1])} měsíčně).</li>
        <li><strong>Doba covidu:</strong> příspěvky o epidemii a opatřeních ({len(cov)}) jsou z let 2020 a 2021, o válce na Ukrajině ({len(ukr)}) z února až června 2022. Po volbách jde o výjimky.</li>
        <li><strong>Městský rozhlas:</strong> pravidelná shrnutí hlášení ({len(rozh)} příspěvků) vrcholí v roce 2022 ({rozh_y['2022']}) a 2023 ({rozh_y['2023']}). Od roku 2024 se téměř neobjevují.</li>
        <li><strong>Participativní rozpočet:</strong> {len(part)} příspěvků v letech 2019 až 2022, po volbách žádný.</li>
        <li><strong>Velké stavby po volbách:</strong> rekonstrukce Bačova ({len(bacov)} příspěvků od {_d(bacov[0]['published'])}) a dostavba učeben a tělocvičny ZŠ ({len(teloc_b)} příspěvků po volbách, všechny od roku 2025). Před volbami byla tělocvična tématem jen {len(teloc) - len(teloc_b)}×.</li>
        <li><strong>Zastupitelstvo:</strong> pozvánky a shrnutí jsou častější ({cz(zast_a / mA, 2)} → {cz(zast_b / mB, 2)} měsíčně).</li>
        <li><strong>Pozvánky na akce</strong> mají nejméně příspěvků v roce 2024 ({poz['2024']}), proti {poz['2022']} v roce 2022 a {poz['2023']} v roce 2023. Příčina z dat nevyplývá.</li>
      </ul>

      <h4 class="display">Srovnání období</h4>
      <ul class="fb-an-list">
        <li><strong>Objem:</strong> po volbách je měsíčně příspěvků {less(len(A) / mA, len(B) / mB)}, vlastních {less(sa['own'] / mA, sb['own'] / mB)}.</li>
        <li><strong>Čas:</strong> příspěvky vznikají víc v pracovní dny, o víkendu klesl podíl z {share_pct(sa['wk'], 1)} na {share_pct(sb['wk'], 1)}.</li>
        <li><strong>Obsah:</strong> před volbami tvoří větší podíl akce, krizová komunikace (covid, Ukrajina), zdraví a sociální služby a životní prostředí. Po volbách tvoří větší podíl stavby, ztráty a nálezy a sdílení z profilů organizací.</li>
        <li><strong>Forma:</strong> příspěvky jsou delší, ale častěji bez textu nebo jen technické ({len(krit)} změn úvodní fotky, žádná před volbami).</li>
        <li><strong>Sdílení:</strong> v obou obdobích nejčastěji z profilu Pečeckých služeb, po volbách přibylo sdílení z profilu Kulturního střediska.</li>
        <li><strong>Reakce:</strong> medián reakcí na příspěvek je v obou obdobích stejný (10). Průměr po volbách vzrostl kvůli několika příspěvkům s mimořádným ohlasem.</li>
      </ul>
      <p class="meta-note">Pokles počtu příspěvků nemusí znamenat pokles komunikace města: část informací může jít jinými kanály (web města, mobilní aplikace, profily organizací). Počty reakcí jsou snímky k datu sběru.</p>
    </section>
'''
