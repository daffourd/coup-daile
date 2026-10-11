#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coup de Patte : moteur de la rubrique Actualites.

Commandes :
  python actualites.py generate   ecrit l'article du jour (API Anthropic si la cle existe,
                                  sinon article de reserve), sauf s'il existe deja
  python actualites.py build      regenere toutes les pages statiques, le flux RSS,
                                  le sitemap, robots.txt, llms.txt et les visuels
  python actualites.py social     publie l'article du jour sur Facebook et Instagram
                                  (si les secrets Meta sont presents)
  python actualites.py check FICHIER.json   valide un article sans rien publier

Source unique de verite : un fichier JSON par article dans actualites/_data/.
Tout le reste est regenere a chaque passage. Bibliotheque standard + Pillow.
"""
import datetime
import glob
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

try:
    from zoneinfo import ZoneInfo
    PARIS = ZoneInfo("Europe/Paris")
except Exception:  # pragma: no cover
    PARIS = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "actualites", "_data")
RESERVE = os.path.join(HERE, "reserve")
OUT = os.path.join(ROOT, "actualites")
IMG = os.path.join(OUT, "img")
FONTS = os.path.join(HERE, "fonts")
SOCIAL_STATE = os.path.join(DATA, "_social.json")

SITE = "https://coupdepatte.eu"
SUPA = "https://sgxohmndhngpxgkobkbm.supabase.co/rest/v1"
SUPA_KEY = "sb_publishable_OBbJMFqX9UIOkj6FF2T34Q_KTrqUbvL"  # cle publiable, publique par nature

# Rubrique du jour (0 = lundi)
RUBRIQUES = [
    ("france", "Actu France", "une actualite francaise recente (14 derniers jours) sur la faune sauvage en ville : oiseaux, herissons, chauves-souris, renards, ecureuils, etc."),
    ("monde", "Europe et monde", "une actualite europeenne ou internationale recente (14 derniers jours) sur la faune sauvage urbaine, avec ce qu'elle enseigne pour la France"),
    ("geste", "Le bon geste", "un geste concret de sauvetage ou de protection, rattache a l'actualite ou a la saison en cours"),
    ("espece", "Portrait d'espece", "le portrait d'une espece sauvage vivant en ville, en lien avec ce qui lui arrive en ce moment (saison, actualite)"),
    ("initiative", "Initiative", "une initiative recente et inspirante (ville, association, centre de soins, chercheurs) en faveur de la faune sauvage urbaine"),
    ("saison", "Au fil des saisons", "ce qui se passe pour la faune urbaine a cette periode de l'annee (nidification, canicule, migration, collisions, grand froid, hibernation) et comment aider"),
    ("science", "Science et decouvertes", "une etude ou une decouverte scientifique recente sur la faune sauvage en ville, expliquee simplement"),
]
RUBRIQUE_LABEL = {
    "france": "Actu France", "monde": "Europe et monde", "geste": "Le bon geste",
    "espece": "Portrait d'espèce", "initiative": "Initiative", "saison": "Au fil des saisons",
    "science": "Science et découvertes",
}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

VERT = "#1F9E67"
BEIGE = "#F7F5EF"
AMBRE = "#E39A2E"
TEXTE = "#233029"


# ---------------------------------------------------------------- utilitaires

def today_paris():
    now = datetime.datetime.now(PARIS) if PARIS else datetime.datetime.utcnow()
    return now.date()


def log(*a):
    print("[actualites]", *a, flush=True)


def esc(s):
    return html.escape(str(s or ""), quote=True)


def slugify(s, maxlen=70):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rsplit("-", 1)[0]
    return s or "article"


def date_fr(d):
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d)
    return "%d %s %d" % (d.day, MOIS[d.month - 1], d.year)


def clean_text(s):
    """Retire toute balise, normalise les espaces, interdit les tirets longs."""
    s = str(s or "")
    s = re.sub(r"<[^>]*>", "", s)
    s = s.replace(" ", " ")
    s = re.sub(r"\s*[—–]\s*", ", ", s)  # tiret cadratin ou demi-cadratin
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def clean_article(a):
    def walk(v):
        if isinstance(v, str):
            return clean_text(v)
        if isinstance(v, list):
            return [walk(x) for x in v]
        if isinstance(v, dict):
            return {k: (v[k] if k in ("url", "slug", "date") else walk(v[k])) for k in v}
        return v
    return walk(a)


def http(method, url, data=None, headers=None, timeout=60):
    body = None
    h = {"User-Agent": "CoupDePatte-Actualites/1.0 (+https://coupdepatte.eu)"}
    if headers:
        h.update(headers)
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # reseau
        return 0, str(e).encode("utf-8")


def load_articles():
    arts = []
    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        if os.path.basename(f).startswith("_"):
            continue
        with open(f, encoding="utf-8") as fh:
            a = json.load(fh)
        if a.get("masque"):
            continue
        a["_file"] = f
        arts.append(a)
    arts.sort(key=lambda a: (a["date"], a.get("heure", "")), reverse=True)
    return arts


def stats():
    out = {}
    for fn in ("stats_centres", "stats_publics"):
        code, body = http("POST", SUPA + "/rpc/" + fn, {}, {"apikey": SUPA_KEY, "Authorization": "Bearer " + SUPA_KEY}, timeout=20)
        if code == 200:
            try:
                out.update(json.loads(body))
            except Exception:
                pass
    return out


# ---------------------------------------------------------------- validation

def word_count(a):
    txt = " ".join([a.get("chapo", "")] + [p for s in a.get("sections", []) for p in s.get("paragraphes", [])]
                   + a.get("gestes", []) + [f.get("r", "") for f in a.get("faq", [])])
    return len(txt.split())


def validate(a, check_urls=False):
    """Renvoie la liste des problemes (vide = article valide)."""
    p = []
    req = ["slug", "date", "rubrique", "titre", "chapo", "meta_description", "sections", "gestes", "faq", "sources"]
    for k in req:
        if not a.get(k):
            p.append("champ manquant : " + k)
    if p:
        return p
    if a["rubrique"] not in RUBRIQUE_LABEL:
        p.append("rubrique inconnue")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", a["date"]):
        p.append("date invalide")
    if not re.match(r"^[a-z0-9-]{8,80}$", a["slug"]):
        p.append("slug invalide")
    if not 20 <= len(a["titre"]) <= 110:
        p.append("titre de %d caracteres (20 a 110)" % len(a["titre"]))
    if not 80 <= len(a["chapo"]) <= 420:
        p.append("chapo de %d caracteres (80 a 420)" % len(a["chapo"]))
    if not 70 <= len(a["meta_description"]) <= 170:
        p.append("meta_description de %d caracteres (70 a 170)" % len(a["meta_description"]))
    if not 2 <= len(a["sections"]) <= 5:
        p.append("2 a 5 sections attendues")
    for s in a["sections"]:
        if not s.get("titre") or not s.get("paragraphes"):
            p.append("section incomplete")
    if not 3 <= len(a["gestes"]) <= 6:
        p.append("3 a 6 gestes attendus")
    if not 2 <= len(a["faq"]) <= 4:
        p.append("2 a 4 questions de FAQ attendues")
    if not 1 <= len(a["sources"]) <= 6:
        p.append("1 a 6 sources attendues")
    for s in a["sources"]:
        u = s.get("url", "")
        if not u.startswith("https://"):
            p.append("source sans URL https : " + s.get("titre", "?"))
    n = word_count(a)
    if not 450 <= n <= 1500:
        p.append("%d mots (450 a 1500 attendus)" % n)
    blob = json.dumps(a, ensure_ascii=False).lower()
    for bad in ["qu'on ", "qu’on ", "—", "–", "lorem", "[source", "xxx"]:
        if bad in blob:
            p.append("formulation interdite : " + bad.strip())
    if check_urls:
        ok = 0
        for s in a["sources"]:
            code, _ = http("GET", s["url"], timeout=25)
            if code and code < 400 or code in (401, 403, 429):
                ok += 1
            else:
                p.append("source injoignable (%s) : %s" % (code, s["url"]))
        if ok == 0:
            p.append("aucune source joignable")
    return p


# ---------------------------------------------------------------- generation par l'API

SCHEMA = """{
  "titre": "titre factuel de 40 a 95 caracteres, avec le mot-cle principal, sans point final",
  "chapo": "2 phrases (150 a 320 caracteres) qui repondent directement a la question que se pose le lecteur",
  "meta_description": "resume de 110 a 160 caracteres pour Google",
  "mots_cles": ["4 a 8 expressions que les gens tapent vraiment dans Google"],
  "especes": ["especes concernees, noms francais"],
  "zone": "France | Europe | Monde",
  "sections": [
    {"titre": "L'essentiel de l'actu (ou un intertitre explicite)", "paragraphes": ["2 ou 3 paragraphes de 50 a 120 mots"]},
    {"titre": "Pourquoi c'est important", "paragraphes": ["..."]},
    {"titre": "un troisieme intertitre facultatif", "paragraphes": ["..."]}
  ],
  "gestes": ["3 a 5 gestes concrets, une phrase chacun, verbe d'action en tete"],
  "faq": [{"q": "question telle qu'on la taperait dans Google", "r": "reponse directe en 1 a 3 phrases"}],
  "sources": [{"titre": "titre exact de la page", "editeur": "nom du media ou de l'organisme", "url": "https://...", "date": "AAAA-MM-JJ ou vide"}],
  "social": "texte de 180 a 380 caracteres pour Facebook et Instagram, chaleureux, qui donne envie de lire, sans lien",
  "hashtags": ["5 a 8 hashtags sans le #, en francais"]
}"""

SYSTEM = """Tu es le redacteur de la rubrique Actualites de Coup de Patte (coupdepatte.eu), application gratuite d'une association francaise loi 1901 qui aide le grand public a secourir les animaux sauvages trouves en detresse en ville : oiseaux d'abord, mais aussi herissons, chauves-souris, ecureuils, renards et autre faune urbaine.

