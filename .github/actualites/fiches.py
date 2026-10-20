# -*- coding: utf-8 -*-
"""
Coup de Patte : pages statiques des fiches espèces et des centres de soins.

Appelé par actualites.py build. Rend indexables par les moteurs et les assistants IA
des contenus qui, dans l'application, n'existent qu'en JavaScript :
  /especes/                 index des 100 espèces
  /especes/<slug>/          une page par espèce (données lues dans index.html)
  /centres/                 index des départements couverts
  /centres/<dept>-<slug>/   une page par département (données lues dans la base, table centres)

L'application reste un fichier unique : ces pages sont des vitrines qui renvoient vers elle.
"""
import json
import os
import re
import subprocess

DEPTS = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence", "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes", "09": "Ariège", "10": "Aube", "11": "Aude",
    "12": "Aveyron", "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal", "16": "Charente",
    "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "2A": "Corse-du-Sud", "2B": "Haute-Corse",
    "21": "Côte-d'Or", "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne", "25": "Doubs", "26": "Drôme",
    "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère", "30": "Gard", "31": "Haute-Garonne", "32": "Gers",
    "33": "Gironde", "34": "Hérault", "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire",
    "38": "Isère", "39": "Jura", "40": "Landes", "41": "Loir-et-Cher", "42": "Loire", "43": "Haute-Loire",
    "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère",
    "49": "Maine-et-Loire", "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne",
    "54": "Meurthe-et-Moselle", "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord",
    "60": "Oise", "61": "Orne", "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin", "68": "Haut-Rhin", "69": "Rhône",
    "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres",
    "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse", "85": "Vendée",
    "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort",
    "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis", "94": "Val-de-Marne", "95": "Val-d'Oise",
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion", "976": "Mayotte",
}

TAILLES = {"tp": "très petit, de la taille d'une mésange", "p": "petit, de la taille d'un moineau",
           "m": "moyen, de la taille d'un merle", "g": "grand, de la taille d'un pigeon",
           "tg": "très grand, plus gros qu'un pigeon"}
MILIEUX = {"jardin": "les jardins", "ville": "la ville", "foret": "les bois et forêts", "campagne": "la campagne",
           "eau": "les plans d'eau et rivières", "toit": "les bâtiments"}
GROUPES = {
    "CONDUITE_PASSEREAU": ("Passereau", "passereaux"),
    "CONDUITE_RAPACE": ("Rapace diurne", "rapaces"),
    "CONDUITE_NOCTURNE": ("Rapace nocturne", "rapaces nocturnes"),
    "CONDUITE_CORVIDE": ("Corvidé", "corvidés"),
    "CONDUITE_EAU": ("Oiseau d'eau", "oiseaux d'eau"),
}

LPO_TEL = "05 46 82 12 34"


def _tel(t):
    d = re.sub(r"\D", "", t or "")
    if len(d) == 10:
        return " ".join(d[i:i + 2] for i in range(0, 10, 2)), "+33" + d[1:]
    return (t or ""), d


# ---------------------------------------------------------------- données

def load_especes(root):
    """Lit le tableau ESPECES (et les constantes CONDUITE_*) dans index.html, via Node."""
    src = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    i = src.index("var CONDUITE_PASSEREAU")
    j = src.index("];", src.index("var ESPECES = [")) + 2
    code = src[i:j]
    js = code + "\nvar out=ESPECES.map(function(e){var o={};for(var k in e)o[k]=e[k];return o;});"
    for name in GROUPES:
        js += "\nout.forEach(function(e){ if(e.conduite===%s) e.groupe='%s'; });" % (name, name)
    js += "\nprocess.stdout.write(JSON.stringify(out));"
    res = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        raise RuntimeError("lecture des especes impossible : " + res.stderr[:300])
    return json.loads(res.stdout)


def load_centres(http, supa, key):
    # select=* : les champs ajoutés par la migration v26 (accueil, horaires, acces, si_absent, don_url,
    # conseils_url, depts_couverts, presentation, valide_par_centre) sont pris s'ils existent.
    code, body = http("GET", supa + "/centres?select=*&ouvert=eq.true&order=dept,ville",
                      None, {"apikey": key, "Authorization": "Bearer " + key}, timeout=30)
    if code != 200:
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


