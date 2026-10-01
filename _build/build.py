"""Génère les pages secondaires du site (blog, articles, galerie, histoire, boutique, contact).

Usage : python3 _build/build.py <dossier_scrape>
Le dossier de scrape contient blog/*.html (articles originaux) et blog-1.html, blog-p2.html, blog-p3.html.
"""
import glob, html, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
ORIG = "https://www.latelierinspire.fr"
STORE_ID = "93909024"

NAV = [("blog.html", "Blog"), ("boutique.html", "Boutique"), ("histoire.html", "L'histoire"),
       ("galerie.html", "Galerie"), ("contact.html", "Contact")]


def head(title, desc, prefix=""):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="{prefix}img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css?v=12">
</head>
"""


def header(active, prefix=""):
    links = "\n".join(
        f'        <li><a href="{prefix}{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a></li>' for h, t in NAV)
    return f"""<body>
<a class="skip" href="#main">Passer au contenu principal</a>
<div class="scrollbar" aria-hidden="true"><span></span></div>
<header class="nav" id="nav">
  <div class="nav__inner">
    <a href="{prefix}index.html" class="nav__logo" aria-label="L'Atelier Inspiré — accueil">
      <img src="{prefix}img/logo.png" alt="" width="36" height="41"><span>L'Atelier Inspiré</span>
    </a>
    <nav aria-label="Navigation principale">
      <ul class="nav__links" id="menu">
{links}
      </ul>
    </nav>
    <a href="{prefix}boutique.html" class="btn btn--sm nav__cta">Commander</a>
    <button class="nav__burger" id="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="menu">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg>
    </button>
  </div>
</header>
"""


def footer(prefix=""):
    return f"""
<footer class="footer">
  <div class="container footer__grid">
    <div>
      <img src="{prefix}img/logo.png" alt="L'Atelier Inspiré — Honorer dignement ses proches" width="96" height="110" loading="lazy">
    </div>
    <div>
      <h2>Contact</h2>
      <ul>
        <li><a href="tel:0658760255">06 58 76 02 55</a></li>
        <li><a href="mailto:laetitia@latelierinspire.fr">laetitia@latelierinspire.fr</a></li>
        <li><a href="https://www.instagram.com/latelierinspire.fr" rel="noopener">Instagram</a></li>
      </ul>
    </div>
    <div>
      <h2>Navigation</h2>
      <ul>
{"".join(f'        <li><a href="{prefix}{h}">{t}</a></li>{chr(10)}' for h, t in NAV)}      </ul>
    </div>
  </div>
  <p class="container footer__copy">© L'Atelier Inspiré — Fabrication française et artisanale, Rhône-Alpes. <a href="{prefix}contact.html#cgv">Conditions générales de vente</a></p>