LIGNE EDITORIALE
- Promesse : la faune sauvage des villes, ses dangers, et les gestes qui la sauvent.
- Chaque article part d'un fait reel et verifiable, l'explique simplement, puis debouche sur des gestes concrets.
- Public : grand public francais, souvent sur mobile. Ton : tutoiement, direct, chaleureux, pedagogique, porteur d'espoir. Jamais gore, jamais culpabilisant, jamais militant ni politique.
- Environ 60 % des sujets concernent les oiseaux, le reste les autres animaux sauvages urbains.
- Ecriture optimisee pour Google et pour les moteurs d'IA : reponse directe des le chapo, intertitres explicites, phrases courtes, faits dates et sources, FAQ.

REGLES ABSOLUES
1. N'invente rien : chaque fait, chiffre, date, lieu ou nom vient d'une source que tu as reellement consultee avec l'outil de recherche, et cette source figure dans "sources" avec son URL exacte. Pas de chiffre sans source.
2. Ne cite jamais plus de 15 mots d'affilee d'une source. Reformule.
3. Aucun conseil veterinaire ou medical. Les gestes se limitent aux premiers gestes reconnus par la LPO, l'OFB et les centres de soins (mettre au calme dans un carton aere, ne pas nourrir ni faire boire de force, appeler un centre de soins). Toujours rappeler de contacter un centre de soins de la faune sauvage.
4. Ne conseille jamais de garder un animal sauvage chez soi : c'est interdit sans autorisation.
5. Ne dis rien sur l'association Coup de Patte elle-meme (chiffres, actions, partenaires) : un encart officiel est ajoute automatiquement. Tu peux seulement inviter a ouvrir l'application Coup de Patte pour trouver le centre de soins le plus proche.
6. Pas de tiret long ni demi-cadratin. N'ecris jamais "qu'on", evite le pronom "on". Pas d'emoji. Pas de HTML ni de Markdown dans les textes.
7. Si aucune actualite recente fiable ne convient, choisis un sujet de saison solide et source (LPO, OFB, MNHN, SFEPM, centres de soins, collectivites), sans pretendre que c'est une nouveaute.
8. Ne reprends pas un sujet deja traite (liste fournie).