# ---------------------------------------------------------------- espèces

def espece_slug(e, slugify):
    return slugify(e["nom"])


def render_espece(e, autres, ctx):
    esc, SITE, ORG, head, FOOT, slugify = ctx["esc"], ctx["SITE"], ctx["ORG"], ctx["head"], ctx["FOOT"], ctx["slugify"]
    slug = espece_slug(e, slugify)
    url = "%s/especes/%s/" % (SITE, slug)
    nom = e["nom"]
    groupe, groupe_pl = GROUPES.get(e.get("groupe"), ("Oiseau", "oiseaux"))
    milieux = [MILIEUX[m] for m in (e.get("m") or "").split(",") if m in MILIEUX]
    taille = TAILLES.get(e.get("t"), "")
    titre = "%s blessé ou jeune au sol : que faire ? | Coup de Patte" % nom
    desc = "Tu as trouvé un oiseau de l'espèce %s (%s), blessé ou jeune au sol ? Le reconnaître, les bons gestes et qui appeler. Fiche gratuite Coup de Patte." % (nom, e["latin"])
    faq = [
        {"q": "Que faire si je trouve un jeune %s au sol ?" % nom,
         "r": "%s %s" % (e["jeune"], e["conduite"])},
        {"q": "Comment reconnaître cette espèce ?",
         "r": e["reco"]},
        {"q": "Que mange-t-il ? Faut-il le nourrir ?",
         "r": "%s Ne donne jamais à manger ni à boire de force à un oiseau sauvage trouvé en détresse, et jamais de pain ni de lait : appelle d'abord un centre de soins." % e["regime"]},
        {"q": "Qui appeler s'il est blessé ?",
         "r": "Un centre de soins de la faune sauvage. L'application Coup de Patte t'indique le plus proche et son numéro. À défaut, la LPO oriente au %s. La loi interdit de garder un oiseau sauvage chez soi." % LPO_TEL},
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "Article", "headline": "%s blessé ou jeune au sol : que faire ?" % nom, "description": desc,
         "inLanguage": "fr-FR", "mainEntityOfPage": url, "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
         "about": {"@type": "Taxon", "name": e["latin"], "alternateName": nom, "taxonRank": "species"},
         "image": SITE + "/og-accueil.png", "isAccessibleForFree": True},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"],
                                             "acceptedAnswer": {"@type": "Answer", "text": f["r"]}} for f in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Coup de Patte", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Fiches espèces", "item": SITE + "/especes/"},
            {"@type": "ListItem", "position": 3, "name": nom, "item": url}]},
    ]}
    extra = '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    out = [head(titre, desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article>')
    out.append('<nav class="fil"><a href="/">Coup de Patte</a> › <a href="/especes/">Fiches espèces</a></nav>')
    out.append('<span class="etiq">%s</span>' % esc(groupe))
    out.append('<h1>%s</h1>' % esc(nom))
    out.append('<p class="meta"><i>%s</i>%s</p>' % (esc(e["latin"]), (" · Taille : " + esc(taille)) if taille else ""))
    out.append('<p class="chapo">%s</p>' % esc(e["reco"]))
    out.append('<h2>Où le voit-on ?</h2><p>%s</p>' % esc(
        ("On le rencontre surtout dans %s." % (", ".join(milieux[:-1]) + " et " + milieux[-1] if len(milieux) > 1 else milieux[0])) if milieux else "Présent dans différents milieux en France."))
    out.append('<h2>Le jeune</h2><p>%s</p>' % esc(e["jeune"]))
    out.append('<h2>Alimentation</h2><p>%s</p>' % esc(e["regime"]))
    out.append('<section class="geste"><h2>Le bon geste</h2><p>%s</p>'
               '<p>En cas de doute, appelle un centre de soins de la faune sauvage avant toute manipulation. '
               'Ne donne ni eau ni nourriture de force, et ne le garde pas chez toi : la loi l\'interdit et il a besoin de soins adaptés.</p></section>' % esc(e["conduite"]))
    out.append(ctx["encart"])
    out.append('<h2>Questions fréquentes</h2>')
    for f in faq:
        out.append('<details><summary>%s</summary><p>%s</p></details>' % (esc(f["q"]), esc(f["r"])))
    out.append('<p class="avert">Coup de Patte informe et oriente, sans remplacer l\'avis d\'un centre de soins de la faune sauvage ou d\'un vétérinaire.</p>')
    out.append('</article>')
    if autres:
        out.append('<h2>Autres %s</h2><ul>%s</ul>' % (esc(groupe_pl), "".join(
            '<li><a href="/especes/%s/">%s</a></li>' % (esc(espece_slug(o, slugify)), esc(o["nom"])) for o in autres[:8])))
    out.append('<p><a href="/centres/">Trouver un centre de soins par département</a></p>')
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