</footer>
<script src="{prefix}main.js?v=12" defer></script>
</body>
</html>
"""


def page(path, title, desc, active, body, prefix=""):
    with open(os.path.join(ROOT, path), "w") as f:
        f.write(head(title, desc, prefix) + header(active, prefix) + body + footer(prefix))
    print("écrit", path)


def dl(url, dest, size=1400):
    full = os.path.join(ROOT, dest)
    if not os.path.exists(full):
        os.makedirs(os.path.dirname(full), exist_ok=True)
        try:
            urllib.request.urlretrieve(url, full)
            subprocess.run(["sips", "-Z", str(size), full], capture_output=True)
        except Exception as e:
            print("échec", url, e)
            return None
    return dest


def dims(rel):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", os.path.join(ROOT, rel)],
                         capture_output=True, text=True).stdout
    w = re.search(r"pixelWidth: (\d+)", out)
    h = re.search(r"pixelHeight: (\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else (1200, 800)


EMOJI_IMG = re.compile(r'<img[^>]*class="emoji"[^>]*>(</img>)?')
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿️‍]")
MONTHS = {}

# ---------- BLOG ----------
articles = []
for f in glob.glob(os.path.join(SRC, "blog", "*.html")):
    slug = os.path.basename(f)[:-5]
    s = open(f).read()
    meta = s.find('class="post-meta"')
    title = html.unescape(re.sub(r"<[^>]+>", "", re.findall(r"<h2>(.*?)</h2>", s[:meta])[-1])).strip()
    date_iso = re.search(r'<time class="post-date" datetime="([^"]+)">([^<]+)</time>', s)
    feat = re.search(r'<img[^>]*src="([^"]+)"[^>]*class="post-content-image', s)
    a = s.find("</div>", meta) + 6
    rest = s[a:]
    # fin = fermeture du conteneur post-content-wrapper (on suit la profondeur des <div>)
    depth, end = 0, len(rest)
    for m in re.finditer(r"<div\b|</div>|<aside\b", rest):
        if m.group(0) == "<aside":
            end = m.start(); break
        depth += 1 if m.group(0) == "<div" else -1
        if depth < 0:
            end = m.start(); break
    body = re.sub(r"</?div[^>]*>", "", rest[:end])
    body = EMOJI_IMG.sub("", body)
    body = EMOJI.sub("", body)
    body = re.sub(r'\s(class|style|id|decoding|fetchpriority|srcset|sizes|role)="[^"]*"', "", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"<(h3|h2)>\s*<strong>\s*(.*?)</strong>\s*</\1>", r"<\1>\2</\1>", body, flags=re.S)
    body = re.sub(r"<p>\s*(&nbsp;)?\s*</p>", "", body)

    imgs = []
    def repl(m, slug=slug, imgs=imgs):
        n = len(imgs) + 1
        tag = m.group(0)
        url = re.search(r'src="([^"]+)"', tag).group(1)
        alt = (re.search(r'alt="([^"]*)"', tag) or [None, ""])[1]
        if url.startswith("/"):
            url = ORIG + url
        ext = ".png" if url.lower().endswith(".png") else ".jpg"
        rel = dl(url, f"img/blog/{slug}-{n}{ext}")
        imgs.append(rel)
        w, h = dims(rel) if rel else (1200, 800)
        return f'<img src="../{rel}" alt="{alt}" width="{w}" height="{h}" loading="lazy">'
    body = re.sub(r'<img\b[^>]*>(</img>)?', repl, body)
    body = re.sub(r"<strong>\s*</strong>", "", body)
    body = re.sub(r"<figure>", '<figure class="clip">', body)
    body = body.replace(f'href="{ORIG}/blog-1/', 'href="').replace('href="/blog-1/', 'href="')
    body = re.sub(r'href="([a-z0-9-]+)/"', r'href="\1.html"', body)
    body = body.replace(f'href="{ORIG}/boutique/', 'href="../boutique.html" data-orig="')
    body = re.sub(r"\n{2,}", "\n", body).strip()

    cover = dl(feat.group(1), f"img/blog/{slug}-cover.jpg", 1800) if feat else None
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"\s+", " ", text).strip()
    excerpt = text[:200].rsplit(" ", 1)[0] + "…"
    words = len(text.split())
    articles.append(dict(slug=slug, title=title, iso=date_iso.group(1), date=date_iso.group(2).replace(". ", " "),
                         cover=cover, body=body, excerpt=excerpt, minutes=max(1, round(words / 220))))

articles.sort(key=lambda x: x["iso"], reverse=True)

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

for i, a in enumerate(articles):
    nxt = articles[(i + 1) % len(articles)]
    cover = (f'<figure class="article__cover"><img src="../{a["cover"]}" alt="" width="{dims(a["cover"])[0]}" '
             f'height="{dims(a["cover"])[1]}" fetchpriority="high"></figure>') if a["cover"] else ""
    body = f"""<div class="readbar" aria-hidden="true"><span></span></div>