Ta reponse finale contient UNIQUEMENT l'objet JSON demande, sans texte autour."""

QA_SYSTEM = """Tu es le relecteur exigeant de la rubrique Actualites de Coup de Patte, association de sauvetage de la faune sauvage urbaine. Tu verifies un article avant publication automatique. Tu reponds UNIQUEMENT par un objet JSON {"ok": true|false, "problemes": ["..."]}.
Refuse (ok=false) si : conseil veterinaire ou medical au-dela des premiers gestes ; conseil de nourrir, abreuver de force, garder ou elever un animal sauvage ; lait ou pain proposes ; espece mal identifiee ou fait douteux ; chiffre ou affirmation sans source dans la liste ; citation de plus de 15 mots ; affirmation sur l'association Coup de Patte elle-meme ; ton politique, militant, gore ou culpabilisant ; vouvoiement ; tiret long ; "qu'on" ; contenu hors sujet (pas de faune sauvage). Sinon ok=true avec une liste vide."""


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("pas de JSON dans la reponse")
    return json.loads(text[start:end + 1])


def claude(messages, system, tools=None, max_tokens=8000):
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    models = [m for m in [os.environ.get("ACTUS_MODEL", "").strip(), "claude-sonnet-5-5", "claude-sonnet-4-5"] if m]
    last = None
    for model in models:
        msgs = list(messages)
        for _ in range(4):  # gere les pauses de l'outil de recherche
            body = {"model": model, "max_tokens": max_tokens, "system": system, "messages": msgs}
            if tools:
                body["tools"] = tools
            code, raw = http("POST", "https://api.anthropic.com/v1/messages", body,
                             {"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout=300)
            if code == 404 or (code == 400 and b"model" in raw.lower()):
                last = "modele %s indisponible" % model
                break
            if code == 529 or code == 429 or code >= 500:
                time.sleep(20)
                last = "API %s" % code
                continue
            if code != 200:
                raise RuntimeError("API Anthropic %s : %s" % (code, raw[:400]))
            r = json.loads(raw)
            if r.get("stop_reason") == "pause_turn":
                msgs = msgs + [{"role": "assistant", "content": r["content"]}]
                continue
            text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
            return text
        log(last)
    raise RuntimeError(last or "API indisponible")


def generate_with_api(day, rub, recent_titles):
    key, label, consigne = rub
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8,
              "user_location": {"type": "approximate", "country": "FR", "timezone": "Europe/Paris"}}]
    user = (
        "Nous sommes le %s. Rubrique du jour : %s.\n"
        "Sujet attendu : %s.\n\n"
        "1. Fais une veille avec l'outil de recherche (sources francophones de preference : presse nationale et regionale, LPO, OFB, MNHN, collectivites, centres de soins ; pour l'Europe et le monde, presse internationale). Privilegie des faits publies dans les 14 derniers jours.\n"
        "2. Choisis UN sujet utile au grand public, verifie-le dans au moins deux sources si possible.\n"
        "3. Redige l'article (600 a 1000 mots au total) en respectant strictement ce format JSON :\n%s\n\n"
        "Sujets deja traites, a ne pas reprendre :\n- %s"
    ) % (date_fr(day), label, consigne, SCHEMA, "\n- ".join(recent_titles[:40]) or "(aucun)")
    text = claude([{"role": "user", "content": user}], SYSTEM, tools=tools)
    return extract_json(text)


def qa_review(a):
    payload = {k: a[k] for k in ("titre", "chapo", "sections", "gestes", "faq", "sources", "social") if k in a}
    text = claude([{"role": "user", "content": "Article a relire :\n" + json.dumps(payload, ensure_ascii=False, indent=1)}],
                  QA_SYSTEM, max_tokens=1500)
    return extract_json(text)