def render_especes_index(especes, ctx):
    esc, SITE, ORG, head, FOOT, slugify = ctx["esc"], ctx["SITE"], ctx["ORG"], ctx["head"], ctx["FOOT"], ctx["slugify"]
    url = SITE + "/especes/"
    desc = "Les fiches de %d espèces d'oiseaux de France : les reconnaître, reconnaître leurs jeunes, et que faire si tu en trouves un blessé ou au sol. Par l'association Coup de Patte." % len(especes)
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "CollectionPage", "name": "Fiches espèces : que faire pour chaque oiseau", "url": url, "description": desc,
        "publisher": {"@id": ORG["@id"]},
        "hasPart": [{"@type": "Article", "headline": e["nom"], "url": "%s/especes/%s/" % (SITE, espece_slug(e, slugify))} for e in especes]}]}
    out = [head("Fiches espèces : que faire pour chaque oiseau trouvé | Coup de Patte", desc, url, SITE + "/og-accueil.png",
                '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))]
    out.append('<main><nav class="fil"><a href="/">Coup de Patte</a> › Fiches espèces</nav>')
    out.append('<h1>Fiches espèces</h1>')
    out.append('<p class="chapo">%d oiseaux que tu peux croiser en France, en ville comme à la campagne : comment les reconnaître, à quoi ressemblent leurs jeunes, et le bon geste si tu en trouves un en détresse.</p>' % len(especes))
    for key, (label, pl) in GROUPES.items():
        grp = sorted([e for e in especes if e.get("groupe") == key], key=lambda e: e["nom"])
        if not grp:
            continue
        out.append('<h2>%s</h2><ul>%s</ul>' % (esc(pl[0].upper() + pl[1:]), "".join(
            '<li><a href="/especes/%s/">%s</a> <i style="color:var(--doux)">%s</i></li>' % (esc(espece_slug(e, slugify)), esc(e["nom"]), esc(e["latin"])) for e in grp)))
    out.append(ctx["encart"])
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


# ---------------------------------------------------------------- centres

def dept_slug(code, slugify):
    return "%s-%s" % (code.lower(), slugify(DEPTS.get(code, code)))


SI_ABSENT_GENERAL = ("La LPO oriente au %s. Un vétérinaire doit accueillir un animal sauvage en détresse. "
                     "Garder un oiseau sauvage chez soi est interdit." % LPO_TEL)


def si_absent_dept(centres):
    """Consigne « si personne ne répond » : celle que le centre nous a donnée, sinon la consigne générale."""
    propres = []
    for c in centres:
        if c.get("si_absent") and c["si_absent"] not in propres:
            propres.append(c["si_absent"])
    if not propres:
        return SI_ABSENT_GENERAL
    return " ".join(propres) + " Un vétérinaire doit aussi accueillir un animal sauvage en détresse, et garder un oiseau sauvage chez soi est interdit."


def _date_fr_simple(iso, ctx):
    try:
        return ctx["date_fr"](iso)
    except Exception:
        return iso


def render_centres_dept(code, centres, ctx):
    esc, SITE, ORG, head, FOOT, slugify = ctx["esc"], ctx["SITE"], ctx["ORG"], ctx["head"], ctx["FOOT"], ctx["slugify"]
    nomd = DEPTS.get(code, code)
    url = "%s/centres/%s/" % (SITE, dept_slug(code, slugify))
    n = len(centres)
    titre = "Oiseau blessé, %s (%s) : qui appeler ? Centres de soins faune sauvage | Coup de Patte" % (nomd, code)
    villes = ", ".join(sorted(set(c["ville"] for c in centres)))
    desc = ("Oiseau ou animal sauvage blessé dans le département %s (%s) ? %d centre%s de soins à appeler (%s), "
            "les bons gestes avant d'y aller. Liste gratuite Coup de Patte.") % (nomd, code, n, "s" if n > 1 else "", villes)
    items = []
    for c in centres:
        t_aff, t_int = _tel(c.get("tel"))
        it = {"@type": "Organization", "name": c["nom"],
              "address": {"@type": "PostalAddress", "addressLocality": c["ville"], "addressRegion": nomd, "addressCountry": "FR"}}
        if t_int:
            it["telephone"] = t_int
        if c.get("site"):
            it["url"] = c["site"]
        if c.get("email"):
            it["email"] = c["email"]
        if c.get("lat") and c.get("lon"):
            it["location"] = {"@type": "Place", "geo": {"@type": "GeoCoordinates", "latitude": c["lat"], "longitude": c["lon"]}}
        items.append(it)
    faq = [
        {"q": "Où emmener un oiseau blessé dans le département %s (%s) ?" % (nomd, code),
         "r": "Appelle d'abord l'un de ces centres de soins de la faune sauvage : %s. Ils te diront s'il faut l'apporter et comment le transporter." % "; ".join(
             "%s à %s%s" % (c["nom"], c["ville"], (" (" + _tel(c.get("tel"))[0] + ")") if c.get("tel") else "") for c in centres)},
        {"q": "Que faire avant d'appeler ?",
         "r": "Place l'oiseau dans un carton aéré, au calme, au chaud et dans le noir. Ne lui donne ni à boire ni à manger de force, et ne le manipule pas plus que nécessaire."},
        {"q": "Et si aucun centre ne répond ?",
         "r": si_absent_dept(centres)},
    ]
    ld = {"@context": "https://schema.org", "@graph": [
        ORG,
        {"@type": "WebPage", "name": "Centres de soins de la faune sauvage : %s (%s)" % (nomd, code), "url": url, "description": desc,
         "inLanguage": "fr-FR", "publisher": {"@id": ORG["@id"]},
         "mainEntity": {"@type": "ItemList", "numberOfItems": n,
                        "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": it} for i, it in enumerate(items)]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"],
                                             "acceptedAnswer": {"@type": "Answer", "text": f["r"]}} for f in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Coup de Patte", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Centres de soins", "item": SITE + "/centres/"},
            {"@type": "ListItem", "position": 3, "name": "%s (%s)" % (nomd, code), "item": url}]},
    ]}
    extra = '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    out = [head(titre, desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article>')
    out.append('<nav class="fil"><a href="/">Coup de Patte</a> › <a href="/centres/">Centres de soins</a></nav>')
    out.append('<span class="etiq">%s</span>' % esc(code))
    out.append('<h1>Centres de soins de la faune sauvage : %s</h1>' % esc(nomd))
    out.append('<p class="chapo">Tu as trouvé un oiseau ou un animal sauvage blessé dans le département %s ? Appelle avant de te déplacer : le centre te dira quoi faire et s\'il peut l\'accueillir.</p>' % esc(nomd))
    for c in centres:
        t_aff, t_int = _tel(c.get("tel"))
        lignes = ['<b style="display:block;font-family:Fraunces,Georgia,serif;font-size:19px">%s</b>' % esc(c["nom"]),
                  '<span>%s</span>' % (esc(c["ville"]) if c.get("_couvre") else "%s (%s)" % (esc(c["ville"]), esc(code)))]
        if t_int:
            lignes.append('<p style="margin:8px 0 0"><a class="btn" href="tel:%s">Appeler le %s</a></p>' % (esc(t_int), esc(t_aff)))
        if c.get("_couvre"):
            lignes.append('<p style="margin:6px 0 0;font-size:15px"><b>Centre de référence pour ce département.</b></p>')
        if c.get("valide_par_centre"):
            lignes.append('<p style="margin:6px 0 0;font-size:14px;color:var(--vert,#1F9E67)">&#10003; Fiche relue et validée par le centre le %s</p>'
                          % esc(_date_fr_simple(c["valide_par_centre"], ctx)))
        if c.get("accueil"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px"><b>Animaux accueillis :</b> %s</p>' % esc(c["accueil"]))
        elif c.get("note"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px">%s</p>' % esc(c["note"]))
        if c.get("acces"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px"><b>Accès :</b> %s</p>' % esc(c["acces"]))
        if c.get("horaires"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px"><b>Horaires :</b> %s</p>' % esc(c["horaires"]))
        if c.get("presentation"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px">%s</p>' % esc(c["presentation"]))
        liens = []
        if c.get("email"):
            liens.append('<a href="mailto:%s">%s</a>' % (esc(c["email"]), esc(c["email"])))
        if c.get("site"):
            liens.append('<a href="%s" rel="noopener" target="_blank">Site du centre</a>' % esc(c["site"]))
        if c.get("conseils_url") and c.get("conseils_url") != c.get("site"):
            liens.append('<a href="%s" rel="noopener" target="_blank">Fiches conseils du centre</a>' % esc(c["conseils_url"]))
        if liens:
            lignes.append('<p style="margin:8px 0 0">%s</p>' % " · ".join(liens))
        if c.get("si_absent"):
            lignes.append('<p style="margin:8px 0 0;font-size:15px"><b>Si personne ne répond :</b> %s</p>' % esc(c["si_absent"]))
        if c.get("don_url"):
            lignes.append('<p style="margin:10px 0 0"><a class="btn" style="background:transparent;color:inherit;border:1.5px solid currentColor" '
                          'href="%s" rel="noopener" target="_blank">Soutenir ce centre par un don</a></p>' % esc(c["don_url"]))
        out.append('<section class="encart" style="border-left-color:var(--corail)">%s</section>' % "".join(lignes))
    if centres and all((c.get("accueil") or "").lower().startswith("uniquement") for c in centres):
        out.append('<p class="avert">Ce centre n\'accueille pas toutes les espèces. Pour un autre animal, '
                   '<a href="/">l\'application Coup de Patte</a> t\'indique le centre le plus proche ; '
                   'un vétérinaire doit aussi accueillir un animal sauvage en détresse.</p>')
    out.append('<section class="geste"><h2>Le bon geste en attendant</h2><ol>'
               '<li>Place-le dans un carton aéré, avec un linge au fond.</li>'
               '<li>Garde-le au calme, au chaud et dans le noir.</li>'
               '<li>Ne lui donne ni à boire ni à manger de force.</li>'
               '<li>Appelle le centre avant de te déplacer.</li></ol></section>')
    out.append('<h2>Questions fréquentes</h2>')
    for f in faq:
        out.append('<details><summary>%s</summary><p>%s</p></details>' % (esc(f["q"]), esc(f["r"])))
    verif = sorted(set(c.get("verifie_le") or "" for c in centres if c.get("verifie_le")))
    out.append('<p class="avert">Coordonnées vérifiées par Coup de Patte%s. Une information a changé ? Signale-la depuis l\'application.</p>' % (
        (" (dernière vérification : %s)" % ctx["date_fr"](verif[-1])) if verif else ""))
    out.append('</article>')
    out.append(ctx["encart"])
    out.append('<p><a href="/centres/">Tous les départements</a> · <a href="/especes/">Fiches espèces</a></p>')
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


def render_centres_index(par_dept, ctx):
    esc, SITE, ORG, head, FOOT, slugify = ctx["esc"], ctx["SITE"], ctx["ORG"], ctx["head"], ctx["FOOT"], ctx["slugify"]
    url = SITE + "/centres/"
    total = sum(len(v) for v in par_dept.values())
    desc = "%d centres de soins de la faune sauvage dans %d départements : qui appeler pour un oiseau ou un animal sauvage blessé près de chez toi. Liste gratuite Coup de Patte." % (total, len(par_dept))
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "CollectionPage", "name": "Centres de soins de la faune sauvage par département", "url": url, "description": desc,
        "publisher": {"@id": ORG["@id"]},
        "hasPart": [{"@type": "WebPage", "name": "%s (%s)" % (DEPTS.get(d, d), d), "url": "%s/centres/%s/" % (SITE, dept_slug(d, slugify))} for d in par_dept]}]}
    out = [head("Centres de soins de la faune sauvage par département | Coup de Patte", desc, url, SITE + "/og-accueil.png",
                '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))]
    out.append('<main><nav class="fil"><a href="/">Coup de Patte</a> › Centres de soins</nav>')
    out.append('<h1>Centres de soins de la faune sauvage par département</h1>')
    out.append('<p class="chapo">%d centres qui accueillent les oiseaux, dans %d départements. Si le tien n\'y figure pas, l\'application te montre le centre le plus proche de toi, et la LPO oriente au %s.</p>' % (total, len(par_dept), LPO_TEL))
    out.append('<ul>%s</ul>' % "".join(
        '<li><a href="/centres/%s/">%s (%s)</a> : %d centre%s</li>' % (esc(dept_slug(d, slugify)), esc(DEPTS.get(d, d)), esc(d), len(v), "s" if len(v) > 1 else "")
        for d, v in par_dept.items()))
    out.append(ctx["encart"])
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


# ---------------------------------------------------------------- orchestration

def build(ctx):
    """Écrit les pages ; renvoie la liste des URL publiées pour le sitemap et llms.txt."""
    root, write, slugify, SITE = ctx["ROOT"], ctx["write"], ctx["slugify"], ctx["SITE"]
    publiees = {"especes": [], "centres": []}

    try:
        especes = load_especes(root)
    except Exception as ex:  # l'absence de Node ne doit jamais bloquer les actualités
        ctx["log"]("fiches especes ignorees :", ex)
        especes = []
    if especes:
        for e in especes:
            autres = [o for o in especes if o.get("groupe") == e.get("groupe") and o["id"] != e["id"]]
            write(os.path.join(root, "especes", espece_slug(e, slugify), "index.html"), render_espece(e, autres, ctx))
            publiees["especes"].append(("%s/especes/%s/" % (SITE, espece_slug(e, slugify)), e["nom"], e["latin"]))
        write(os.path.join(root, "especes", "index.html"), render_especes_index(especes, ctx))

    centres = load_centres(ctx["http"], ctx["SUPA"], ctx["SUPA_KEY"])
    if centres:
        par_dept = {}
        for c in centres:
            d = (c.get("dept") or "").strip().upper()
            if d in DEPTS:
                par_dept.setdefault(d, []).append(c)
        # Centres régionaux : un centre peut prendre en charge d'autres départements (ex. LPO PACA pour 13, 83, 04).
        # Il apparaît alors aussi sur leurs pages, après les centres du département.
        for c in centres:
            for d2 in (c.get("depts_couverts") or []):
                d2 = (d2 or "").strip().upper()
                if d2 in DEPTS and d2 != (c.get("dept") or "").strip().upper():
                    x = dict(c)
                    x["_couvre"] = True
                    x["ville"] = "%s (%s)" % (c["ville"], (c.get("dept") or "").strip().upper())
                    par_dept.setdefault(d2, []).append(x)
        par_dept = dict(sorted(par_dept.items(), key=lambda kv: (len(kv[0]), kv[0])))
        for d, cs in par_dept.items():
            write(os.path.join(root, "centres", dept_slug(d, slugify), "index.html"), render_centres_dept(d, cs, ctx))
            publiees["centres"].append(("%s/centres/%s/" % (SITE, dept_slug(d, slugify)), DEPTS[d], d, len(cs)))
        write(os.path.join(root, "centres", "index.html"), render_centres_index(par_dept, ctx))
    else:
        ctx["log"]("centres : base injoignable, pages existantes conservees")
        # on conserve les pages déjà publiées pour le sitemap
        base = os.path.join(root, "centres")
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                if os.path.isfile(os.path.join(base, name, "index.html")):
                    code = name.split("-", 1)[0].upper()
                    publiees["centres"].append(("%s/centres/%s/" % (SITE, name), DEPTS.get(code, code), code, 0))
    return publiees