<main id="main" tabindex="-1" class="article">
  <header class="article__head container">
    <a class="back" href="../blog.html"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>Tous les articles</a>
    <p class="eyebrow reveal"><time datetime="{a['iso']}">{a['date']}</time> · {a['minutes']} min de lecture</p>
    <h1 class="display split">{html.escape(a['title'])}</h1>
  </header>
  {cover}
  <article class="prose container">
{a['body']}
  </article>
  <aside class="next container">
    <a href="{nxt['slug']}.html" class="next__card">
      <span class="eyebrow">Article suivant</span>
      <span class="next__title">{html.escape(nxt['title'])}</span>
      {ARROW}
    </a>
  </aside>
</main>"""
    page(f"blog/{a['slug']}.html", f"{a['title']} — L'Atelier Inspiré", a["excerpt"], "blog.html", body, "../")

cards = []
for i, a in enumerate(articles):
    w, h = dims(a["cover"]) if a["cover"] else (0, 0)
    img = (f'<div class="post__img clip"><img src="{a["cover"]}" alt="" width="{w}" height="{h}" loading="lazy"></div>'
           if a["cover"] else "")
    cls = "post post--feature" if i == 0 else "post"
    cards.append(f"""    <li class="{cls} reveal">
      <a href="blog/{a['slug']}.html">
        {img}
        <div class="post__body">
          <p class="post__meta"><time datetime="{a['iso']}">{a['date']}</time> · {a['minutes']} min</p>
          <h2>{html.escape(a['title'])}</h2>
          <p>{html.escape(a['excerpt'])}</p>
          <span class="card__more">Lire l'article {ARROW}</span>
        </div>
      </a>
    </li>""")

page("blog.html", "Blog — L'Atelier Inspiré", "Conseils, inspirations et réflexions autour du deuil, de la mémoire et des objets commémoratifs personnalisés.",
     "blog.html", f"""<main id="main" tabindex="-1">
  <section class="pagehead container">
    <p class="eyebrow reveal">Le journal de l'atelier</p>
    <h1 class="mega split">Blog</h1>
    <p class="lead reveal">Conseils, inspirations et réflexions autour du deuil, de la mémoire et des hommages personnalisés.</p>
  </section>
  <ul class="posts container">
{chr(10).join(cards)}
  </ul>