def fix_with_api(a, problemes):
    user = ("Corrige cet article pour resoudre ces problemes, sans ajouter de fait non source, et renvoie le JSON complet au meme format.\n"
            "Problemes :\n- %s\n\nArticle :\n%s") % ("\n- ".join(problemes), json.dumps(a, ensure_ascii=False))
    return extract_json(claude([{"role": "user", "content": user}], SYSTEM))


def finalize(a, day, rub_key, origine):
    a = clean_article(a)
    a["date"] = day.isoformat()
    a["rubrique"] = a.get("rubrique") if a.get("rubrique") in RUBRIQUE_LABEL else rub_key
    a["origine"] = origine
    existing = {x["slug"] for x in load_articles()}
    base = slugify(a.get("slug") or a.get("titre", "article"))
    slug, i = base, 2
    while slug in existing:
        slug, i = "%s-%d" % (base, i), i + 1
    a["slug"] = slug
    a.pop("_file", None)
    return a


def save_article(a):
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, "%s-%s.json" % (a["date"], a["slug"]))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(a, fh, ensure_ascii=False, indent=2)
    log("article enregistre :", os.path.relpath(path, ROOT))
    return path


def use_reserve(day, rub_key):
    files = sorted(glob.glob(os.path.join(RESERVE, "*.json")))
    if not files:
        log("plus aucun article de reserve")
        return None
    f = files[0]
    with open(f, encoding="utf-8") as fh:
        a = json.load(fh)
    a = finalize(a, day, a.get("rubrique", rub_key), "reserve")
    pb = validate(a)
    if pb:
        log("article de reserve invalide", f, pb)
        return None
    save_article(a)
    os.remove(f)
    return a


def cmd_generate():
    day = today_paris()
    arts = load_articles()
    if any(a["date"] == day.isoformat() for a in arts):
        log("un article existe deja pour aujourd'hui, rien a faire")
        return
    rub = RUBRIQUES[day.weekday()]
    recent = [a["titre"] for a in arts]
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        for essai in (1, 2):
            try:
                a = generate_with_api(day, rub, recent)
                a = finalize(a, day, rub[0], "ia")
                pb = validate(a, check_urls=True)
                if not pb:
                    qa = qa_review(a)
                    pb = [] if qa.get("ok") else (qa.get("problemes") or ["refus du relecteur"])
                if pb:
                    log("essai %d, problemes :" % essai, pb)
                    a = finalize(fix_with_api(a, pb), day, rub[0], "ia")
                    pb = validate(a, check_urls=True)
                    if not pb:
                        qa = qa_review(a)
                        pb = [] if qa.get("ok") else (qa.get("problemes") or ["refus du relecteur"])
                if not pb:
                    save_article(a)
                    return
                log("essai %d rejete :" % essai, pb)
            except Exception as e:
                log("essai %d en erreur :" % essai, e)
    else:
        log("pas de cle API : article de reserve")
    use_reserve(day, rub[0])


# ---------------------------------------------------------------- visuels

def _font(name, size, weight=None):
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if weight:
        try:
            axes = f.get_variation_axes()
            vals = []
            for ax in axes:
                n = ax.get("name", b"")
                n = n.decode() if isinstance(n, bytes) else str(n)
                if n.lower().startswith("weight") or n.lower() == "wght":
                    vals.append(weight)
                elif n.lower().startswith("optical") or n.lower() == "opsz":
                    vals.append(min(max(size / 2, ax["minimum"]), ax["maximum"]))
                else:
                    vals.append(ax.get("default", ax["minimum"]))
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


def _wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_card(a, path, w, h):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), BEIGE)
    d = ImageDraw.Draw(img)
    pad = int(w * 0.075)
    band_h = int(h * 0.80)
    d.rectangle([0, 0, w, band_h], fill=VERT)
    # motif discret : cercles clairs
    d.ellipse([w - int(w * .38), -int(h * .18), w + int(w * .18), int(h * .30)], fill="#2AAA74")
    # etiquette de rubrique
    lab = RUBRIQUE_LABEL.get(a["rubrique"], "Actualité").upper()
    fl = _font("Nunito.ttf", int(h * 0.032), 800)
    tw = d.textlength(lab, font=fl)
    y = pad
    d.rounded_rectangle([pad, y, pad + tw + 40, y + int(h * .062)], radius=int(h * .031), fill=AMBRE)
    d.text((pad + 20, y + int(h * .031)), lab, font=fl, fill="#FFFFFF", anchor="lm")
    # titre
    maxw = w - 2 * pad
    size = int(h * (0.085 if w == h else 0.095))
    while size > 24:
        ft = _font("Fraunces.ttf", size, 700)
        lines = _wrap(d, a["titre"], ft, maxw)
        lh = int(size * 1.16)
        if len(lines) <= (6 if w == h else 4) and len(lines) * lh <= band_h - y - int(h * .13) - pad:
            break
        size -= 4
    ty = band_h - pad - len(lines) * lh
    for i, ln in enumerate(lines):
        d.text((pad, ty + i * lh), ln, font=ft, fill="#FFFFFF")
    # pied : logo + adresse
    foot_y = band_h + (h - band_h) // 2
    try:
        logo = Image.open(os.path.join(ROOT, "icon-192.png")).convert("RGBA")
        ls = int((h - band_h) * 0.62)
        logo = logo.resize((ls, ls))
        img.paste(logo, (pad, foot_y - ls // 2), logo)
        lx = pad + ls + 22
    except Exception:
        lx = pad
    fb = _font("Fraunces.ttf", int(h * 0.042), 700)
    d.text((lx, foot_y), "Coup de Patte", font=fb, fill=TEXTE, anchor="lm")
    fs = _font("Nunito.ttf", int(h * 0.032), 700)
    d.text((w - pad, foot_y), "coupdepatte.eu", font=fs, fill="#5C6B63", anchor="rm")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)


# ---------------------------------------------------------------- pages

CSS = """
:root{--vert:#1F9E67;--vert-pale:#E7F1EB;--beige:#F7F5EF;--ambre:#E39A2E;--ambre-pale:#FBEFD8;--corail:#D7614F;--texte:#233029;--doux:#5C6B63;--blanc:#fff;--bord:#E6E3DA;}
@media (prefers-color-scheme:dark){:root{--beige:#0f1512;--blanc:#1e2823;--texte:#eaf1ec;--doux:#a7b6ac;--bord:#2c3a32;--vert-pale:#20302a;--ambre-pale:#2f2a1c;}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Nunito,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;background:var(--beige);color:var(--texte);line-height:1.65;font-size:17px}
a{color:var(--vert)}
.top{display:flex;align-items:center;gap:10px;padding:12px 16px;max-width:760px;margin:0 auto}
.top .logo{width:36px;height:36px;border-radius:11px;background:var(--vert);display:grid;place-items:center;flex:0 0 auto}
.top .logo svg{width:20px;height:20px}
.top .marque{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:19px;color:var(--texte);text-decoration:none}
.top .cta{margin-left:auto;background:var(--corail);color:#fff;text-decoration:none;font-weight:800;font-size:14px;padding:9px 14px;border-radius:999px;white-space:nowrap}
main{max-width:760px;margin:0 auto;padding:8px 16px 40px}
.fil{font-size:13px;color:var(--doux);margin:6px 0 14px}
.fil a{color:var(--doux)}
.etiq{display:inline-block;background:var(--ambre-pale);color:#9a5c0c;font-weight:800;font-size:12px;letter-spacing:.04em;text-transform:uppercase;padding:4px 10px;border-radius:999px}
h1{font-family:Fraunces,Georgia,serif;font-size:clamp(28px,6vw,40px);line-height:1.15;letter-spacing:-.5px;margin:12px 0 10px}
.meta{font-size:14px;color:var(--doux);margin-bottom:18px}
.chapo{font-size:19px;font-weight:700;line-height:1.55;margin-bottom:22px}
.visuel{width:100%;height:auto;border-radius:20px;display:block;margin:0 0 26px}
h2{font-family:Fraunces,Georgia,serif;font-size:24px;line-height:1.25;margin:30px 0 10px}
p{margin:0 0 14px}
.geste{background:var(--vert-pale);border-radius:20px;padding:20px 22px;margin:28px 0}
.geste h2{margin-top:0}
.geste ol{padding-left:22px}.geste li{margin:6px 0;font-weight:600}
.encart{background:var(--blanc);border:1px solid var(--bord);border-left:6px solid var(--vert);border-radius:18px;padding:18px 20px;margin:28px 0}
.encart h2{font-size:20px;margin-top:0}
.btn{display:inline-block;background:var(--vert);color:#fff;text-decoration:none;font-weight:800;padding:12px 18px;border-radius:999px;margin-top:6px}
details{background:var(--blanc);border:1px solid var(--bord);border-radius:14px;padding:12px 16px;margin:8px 0}
summary{font-weight:800;cursor:pointer}
details p{margin:8px 0 0}
.sources{font-size:14px;color:var(--doux)}
.sources li{margin:4px 0 4px 18px}
.liste{list-style:none}
.carte{display:flex;gap:14px;background:var(--blanc);border:1px solid var(--bord);border-radius:18px;padding:12px;margin:12px 0;text-decoration:none;color:inherit}
.carte img{width:96px;height:96px;border-radius:14px;flex:0 0 auto;object-fit:cover}
.carte b{display:block;font-family:Fraunces,Georgia,serif;font-size:18px;line-height:1.25;margin:4px 0}
.carte span{font-size:13px;color:var(--doux)}
.avert{font-size:13px;color:var(--doux);margin-top:26px}
footer{max-width:760px;margin:0 auto;padding:20px 16px 50px;font-size:13px;color:var(--doux)}
footer a{color:var(--doux)}
"""

LOGO_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/><line x1="16" y1="8" x2="2" y2="22"/><line x1="17.5" y1="15" x2="9" y2="15"/></svg>'

ORG = {
    "@type": "NGO", "@id": SITE + "/#association", "name": "Coup de Patte",
    "url": SITE + "/", "logo": SITE + "/icon-512.png",
    "description": "Association loi 1901 et application gratuite pour secourir les animaux sauvages trouvés en détresse en ville.",
    "address": {"@type": "PostalAddress", "streetAddress": "1 impasse du Parc", "postalCode": "34130",
                "addressLocality": "Saint-Aunès", "addressCountry": "FR"},
}


def head(title, desc, url, image, extra=""):
    return """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{u}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#1F9E67">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Coup de Patte">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{i}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Actualités Coup de Patte" href="{s}/actualites/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>{c}</style>
{x}
</head>
<body>
<header class="top"><a href="/" class="logo" aria-label="Coup de Patte, accueil">{l}</a><a href="/" class="marque">Coup de Patte</a><a class="cta" href="/">J'ai trouvé un animal</a></header>
""".format(t=esc(title), d=esc(desc), u=esc(url), i=esc(image), s=SITE, c=CSS, x=extra, l=LOGO_SVG)


FOOT = """<footer>Coup de Patte, association loi 1901, 1 impasse du Parc, 34130 Saint-Aunès. Application gratuite pour secourir la faune sauvage en ville. <a href="/">Ouvrir l'application</a> · <a href="/actualites/">Toutes les actualités</a> · <a href="/actualites/rss.xml">Flux RSS</a></footer>
</body></html>
"""


def encart_html(st):
    c = st.get("centres_ouverts")
    dpt = st.get("departements_couverts")
    lignes = []
    if c and dpt:
        lignes.append("<p>L'application gratuite Coup de Patte référence <b>%d centres de soins</b> de la faune sauvage dans <b>%d départements</b>, avec un guide en 3 questions pour savoir quoi faire en moins d'une minute.</p>" % (c, dpt))
    else:
        lignes.append("<p>L'application gratuite Coup de Patte te guide en 3 questions pour savoir quoi faire en moins d'une minute, et t'indique le centre de soins de la faune sauvage le plus proche.</p>")
    lignes.append("<p>Elle t'aide aussi à identifier l'espèce, à signaler un oiseau bagué au Muséum et à trouver des bénévoles près de chez toi.</p>")
    return ('<aside class="encart"><h2>Coup de Patte en action</h2>%s<a class="btn" href="/">Ouvrir l\'application</a></aside>' % "".join(lignes))


def article_url(a):
    return "%s/actualites/%s/" % (SITE, a["slug"])


def render_article(a, others, st):
    url = article_url(a)
    img = "%s/actualites/img/%s.png" % (SITE, a["slug"])
    og = "%s/actualites/img/%s-og.png" % (SITE, a["slug"])
    rub = RUBRIQUE_LABEL.get(a["rubrique"], "Actualité")
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            ORG,
            {"@type": "NewsArticle", "headline": a["titre"], "description": a["meta_description"],
             "datePublished": a["date"] + "T07:00:00+02:00", "dateModified": a.get("modifie", a["date"]) + "T07:00:00+02:00",
             "inLanguage": "fr-FR", "mainEntityOfPage": url, "image": [og, img],
             "articleSection": rub, "keywords": ", ".join(a.get("mots_cles", [])),
             "about": [{"@type": "Thing", "name": e} for e in a.get("especes", [])],
             "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
             "citation": [s["url"] for s in a["sources"]], "isAccessibleForFree": True},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"],
                                                 "acceptedAnswer": {"@type": "Answer", "text": f["r"]}} for f in a["faq"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Coup de Patte", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Actualités", "item": SITE + "/actualites/"},
                {"@type": "ListItem", "position": 3, "name": a["titre"], "item": url}]},
        ],
    }
    extra = ('<meta property="article:published_time" content="%sT07:00:00+02:00">\n<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">\n'
             '<script type="application/ld+json">%s</script>') % (a["date"], json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))
    out = [head(a["titre"] + " | Coup de Patte", a["meta_description"], url, og, extra)]
    out.append('<main><article>')
    out.append('<nav class="fil"><a href="/">Coup de Patte</a> › <a href="/actualites/">Actualités</a></nav>')
    out.append('<span class="etiq">%s</span>' % esc(rub))
    out.append('<h1>%s</h1>' % esc(a["titre"]))
    out.append('<p class="meta">Publié le <time datetime="%s">%s</time> · Rédaction Coup de Patte</p>' % (a["date"], date_fr(a["date"])))
    out.append('<p class="chapo">%s</p>' % esc(a["chapo"]))
    out.append('<img class="visuel" src="/actualites/img/%s-og.png" width="1200" height="630" alt="%s">' % (esc(a["slug"]), esc(a["titre"])))
    for s in a["sections"]:
        out.append('<h2>%s</h2>' % esc(s["titre"]))
        for p in s["paragraphes"]:
            out.append('<p>%s</p>' % esc(p))
    out.append('<section class="geste"><h2>Le bon geste</h2><ol>%s</ol><p style="margin-top:10px">En cas de doute, appelle un centre de soins de la faune sauvage avant toute manipulation.</p></section>'
               % "".join("<li>%s</li>" % esc(g) for g in a["gestes"]))
    out.append(encart_html(st))
    out.append('<h2>Questions fréquentes</h2>')
    for f in a["faq"]:
        out.append('<details><summary>%s</summary><p>%s</p></details>' % (esc(f["q"]), esc(f["r"])))
    out.append('<h2>Sources</h2><ul class="sources">')
    for s in a["sources"]:
        dt = (", " + date_fr(s["date"])) if re.match(r"^\d{4}-\d{2}-\d{2}$", s.get("date") or "") else ""
        out.append('<li><a href="%s" rel="noopener" target="_blank">%s</a>, %s%s</li>' % (esc(s["url"]), esc(s.get("titre", s["url"])), esc(s.get("editeur", "")), esc(dt)))
    out.append('</ul>')
    out.append('<p class="avert">Coup de Patte informe et oriente, sans remplacer l\'avis d\'un centre de soins de la faune sauvage ou d\'un vétérinaire.</p>')
    out.append('</article>')
    if others:
        out.append('<h2>À lire aussi</h2><ul class="liste">')
        for o in others[:3]:
            out.append(card_html(o))
        out.append('</ul>')
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