</main>""")

# ---------- GALERIE ----------
gal = sorted(glob.glob(os.path.join(ROOT, "img/galerie/*.jpg")))
cols = [[], [], []]
for i, g in enumerate(gal):
    rel = os.path.relpath(g, ROOT)
    w, h = dims(rel)
    cols[i % 3].append(f'<figure class="gal__item"><button type="button" class="gal__btn" data-full="{rel}" aria-label="Agrandir la création {i + 1}">'
                       f'<img src="{rel}" alt="Création personnalisée L\'Atelier Inspiré n°{i + 1}" width="{w}" height="{h}" loading="lazy"></button></figure>')
pick = gal[::9][:12]
ring_html = "\n".join(
    f'          <li class="stack__card" style="--i:{k};--tilt:{[-4,3,-2,5,-5,2,-3,4,-1,3,-4,2][k % 12]}deg"><button type="button" class="gal__btn" data-full="{os.path.relpath(g, ROOT)}" aria-label="Agrandir la création {k + 1}">'
    f'<img src="{os.path.relpath(g, ROOT)}" alt="Création personnalisée L\'Atelier Inspiré" loading="lazy"></button></li>' for k, g in enumerate(pick))
# mini-photos flottantes autour de la pile : (gauche %, haut %, taille px, vitesse, rotation)
FLOATS = [(6, 14, 110, -260, -8), (20, 62, 80, 180, 6), (4, 78, 96, -120, 10), (28, 28, 64, 320, -4),
          (78, 10, 100, 220, 7), (88, 44, 76, -300, -10), (72, 70, 118, -160, 5), (90, 84, 70, 260, -6)]
float_html = "\n".join(
    f'        <li class="floaty" data-speed="{sp}" style="left:{x}%;top:{y}%;--sz:{sz}px;--rot:{r}deg">'
    f'<img src="{os.path.relpath(g, ROOT)}" alt="" loading="lazy"></li>' for (x, y, sz, sp, r), g in zip(FLOATS, gal[4::13]))
col_html = "\n".join(f'    <div class="gal__col" data-speed="{sp}">\n      ' + "\n      ".join(c) + "\n    </div>"
                     for c, sp in zip(cols, ("0", "-0.18", "0.08")))
page("galerie.html", "Galerie — L'Atelier Inspiré", "Créations uniques et personnalisées réalisées pour nos clients : galets, ardoises et pierres gravés.",
     "galerie.html", f"""<main id="main" tabindex="-1">
  <section class="pagehead container">
    <p class="eyebrow reveal">Galerie</p>
    <h1 class="mega split">Bienvenue dans notre galerie</h1>
    <p class="lead reveal">Vous y découvrirez des <strong>créations uniques et personnalisées</strong>, réalisées avec soin pour mes clients pour rendre hommage à leurs êtres chers. Chaque galet, chaque mot, chaque gravure porte une histoire, un lien, une émotion.</p>
    <p class="lead reveal">Laissez-vous inspirer par ces exemples pour imaginer <strong>votre propre message</strong>, simple ou poétique.</p>
  </section>
  <section class="stack" id="stack" aria-label="Sélection de créations">
    <div class="stack__sticky">
      <ul class="floaties" aria-hidden="true">
{float_html}
      </ul>
      <ul class="stack__pile" id="pile">
{ring_html}
      </ul>
      <p class="stack__count" aria-hidden="true"><span id="stackNum">01</span> / {len(pick):02d}</p>
    </div>
  </section>
  <div class="marquee" aria-hidden="true"><div class="marquee__track" data-marquee>Chaque galet · chaque mot · chaque gravure · porte une histoire · un lien · une émotion · Chaque galet · chaque mot · chaque gravure · porte une histoire · un lien · une émotion · </div></div>
  <section class="allgal container">
    <button type="button" class="btn btn--ghost" id="galToggle" aria-expanded="false" aria-controls="galAll">Voir toutes les créations ({len(gal)})</button>
    <div class="gal" id="galAll" hidden>
{col_html}
    </div>
  </section>
  <section class="cta container">
    <h2 class="display split">Imaginez votre propre message</h2>
    <a href="boutique.html" class="btn reveal">Commandez maintenant</a>
  </section>
</main>
<dialog class="lightbox" id="lightbox" aria-label="Image agrandie">
  <button type="button" class="lightbox__close" aria-label="Fermer"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <img alt="">