def card_html(o):
    return ('<li><a class="carte" href="/actualites/%s/"><img src="/actualites/img/%s.png" alt="" loading="lazy" width="96" height="96">'
            '<div><span>%s · %s</span><b>%s</b><span>%s</span></div></a></li>') % (
        esc(o["slug"]), esc(o["slug"]), esc(RUBRIQUE_LABEL.get(o["rubrique"], "")), date_fr(o["date"]),
        esc(o["titre"]), esc(o["chapo"][:150] + ("…" if len(o["chapo"]) > 150 else "")))


def render_index(arts):
    url = SITE + "/actualites/"
    desc = "Chaque jour, une actualité de la faune sauvage en ville en France, en Europe et dans le monde, et les gestes qui la sauvent. Par l'association Coup de Patte."
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "CollectionPage", "name": "Actualités de la faune sauvage en ville", "url": url, "description": desc,
        "publisher": {"@id": ORG["@id"]},
        "hasPart": [{"@type": "NewsArticle", "headline": a["titre"], "url": article_url(a), "datePublished": a["date"]} for a in arts[:30]]}]}
    img = (SITE + "/actualites/img/%s-og.png" % arts[0]["slug"]) if arts else SITE + "/icon-512.png"
    out = [head("Actualités de la faune sauvage en ville | Coup de Patte", desc, url, img,
                '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))]
    out.append('<main><nav class="fil"><a href="/">Coup de Patte</a> › Actualités</nav>')
    out.append('<h1>Actualités de la faune sauvage en ville</h1>')
    out.append('<p class="chapo">Chaque jour, une actualité de France, d\'Europe ou du monde sur les animaux sauvages qui vivent près de nous, et les gestes simples qui les sauvent.</p>')
    out.append('<ul class="liste">%s</ul>' % "".join(card_html(a) for a in arts))
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


def rfc822(d):
    dt = datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(7, 0))
    return dt.strftime("%a, %d %b %Y 07:00:00 +0200")


def render_rss(arts):
    items = []
    for a in arts[:30]:
        items.append("<item><title>%s</title><link>%s</link><guid isPermaLink=\"true\">%s</guid><pubDate>%s</pubDate><category>%s</category><description>%s</description><enclosure url=\"%s/actualites/img/%s-og.png\" type=\"image/png\" length=\"0\"/></item>" % (
            esc(a["titre"]), article_url(a), article_url(a), rfc822(a["date"]), esc(RUBRIQUE_LABEL.get(a["rubrique"], "")), esc(a["chapo"]), SITE, a["slug"]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            '<title>Actualités Coup de Patte</title><link>%s/actualites/</link><language>fr-FR</language>'
            '<description>La faune sauvage des villes, ses dangers, et les gestes qui la sauvent.</description>'
            '<atom:link href="%s/actualites/rss.xml" rel="self" type="application/rss+xml"/>%s</channel></rss>\n') % (SITE, SITE, "".join(items))


def render_sitemap(arts):
    urls = [(SITE + "/", today_paris().isoformat(), "daily", "1.0"), (SITE + "/actualites/", arts[0]["date"] if arts else today_paris().isoformat(), "daily", "0.9")]
    for a in arts:
        urls.append((article_url(a), a.get("modifie", a["date"]), "monthly", "0.7"))
    body = "".join("<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>" % u for u in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % body


ROBOTS = """# Coup de Patte : contenus ouverts aux moteurs de recherche et aux assistants IA
User-agent: *
Allow: /
Disallow: /.github/

Sitemap: https://coupdepatte.eu/sitemap.xml
"""


def render_llms(arts, st):
    c = st.get("centres_ouverts")
    dpt = st.get("departements_couverts")
    lines = [
        "# Coup de Patte",
        "",
        "> Association loi 1901 (Saint-Aunès, Hérault) et application web gratuite qui aide le grand public à secourir les animaux sauvages trouvés en détresse en ville, en particulier les oiseaux : oisillon tombé du nid, oiseau blessé, oiseau bagué, martinet au sol.",
        "",
        "- Application : https://coupdepatte.eu/ (guide d'urgence en 3 questions, fiches de 100 espèces, carte des centres de soins, signalement des oiseaux bagués au Muséum, annuaire de bénévoles)",
    ]
    if c and dpt:
        lines.append("- Centres de soins de la faune sauvage référencés : %d, dans %d départements" % (c, dpt))
    lines += [
        "- Conseils fondés sur la LPO, l'OFB, le CRBPO (Muséum national d'Histoire naturelle) et les centres de soins.",
        "- Règle d'or : un oisillon emplumé au sol n'est presque jamais abandonné ; un animal sauvage blessé se confie à un centre de soins, il ne se garde pas chez soi.",
        "",
        "## Actualités",
        "",
        "- Index : https://coupdepatte.eu/actualites/",
        "- Flux RSS : https://coupdepatte.eu/actualites/rss.xml",
        "",
    ]
    for a in arts[:60]:
        lines.append("- [%s](%s) (%s) : %s" % (a["titre"], article_url(a), a["date"], a["meta_description"]))
    return "\n".join(lines) + "\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def cmd_build():
    arts = load_articles()
    st = stats()
    live = set()
    for i, a in enumerate(arts):
        pb = validate(a)
        if pb:
            log("article ignore (invalide) :", a.get("slug"), pb)
            continue
        live.add(a["slug"])
        others = [o for o in arts if o["slug"] != a["slug"]]
        # proximite : meme rubrique d'abord, puis les plus recents
        others.sort(key=lambda o: (o["rubrique"] != a["rubrique"], o["date"]), reverse=False)
        others = sorted(others[:6], key=lambda o: o["date"], reverse=True)
        write(os.path.join(OUT, a["slug"], "index.html"), render_article(a, others, st))
        sq = os.path.join(IMG, a["slug"] + ".png")
        og = os.path.join(IMG, a["slug"] + "-og.png")
        if not os.path.exists(sq):
            make_card(a, sq, 1080, 1080)
        if not os.path.exists(og):
            make_card(a, og, 1200, 630)
    arts = [a for a in arts if a["slug"] in live]
    # pages d'articles masques ou supprimes : retirees du site
    for d in glob.glob(os.path.join(OUT, "*", "index.html")):
        slug = os.path.basename(os.path.dirname(d))
        if slug not in live:
            os.remove(d)
            try:
                os.rmdir(os.path.dirname(d))
            except OSError:
                pass
    write(os.path.join(OUT, "index.html"), render_index(arts))
    feed = [{"slug": a["slug"], "titre": a["titre"], "chapo": a["chapo"], "date": a["date"],
             "rubrique": RUBRIQUE_LABEL.get(a["rubrique"], ""), "url": "/actualites/%s/" % a["slug"],
             "image": "/actualites/img/%s.png" % a["slug"]} for a in arts[:50]]
    write(os.path.join(OUT, "articles.json"), json.dumps({"maj": today_paris().isoformat(), "articles": feed}, ensure_ascii=False, indent=1))
    write(os.path.join(OUT, "rss.xml"), render_rss(arts))
    write(os.path.join(ROOT, "sitemap.xml"), render_sitemap(arts))
    write(os.path.join(ROOT, "robots.txt"), ROBOTS)
    write(os.path.join(ROOT, "llms.txt"), render_llms(arts, st))
    log("%d articles publies" % len(arts))


# ---------------------------------------------------------------- reseaux sociaux

def cmd_social():
    page = os.environ.get("META_PAGE_ID", "").strip()
    token = os.environ.get("META_PAGE_TOKEN", "").strip()
    ig = os.environ.get("META_IG_USER_ID", "").strip()
    ver = os.environ.get("META_GRAPH_VERSION", "v23.0").strip()
    if not (page and token):
        log("secrets Meta absents : publication sur les reseaux ignoree")
        return
    state = {}
    if os.path.exists(SOCIAL_STATE):
        with open(SOCIAL_STATE, encoding="utf-8") as fh:
            state = json.load(fh)
    day = today_paris().isoformat()
    todo = [a for a in load_articles() if a["date"] == day and not state.get(a["slug"], {}).get("ok")]
    if not todo:
        log("rien a publier sur les reseaux")
        return
    for a in todo:
        url = article_url(a)
        img = "%s/actualites/img/%s.png" % (SITE, a["slug"])
        # attendre que Vercel serve la page et l'image
        for _ in range(40):
            c1, _ = http("GET", url, timeout=20)
            c2, _ = http("GET", img, timeout=20)
            if c1 == 200 and c2 == 200:
                break
            time.sleep(15)
        tags = " ".join("#" + re.sub(r"[^\w]", "", h) for h in a.get("hashtags", [])[:8])
        texte = a.get("social") or a["chapo"]
        st = state.setdefault(a["slug"], {})
        api = "https://graph.facebook.com/%s/" % ver
        if not st.get("facebook"):
            code, raw = http("POST", api + page + "/feed", urllib.parse.urlencode(
                {"message": "%s\n\n%s" % (texte, tags), "link": url, "access_token": token}),
                {"Content-Type": "application/x-www-form-urlencoded"})
            log("facebook", code, raw[:200])
            if code == 200:
                st["facebook"] = json.loads(raw).get("id")
        if ig and not st.get("instagram"):
            cap = "%s\n\nArticle complet sur coupdepatte.eu, rubrique Actualités.\n\n%s" % (texte, tags)
            code, raw = http("POST", api + ig + "/media", urllib.parse.urlencode(
                {"image_url": img, "caption": cap, "access_token": token}),
                {"Content-Type": "application/x-www-form-urlencoded"})
            log("instagram media", code, raw[:200])
            if code == 200:
                cid = json.loads(raw).get("id")
                for _ in range(10):
                    time.sleep(6)
                    code, raw = http("POST", api + ig + "/media_publish", urllib.parse.urlencode(
                        {"creation_id": cid, "access_token": token}),
                        {"Content-Type": "application/x-www-form-urlencoded"})
                    if code == 200:
                        st["instagram"] = json.loads(raw).get("id")
                        break
                log("instagram publish", code, raw[:200])
        st["ok"] = bool(st.get("facebook")) and (bool(st.get("instagram")) or not ig)
    with open(SOCIAL_STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- entree

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "generate":
        cmd_generate()
    elif cmd == "build":
        cmd_build()
    elif cmd == "social":
        cmd_social()
    elif cmd == "check":
        with open(sys.argv[2], encoding="utf-8") as fh:
            art = clean_article(json.load(fh))
        pb = validate(art, check_urls="--urls" in sys.argv)
        print(json.dumps({"mots": word_count(art), "problemes": pb}, ensure_ascii=False, indent=1))
        sys.exit(1 if pb else 0)
    else:
        print(__doc__)
        sys.exit(2)