</dialog>""")

# ---------- HISTOIRE ----------
hw, hh = dims("img/histoire.jpg")
page("histoire.html", "L'histoire — L'Atelier Inspiré", "Laetitia, créatrice de L'Atelier Inspiré : l'histoire d'une boutique d'articles commémoratifs modernes et personnalisés, née en 2021.",
     "histoire.html", f"""<main id="main" tabindex="-1">
  <section class="pagehead container">
    <p class="eyebrow reveal">L'histoire</p>
    <h1 class="mega split">Mon histoire…</h1>
  </section>

  <section class="vid" id="vid">
    <div class="vid__sticky">
      <div class="vid__frame" id="vidFrame">
        <button type="button" class="vid__poster" id="vidPlay" aria-label="Lire la vidéo de présentation">
          <img src="img/bg3.jpg" alt="" loading="lazy">
          <span class="vid__play"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span>
          <span class="vid__note">La vidéo est hébergée sur YouTube. En cliquant, vous acceptez son chargement.</span>
        </button>
      </div>
    </div>
  </section>

  <section class="story container">
    <figure class="story__img clip"><img src="img/histoire.jpg" alt="Laetitia, fondatrice de L'Atelier Inspiré" width="{hw}" height="{hh}" loading="lazy"></figure>
    <div class="story__text">
      <p class="eyebrow reveal">Je me présente</p>
      <h2 class="display split">Laetitia</h2>
      <p class="lead reveal">48 ans, maman, dynamique, villeurbannaise et passionnée !</p>
      <p class="reveal">Il y a 5 ans, j'ai été confrontée à organiser et gérer les obsèques de mon papa, et je n'ai pas trouvé d'articles personnalisés qui apportent suffisamment d'émotion, d'apaisement, voire de poésie…</p>
      <p class="reveal">J'ai donc souhaité créer une gamme d'articles personnalisés pour ces périodes que nous traversons tous suite à la perte d'un proche.</p>
    </div>
  </section>

  <section class="timeline container" aria-label="Les étapes">
    <div class="timeline__line" aria-hidden="true"><span></span></div>
    <div class="tl reveal"><span class="tl__year">2021</span><p>« L'atelier inspiré » est sorti de terre (c'est le cas de le dire !) — une boutique d'articles commémoratifs plus modernes et personnalisés. Une activité qui a du sens.</p></div>
    <div class="tl reveal"><span class="tl__year">Exclusif</span><p>Les objets commémoratifs que j'ai imaginés sont tous des produits exclusifs et personnalisés sur demande. Un support durable et riche en symboles.</p></div>
    <div class="tl reveal"><span class="tl__year">Rhône-Alpes</span><p>Fabrication et gravure en Rhône-Alpes.</p></div>
  </section>

  <section class="promise">
    <div class="container promise__inner">
      <p class="eyebrow reveal">Notre promesse</p>
      <p class="words" data-words>Nous vous promettons bien plus qu'un simple cadeau. Notre engagement va bien au-delà. Nous sommes là pour vous aider à vous libérer d'une émotion qui sera à tout jamais gravée sur la pierre.</p>
      <p class="lead reveal">Ce cadeau, préparé avec soin et personnalisé, est notre promesse de vous accompagner dans ce voyage.</p>
      <p class="lead reveal">Votre patience et votre fidélité nous touchent profondément, tout comme votre soutien aux petits entrepreneurs français. Vous êtes au cœur de notre mission.</p>
      <p class="signature reveal">Merci à vous, Laetitia.</p>
    </div>
  </section>
</main>""")

# ---------- BOUTIQUE (widget Ecwid : panier et paiement restent ceux de la boutique) ----------
page("boutique.html", "Boutique — L'Atelier Inspiré", "Galets, ardoises et pierres funéraires gravés et personnalisés. Livraison rapide en 5 à 7 jours.",
     "boutique.html", f"""<main id="main" tabindex="-1">
  <section class="pagehead container">
    <p class="eyebrow reveal">Boutique</p>
    <h1 class="mega split">Des souvenirs gravés dans la pierre</h1>
    <p class="lead reveal">Livraison rapide (5 à 7 jours) ou moins sur demande.</p>
  </section>
  <div class="marquee" aria-hidden="true"><div class="marquee__track" data-marquee>Gravure personnalisée · Pierre naturelle · Fabrication française · Livraison 5 à 7 jours · Gravure personnalisée · Pierre naturelle · Fabrication française · Livraison 5 à 7 jours · </div></div>
  <section class="shop container">
    <div id="my-store-{STORE_ID}" class="shop__store">
      <div class="shop__loading" role="status"><span class="spinner" aria-hidden="true"></span>Chargement de la boutique…</div>
    </div>
    <noscript><p>La boutique nécessite JavaScript. <a href="{ORIG}/boutique/">Ouvrir la boutique</a></p></noscript>
  </section>
</main>
<script data-cfasync="false" type="text/javascript" src="https://app.ecwid.com/script.js?{STORE_ID}&data_platform=code" charset="utf-8"></script>
<script type="text/javascript">xProductBrowser("categoriesPerRow=3","views=grid(20,3) list(60) table(60)","categoryView=grid","searchView=list","id=my-store-{STORE_ID}");</script>""")

# ---------- CONTACT ----------
page("contact.html", "Contact — L'Atelier Inspiré", "Contactez Laetitia : 06 58 76 02 55, laetitia@latelierinspire.fr. Conditions générales de vente.",
     "contact.html", """<main id="main" tabindex="-1">
  <section class="pagehead container">
    <p class="eyebrow reveal">Contact</p>
    <h1 class="mega split">Contactez-nous</h1>
  </section>
  <section class="contact container">
    <div class="contact__info">
      <a class="contact__big reveal" href="tel:0658760255"><span>Téléphone</span>06 58 76 02 55</a>
      <a class="contact__big reveal" href="mailto:laetitia@latelierinspire.fr"><span>E-mail</span>laetitia@latelierinspire.fr</a>
      <a class="contact__big reveal" href="https://www.instagram.com/latelierinspire.fr" rel="noopener"><span>Instagram</span>@latelierinspire.fr</a>
    </div>
    <form class="form reveal" id="contactForm" novalidate>
      <p class="form__hint">* Indique les champs obligatoires</p>
      <div class="field">
        <label for="f-name">Nom *</label>
        <input id="f-name" name="name" type="text" autocomplete="name" required>
        <p class="field__err" id="e-name">Ce champ est obligatoire.</p>
      </div>
      <div class="field">
        <label for="f-email">E-mail *</label>
        <input id="f-email" name="email" type="email" autocomplete="email" required>
        <p class="field__err" id="e-email">L'adresse électronique n'est pas valide (ex. : prenom@exemple.fr).</p>
      </div>
      <div class="field">
        <label for="f-msg">Message</label>
        <textarea id="f-msg" name="message" rows="5"></textarea>
      </div>
      <div class="field field--check">
        <input id="f-ok" name="consent" type="checkbox" required>
        <label for="f-ok">J'accepte que ces données soient stockées et traitées dans le but d'établir un contact. Je suis conscient que je peux révoquer mon consentement à tout moment. *</label>
        <p class="field__err" id="e-ok">Ce champ est obligatoire.</p>
      </div>
      <button class="btn" type="submit">Envoyer</button>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>
  </section>

  <section class="cgv container" id="cgv">
    <h2 class="h2 split">Conditions générales de vente</h2>
    <ol class="cgv__list">
      <li class="reveal"><h3>Présentation de la boutique</h3><p>Boutique en ligne d'articles funéraires créée par une artiste et créative, située au 92 rue Edouard Vaillant, 69100 Villeurbanne.</p></li>
      <li class="reveal"><h3>Retours et échanges</h3><p>Les retours et échanges ne sont pas acceptés.</p></li>
      <li class="reveal"><h3>Frais d'envoi</h3><p>Les frais d'envoi sont calculés en fonction du produit.</p></li>
      <li class="reveal"><h3>Pays d'expédition</h3><p>Les expéditions se font uniquement en France.</p></li>
      <li class="reveal"><h3>Temps de traitement</h3><p>Le temps de traitement des commandes varie. Pour plus de détails, veuillez consulter les descriptions des articles.</p></li>
      <li class="reveal"><h3>Frais de douane et d'import</h3><p>Les éventuels frais de douane et d'import sont à la charge de l'acheteur. Les vendeurs ne sont pas responsables des retards causés par la douane.</p></li>
      <li class="reveal"><h3>Annulations</h3><p>Les annulations sont acceptées dans l'heure suivant l'achat.</p></li>
      <li class="reveal"><h3>Protection des données</h3><p>Vos données personnelles sont protégées conformément à la législation en vigueur.</p></li>
    </ol>
  </section>
</main>""")
