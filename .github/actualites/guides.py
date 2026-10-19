# -*- coding: utf-8 -*-
"""Pages permanentes de Coup de Patte : guides d'urgence et pages de l'association.

Appele par actualites.py (cmd_build) comme fiches.py. Chaque page est regeneree a
chaque publication, ajoutee au sitemap et a llms.txt.

Contenu : repris de la doctrine deja publiee dans l'application (ecrans rA, rB,
rNid, bague, gestes), elle-meme fondee sur la LPO, l'OFB et le CRBPO.
Regles de redaction : tutoiement, jamais de tiret cadratin ni demi-cadratin,
jamais « qu'on », aucune adresse e-mail visible.
"""
import json

LPO_TEL = "05 46 82 12 34"

SRC = {
    "lpo_oisillon": ("J'ai trouvé un jeune oisillon, que faire ?", "LPO",
                     "https://www.lpo.fr/decouvrir-la-nature/conseils-biodiversite/conseils-biodiversite/accueillir-la-faune-sauvage/j-ai-trouve-un-jeune-oisillon-que-faire"),
    "lpo_secourir": ("Secourir un animal sauvage", "LPO",
                     "https://www.lpo.fr/la-lpo-en-actions/agir-pour-la-faune-en-detresse/secourir-un-animal-sauvage"),
    "lpo_guide": ("Secourir un animal sauvage en détresse (guide 2024)", "LPO",
                  "https://www.lpo.fr/media/read/9877/file/SECOURIR%20ANIMAL%20DETRESSE%202024V5WEB.pdf"),
    "lpo_centres": ("Les centres de soins de la faune sauvage", "LPO",
                    "https://www.lpo.fr/la-lpo-en-actions/agir-pour-la-faune-en-detresse/centres-de-soins"),
    "lpo_martinets": ("Cohabiter avec les martinets", "LPO",
                      "https://www.lpo.fr/decouvrir-la-nature/conseils-biodiversite/conseils-biodiversite/accueillir-la-faune-sauvage/cohabiter-avec-les-martinets"),
    "lpo_nord_oisillon": ("J'ai trouvé un oisillon au sol, que faire ?", "LPO Nord",
                          "https://nord.lpo.fr/wp-content/uploads/2021/03/Jai-trouve-un-oisillon-au-sol-que-faire.pdf"),
    "lpo_herault": ("Replacer un jeune oiseau", "LPO Hérault",
                    "https://herault.lpo.fr/wp-content/uploads/2020/07/Replacement-oiseaux.pdf"),
    "crbpo": ("Vous avez trouvé un oiseau bagué", "CRBPO, Muséum national d'Histoire naturelle",
              "https://crbpo.mnhn.fr/vous-trouvez-un-oiseau-bague/article/vous-avez-trouve-un-oiseau-bague-et-vous-voudriez-en-connaitre-un-peu-plus-sur"),
    "ofb_baguage": ("Le baguage, un outil pour suivre les populations d'oiseaux", "OFB",
                    "https://ofb.gouv.fr/doc/le-baguage-un-outil-pour-suivre-les-populations-oiseaux"),
}

GUIDES = [
    {
        "slug": "oisillon-tombe-du-nid",
        "titre": "Oisillon ou bébé oiseau tombé du nid : que faire ?",
        "court": "Oisillon tombé du nid",
        "desc": "Bébé oiseau par terre ? Emplumé, il n'est presque jamais abandonné : laisse-le. Nu ou en duvet, remets-le au nid. Comment s'en occuper, quand appeler un centre de soins.",
        "chapo": "Un oisillon au sol n'est pas forcément en danger. Avant de le ramasser, regarde s'il a des plumes : c'est ce détail qui décide de tout.",
        "sections": [
            ("Il a ses plumes et il sautille : laisse-le", [
                "Un jeune bien emplumé qui sautille ou volette au sol est presque toujours un jeune qui apprend à voler. C'est un « sauteur ». Il a quitté le nid volontairement et ses parents continuent de le nourrir tout près, même si tu ne les vois pas.",
                "Le bon réflexe : éloigne-toi et observe de loin. Les parents reviennent dès que la voie est libre. S'il est exposé (route, trottoir, plein soleil), pose-le en hauteur tout près, sur une branche, un muret ou dans un buisson, à quelques mètres seulement de l'endroit où tu l'as trouvé.",
                "Le toucher n'entraîne aucun rejet de la part des parents. Lave-toi simplement les mains après.",
            ]),
            ("Il est nu, rose ou en duvet : remets-le au nid", [
                "Un oisillon sans plumes ou couvert de duvet est tombé trop tôt. S'il ne retourne pas au nid, il a besoin d'aide.",
                "Si le nid est intact et accessible, replace-le délicatement dedans. Si le nid est tombé ou détruit, recrée un nid sommaire dans une petite boîte ou un panier tapissé, fixé au même endroit, le plus haut possible. Les parents continuent souvent à nourrir leurs petits.",
                "S'il est rose, froid ou si le nid est introuvable, garde-le au chaud dans un linge, au calme et dans le noir, et appelle tout de suite un centre de soins de la faune sauvage.",
            ]),
            ("Quand faut-il l'emmener en centre de soins ?", [
                "Appelle un centre s'il est blessé (sang, aile qui pend, patte abîmée), s'il a été attrapé par un chat, s'il est léthargique, couvert de mouches ou de fourmis, ou si aucun parent n'est revenu après une longue observation.",
                "Appelle toujours avant de te déplacer : le centre te dira quoi faire et s'il peut l'accueillir. L'application Coup de Patte t'indique le centre le plus proche et son numéro.",
            ]),
        ],
        "gestes": [
            "Observe d'abord de loin : un jeune emplumé au sol est presque toujours surveillé par ses parents.",
            "Emplumé et exposé : pose-le en hauteur, tout près, à l'abri.",
            "Nu ou en duvet : remets-le au nid, ou recrée un nid au même endroit.",
            "Rentre les chats quelques heures.",
            "Ne lui donne ni eau ni nourriture, jamais de pain ni de lait.",
            "Blessé, froid ou nid introuvable : au chaud, au calme, et appelle un centre de soins.",
        ],
        "faq": [
            ("Les parents vont-ils rejeter l'oisillon si je le touche ?",
             "Non. Les oiseaux ne rejettent pas leurs petits à cause de l'odeur humaine. Tu peux le replacer au nid ou le poser à l'abri, puis te laver les mains."),
            ("Faut-il donner à boire ou à manger à un oisillon ?",
             "Non. Ne lui donne ni eau ni nourriture : l'eau peut partir dans ses voies respiratoires, et le pain ou le lait le rendent malade. Chaque espèce a un régime précis. En cas de doute, appelle un centre de soins."),
            ("Puis-je le garder pour l'élever moi-même ?",
             "Non. La détention d'un oiseau sauvage est interdite, et un oisillon élevé par l'humain ne peut généralement plus être relâché. Le centre de soins a les compétences et les autorisations."),
            ("Comment s'occuper d'un oisillon tombé du nid ?",
             "Le mieux est de ne pas s'en occuper toi-même : remets-le au nid, ou laisse-le près de l'endroit où tu l'as trouvé s'il a ses plumes, pour que ses parents continuent de le nourrir. S'il est seul, blessé ou froid, garde-le au chaud, au calme et dans le noir sans le nourrir, et appelle un centre de soins de la faune sauvage."),
            ("Combien de temps un jeune reste-t-il au sol ?",
             "Quelques jours chez beaucoup de passereaux, le temps que ses plumes de vol poussent. C'est une étape normale de sa croissance."),
        ],
        "sources": ["lpo_oisillon", "lpo_nord_oisillon", "lpo_herault"],
        "liens": [("/especes/merle-noir/", "Fiche merle noir"), ("/especes/", "Toutes les fiches espèces"), ("/centres/", "Centres de soins par département")],
    },
    {
        "slug": "oiseau-blesse",
        "titre": "J'ai trouvé un oiseau blessé : que faire et qui appeler ?",
        "court": "Oiseau blessé",
        "h1": "J'ai trouvé un oiseau blessé : que faire ?",
        "desc": "Oiseau blessé dans ton jardin ou dans la rue ? Comment t'en occuper en attendant : carton aéré, calme, chaleur, ni eau ni nourriture. Et qui appeler près de chez toi.",
        "chapo": "Un oiseau blessé a besoin de calme et d'un centre de soins de la faune sauvage, pas de soins improvisés. Voici les gestes qui l'aident vraiment, dans l'ordre.",
        "sections": [
            ("D'abord, observe : est-il vraiment en détresse ?", [
                "Trop d'oiseaux sont ramassés inutilement. Interviens s'il est manifestement blessé (aile qui pend, saignement, patte abîmée), s'il ne s'enfuit pas à ton approche, s'il est en danger immédiat (route, chat, plein soleil) ou s'il a été attrapé par un chat, même sans blessure visible.",
                "Un oiseau qui vient de percuter une vitre peut être simplement sonné : mets-le dans un carton aéré, au calme et dans le noir, et vérifie au bout d'une heure ou deux s'il peut repartir.",
            ]),
            ("Comment s'occuper d'un oiseau blessé en attendant le centre", [
                "Protège-toi d'abord : des gants, et attention aux serres des rapaces et au bec des hérons, qui visent le visage. Jette un tissu épais (serviette, vêtement) sur l'oiseau : dans l'obscurité, il se calme. Maintiens les ailes collées au corps.",
                "Place-le dans un carton percé de trous, tapissé d'un linge, jamais dans une cage. Garde-le au calme, au chaud et dans le noir, loin des enfants et des animaux.",
            ]),
            ("Appeler un centre de soins de la faune sauvage", [
                "Appelle un centre avant de te déplacer : il te dit quoi faire et s'il peut accueillir l'oiseau. Note le lieu exact de la découverte, il servira pour le relâcher. L'application Coup de Patte t'indique le centre le plus proche et son numéro. À défaut, la LPO oriente au " + LPO_TEL + ".",
                "Pendant le trajet, reste au calme, sans musique, et n'ouvre pas le carton pour vérifier.",
            ]),
            ("Que lui donner à manger ? Rien, et ce n'est pas de la cruauté", [
                "Ne le force jamais à boire : l'eau peut partir dans ses voies respiratoires. Pas de pain, pas de lait, pas de viande hachée : en cas de doute, ni à manger ni à boire.",
                "Ne bloque jamais le bec, ne le montre pas, ne multiplie pas les photos : le stress aggrave son état. Ne tente pas de le soigner ni de le garder : la détention d'un oiseau sauvage est interdite et il a besoin de soins adaptés.",
            ]),
        ],
        "gestes": [
            "Protège-toi (gants, attention au bec et aux serres).",
            "Couvre-le d'un tissu épais pour le calmer.",
            "Carton aéré tapissé d'un linge, au calme, au chaud et dans le noir.",
            "Ni eau ni nourriture.",
            "Appelle un centre de soins avant de te déplacer, et note le lieu exact.",
            "Lave-toi les mains après tout contact.",
        ],
        "faq": [
            ("Qui appeler pour un oiseau blessé ?",
             "Un centre de soins de la faune sauvage. L'application gratuite Coup de Patte t'indique le plus proche et son numéro. À défaut, la LPO oriente au " + LPO_TEL + ". Un vétérinaire peut aussi accueillir un animal sauvage en détresse en urgence."),
            ("Un oiseau attrapé par un chat, sans blessure visible, doit-il aller en centre ?",
             "Oui. La morsure d'un chat transmet des bactéries qui provoquent très vite une infection grave, même sans plaie visible. Le traitement relève d'un centre de soins : appelle-le sans attendre."),
            ("Puis-je le soigner chez moi ?",
             "Non. La loi interdit de détenir un oiseau sauvage, et les soins demandent des compétences et des médicaments spécifiques. Ton rôle est de le mettre à l'abri et de le confier à un centre."),
            ("Comment soigner un oiseau blessé ?",
             "Tu n'as pas à le soigner toi-même, et ce serait risqué pour lui : une aile cassée, une infection ou un choc demandent un examen et des soins de professionnels. Ton rôle est de le mettre à l'abri dans un carton, au calme, au chaud et dans le noir, puis d'appeler un centre de soins de la faune sauvage."),
            ("Que donner à manger à un oiseau blessé ?",
             "Rien. Un oiseau blessé est en état de choc : le nourrir ou le faire boire de force peut le tuer, et chaque espèce a un régime différent. Ni pain, ni lait, ni viande hachée. Le centre de soins te dira quoi faire."),
            ("Un oiseau blessé dans mon jardin ne s'envole plus, que faire ?",
             "Rentre d'abord les chats et les chiens. Observe-le quelques minutes de loin : un jeune emplumé qui sautille n'est pas blessé, ses parents s'en occupent. S'il a une aile qui pend, saigne, ne fuit pas à ton approche ou a été attrapé par un chat, mets-le dans un carton aéré et appelle un centre de soins."),
            ("Oiseau avec une aile cassée : que faire ?",
             "Ne tente pas de bander ou de remettre l'aile. Maintiens doucement les ailes contre le corps avec un tissu, place l'oiseau dans un carton aéré, au calme et dans le noir, et appelle vite un centre de soins de la faune sauvage."),
            ("Et si c'est un pigeon ?",
             "Les mêmes gestes s'appliquent. Appelle un centre de soins avant de te déplacer pour savoir s'il accueille les pigeons."),
        ],
        "sources": ["lpo_secourir", "lpo_guide", "lpo_centres"],
        "liens": [("/guides/oiseau-au-sol-ne-vole-pas/", "Oiseau par terre qui ne s'envole pas"), ("/actualites/pigeon-blesse-en-ville-que-faire/", "Pigeon blessé en ville"), ("/actualites/oiseau-cogne-contre-une-vitre-que-faire/", "Oiseau qui a heurté une vitre"), ("/actualites/mon-chat-a-attrape-un-oiseau-que-faire/", "Mon chat a attrapé un oiseau"), ("/centres/", "Centres de soins par département")],
    },
    {
        "slug": "oiseau-au-sol-ne-vole-pas",
        "titre": "Oiseau par terre qui ne s'envole pas : que faire ?",
        "court": "Oiseau au sol qui ne vole pas",
        "desc": "Un oiseau au sol dans ton jardin ou dans la rue, qui ne s'envole plus ? Jeune qui apprend à voler, oiseau assommé, blessé ou martinet : reconnaître le cas et faire le bon geste.",
        "chapo": "Un oiseau qui reste par terre n'est pas toujours en danger. Avant d'agir, prends une minute pour comprendre ce que tu as devant toi : le bon geste n'est pas le même pour un jeune qui apprend à voler, un oiseau sonné ou un oiseau blessé.",
        "sections": [
            ("1. Il a ses plumes, il sautille ou volette : c'est un jeune", [
                "C'est le cas le plus fréquent au printemps et en été. Le jeune a quitté le nid avant de savoir bien voler et ses parents le nourrissent tout près. Laisse-le, rentre les chats, et s'il est exposé, pose-le en hauteur dans un buisson tout proche.",
            ]),
            ("2. Il est nu ou en duvet : il est tombé du nid", [
                "Remets-le au nid s'il est accessible, ou recrée un nid sommaire au même endroit. S'il est seul et froid, garde-le au chaud dans un linge et appelle un centre de soins.",
            ]),
            ("3. Il vient de heurter une vitre : il est peut-être sonné", [
                "Un oiseau assommé reste immobile, parfois les yeux mi-clos. Mets-le dans un carton aéré, au calme et dans le noir, à l'abri des chats, et regarde au bout d'une heure ou deux s'il peut repartir en ouvrant le carton dehors. S'il ne repart pas, appelle un centre de soins.",
            ]),
            ("4. Aile qui pend, sang, ne fuit pas : il est blessé", [
                "Couvre-le d'un tissu, mets-le dans un carton aéré tapissé d'un linge, au calme, au chaud et dans le noir, sans eau ni nourriture, et appelle un centre de soins de la faune sauvage avant de te déplacer.",
            ]),
            ("5. Ailes en croissant, toutes petites pattes : c'est un martinet", [
                "Un martinet ne peut pas redécoller du sol. Ne le lance jamais en l'air. Mets-le dans un carton aéré et appelle un centre de soins.",
            ]),
            ("6. Il a été attrapé par un chat", [
                "Même sans blessure visible, il doit aller en centre de soins : la morsure d'un chat transmet des bactéries qui provoquent très vite une infection grave.",
            ]),
        ],
        "gestes": [
            "Rentre les chats et les chiens.",
            "Observe une minute de loin avant de toucher.",
            "Jeune emplumé qui sautille : laisse-le, ses parents veillent.",
            "Sonné, blessé, martinet ou attrapé par un chat : carton aéré, calme, noir.",
            "Ni eau ni nourriture.",
            "En cas de doute, appelle un centre de soins de la faune sauvage.",
        ],
        "faq": [
            ("J'ai trouvé un oiseau par terre, que faire ?",
             "Observe-le d'abord de loin : s'il a ses plumes et sautille, c'est un jeune surveillé par ses parents, laisse-le. S'il est nu, remets-le au nid. S'il est sonné, blessé, si c'est un martinet ou s'il a été attrapé par un chat, mets-le dans un carton aéré au calme et appelle un centre de soins."),
            ("Pourquoi un oiseau reste-t-il au sol sans s'envoler ?",
             "Le plus souvent parce que c'est un jeune qui apprend à voler. Sinon, il peut être sonné après un choc contre une vitre, blessé, affaibli, ou être un martinet, incapable de décoller du sol."),
            ("Comment aider un oiseau qui ne vole plus ?",
             "Mets-le à l'abri des prédateurs dans un carton aéré, au calme et dans le noir, sans lui donner à manger ni à boire, et appelle un centre de soins de la faune sauvage. L'application Coup de Patte t'indique le plus proche."),
            ("Faut-il le lancer en l'air pour l'aider à s'envoler ?",
             "Non, jamais. Un oiseau qui ne s'envole pas a une raison : le lancer peut le blesser gravement, surtout un martinet ou un jeune."),
        ],
        "sources": ["lpo_secourir", "lpo_oisillon", "lpo_martinets", "lpo_guide"],
        "liens": [("/guides/oiseau-blesse/", "J'ai trouvé un oiseau blessé"), ("/guides/oisillon-tombe-du-nid/", "Oisillon tombé du nid"), ("/guides/martinet-au-sol/", "Martinet au sol"), ("/actualites/oiseau-cogne-contre-une-vitre-que-faire/", "Oiseau qui a heurté une vitre"), ("/actualites/mon-chat-a-attrape-un-oiseau-que-faire/", "Mon chat a attrapé un oiseau")],
    },
    {
        "slug": "martinet-au-sol",
        "titre": "Martinet au sol : que faire ?",
        "court": "Martinet au sol",
        "desc": "Un martinet au sol ne peut pas redécoller seul. Ne le lance jamais en l'air : mets-le à l'abri dans un carton et appelle un centre de soins. Le guide Coup de Patte.",
        "chapo": "Le martinet vit en vol presque toute sa vie. Au sol, il est en détresse : ses pattes minuscules ne lui permettent pas de reprendre son envol. Il a besoin de toi, et des bons gestes.",
        "sections": [
            ("Le reconnaître", [
                "Le martinet noir a de longues ailes en forme de croissant, un plumage sombre et de toutes petites pattes. Il est souvent confondu avec une hirondelle, mais il est plus grand, entièrement sombre, et il ne se pose pas sur les fils.",
                "Les martinets au sol se trouvent surtout de mai à août, en ville, quand les jeunes quittent leurs nids sous les toits ou que les fortes chaleurs les poussent à sortir trop tôt.",
            ]),
            ("Ne le lance jamais en l'air", [
                "Lancer un martinet est le geste le plus dangereux : s'il est trop jeune, affaibli ou blessé, il retombe et se blesse. C'est la première cause d'aggravation.",
                "Un adulte intact peut parfois repartir seul : présente-le sur ta main ouverte à plat, en légère pente, au-dessus d'une pelouse. S'il s'envole de lui-même, parfait. S'il ne part pas, n'insiste pas.",
            ]),
            ("Le mettre à l'abri et appeler un centre", [
                "Place-le dans un carton aéré tapissé d'un linge, au calme et à température ambiante. Appelle un centre de soins de la faune sauvage : le martinet demande des soins très spécialisés. L'application Coup de Patte t'indique le plus proche.",
                "Ne lui donne ni eau ni nourriture : il se nourrit uniquement d'insectes capturés en vol, et un mauvais aliment ou de l'eau donnée de force peut le tuer.",
            ]),
        ],
        "gestes": [
            "Ne le lance jamais en l'air.",
            "Carton aéré, linge au fond, au calme.",
            "Ni eau ni nourriture.",
            "Adulte intact : main ouverte à plat au-dessus d'une pelouse, sans forcer.",
            "Dans tous les autres cas, appelle un centre de soins.",
        ],
        "faq": [
            ("Un martinet peut-il redécoller du sol ?",
             "Rarement. Ses pattes sont trop courtes et ses ailes trop longues pour décoller depuis une surface plane. Au sol, il a presque toujours besoin d'aide."),
            ("Que mange un martinet ?",
             "Uniquement des insectes attrapés en vol. Ne lui donne rien : seul un centre de soins sait le nourrir correctement."),
            ("Comment savoir si c'est un jeune ?",
             "Un jeune a souvent des plumes bordées de clair sur le front et les ailes, et n'a encore jamais volé. Ne le lance surtout pas : appelle un centre."),
        ],
        "sources": ["lpo_martinets", "lpo_secourir"],
        "liens": [("/especes/martinet-noir/", "Fiche martinet noir"), ("/centres/", "Centres de soins par département")],
    },
    {
        "slug": "oiseau-bague",
        "titre": "Oiseau bagué : que faire ?",
        "court": "Oiseau bagué",
        "desc": "Tu as trouvé un oiseau bagué, vivant ou mort ? Ne retire pas la bague : note le code et signale-le au Muséum (CRBPO). Tu recevras son histoire. Le guide Coup de Patte.",
        "chapo": "Une bague à la patte raconte la vie d'un oiseau : où il est né, par où il migre, combien de temps il vit. Ton signalement fait avancer la science, et tu reçois son histoire en retour.",
        "sections": [
            ("Quel type de bague ?", [
                "Bague en métal gravée : un petit anneau gris, souvent marqué MUSEUM PARIS ou le nom d'une capitale étrangère. C'est une bague scientifique, posée par un bagueur agréé.",
                "Bague ou marque de couleur : plastique coloré avec un code lisible de loin, parfois une marque à l'aile ou un collier. Elles permettent de suivre un oiseau sans le capturer.",
                "Anneau fermé, sans ouverture : c'est en général un pigeon voyageur ou un oiseau d'élevage échappé, à signaler à son propriétaire via la fédération colombophile.",
            ]),
            ("Les bons gestes", [
                "Ne retire jamais la bague d'un oiseau vivant. Note le code complet, la couleur, la patte (gauche ou droite), la date et le lieu exact. Une photo nette de la bague est idéale, sans stresser l'oiseau.",
                "S'il est vivant et en forme, laisse-le repartir. S'il est blessé ou affaibli, suis les gestes d'un oiseau blessé et appelle un centre de soins, en précisant qu'il est bagué. S'il est mort, tu peux signaler la bague : c'est une donnée précieuse.",
            ]),
            ("Signaler au Muséum (CRBPO)", [
                "En France, les bagues scientifiques sont gérées par le Centre de recherches sur la biologie des populations d'oiseaux (CRBPO) du Muséum national d'Histoire naturelle. Le signalement est gratuit et tu reçois en retour l'historique de l'oiseau.",
                "L'application Coup de Patte te guide pas à pas pour préparer ton signalement et l'envoyer au bon organisme.",
            ]),
        ],
        "gestes": [
            "Ne retire jamais la bague d'un oiseau vivant.",
            "Note le code, la couleur, la patte, la date et le lieu ; prends une photo nette.",
            "Vivant et en forme : laisse-le repartir.",
            "Blessé : carton, calme, centre de soins, en signalant la bague.",
            "Signale la bague au Muséum (CRBPO) avec l'application Coup de Patte.",
        ],
        "faq": [
            ("À quoi sert le baguage des oiseaux ?",
             "À suivre les déplacements, la durée de vie et l'état des populations d'oiseaux. Chaque bague retrouvée et signalée apporte une information scientifique."),
            ("Dois-je retirer la bague d'un oiseau mort ?",
             "Tu peux la récupérer si c'est facile, mais le plus utile est de noter le code complet et le lieu, puis de le signaler. Ne touche pas à mains nues un oiseau mort et lave-toi les mains."),
            ("Vais-je savoir d'où vient l'oiseau ?",
             "Oui, en général. Après ton signalement au CRBPO, tu reçois l'historique de l'oiseau : lieu et date de baguage, âge, déplacements connus."),
        ],
        "sources": ["crbpo", "ofb_baguage"],
        "liens": [("/actualites/oiseau-mort-trouve-que-faire/", "Oiseau mort trouvé : que faire ?"), ("/guides/oiseau-blesse/", "Oiseau blessé : que faire ?")],
    },
]


def _ld(ctx, page_type, titre, desc, url, faq=None, crumb=None, sources=None):
    SITE, ORG = ctx["SITE"], ctx["ORG"]
    g = [ORG, {"@type": page_type, "headline": titre, "name": titre, "description": desc, "inLanguage": "fr-FR",
               "url": url, "mainEntityOfPage": url, "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
               "image": SITE + "/og-accueil.png", "isAccessibleForFree": True}]
    if sources:
        g[1]["citation"] = [SRC[s][2] for s in sources]
    if page_type in ("AboutPage", "WebPage"):
        g[1]["about"] = {"@id": ORG["@id"]}
    if faq:
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                                                     "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]})
    items = [{"@type": "ListItem", "position": 1, "name": "Coup de Patte", "item": SITE + "/"}]
    for i, (n, u) in enumerate(crumb or [], start=2):
        items.append({"@type": "ListItem", "position": i, "name": n, "item": u})
    g.append({"@type": "BreadcrumbList", "itemListElement": items})
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@graph": g}, ensure_ascii=False).replace("</", "<\\/")


def _faq_html(esc, faq):
    out = ['<h2>Questions fréquentes</h2>']
    for q, r in faq:
        out.append('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(r)))
    return "".join(out)


def _sources_html(esc, keys):
    out = ['<section class="pied-sources" id="sources"><h2>Sources</h2><ol>']
    for k in keys:
        t, ed, u = SRC[k]
        out.append('<li><a href="%s" rel="noopener" target="_blank">%s</a>, %s</li>' % (esc(u), esc(t), esc(ed)))
    out.append('</ol><p>Consignes reformulées par Coup de Patte à partir de ces sources et de la pratique des centres de soins de la faune sauvage.</p></section>')
    return "".join(out)


def render_guide(g, ctx):
    esc, SITE, head, FOOT = ctx["esc"], ctx["SITE"], ctx["head"], ctx["FOOT"]
    url = "%s/guides/%s/" % (SITE, g["slug"])
    extra = _ld(ctx, "Article", g["titre"], g["desc"], url, g["faq"],
                [("Guides", SITE + "/guides/"), (g["court"], url)], g["sources"])
    out = [head(g["titre"] + " | Coup de Patte", g["desc"], url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article>')
    out.append('<nav class="fil"><a href="/">Coup de Patte</a> › <a href="/guides/">Guides</a></nav>')
    out.append('<span class="etiq">Guide d\'urgence</span>')
    out.append('<h1>%s</h1>' % esc(g.get("h1") or g["titre"]))
    out.append('<p class="meta">Rédaction Coup de Patte · <a href="#sources">%d sources</a></p>' % len(g["sources"]))
    out.append('<p class="chapo">%s</p>' % esc(g["chapo"]))
    out.append('<section class="geste"><h2>L\'essentiel en 30 secondes</h2><ol>%s</ol></section>'
               % "".join("<li>%s</li>" % esc(x) for x in g["gestes"]))
    for titre, paras in g["sections"]:
        out.append('<h2>%s</h2>' % esc(titre))
        for p in paras:
            out.append('<p>%s</p>' % esc(p))
    out.append(ctx["encart"])
    out.append(_faq_html(esc, g["faq"]))
    if g.get("liens"):
        out.append('<h2>Pour aller plus loin</h2><ul>%s</ul>' % "".join(
            '<li><a href="%s">%s</a></li>' % (esc(u), esc(t)) for u, t in g["liens"]))
    out.append('<p class="avert">Coup de Patte informe et oriente, sans remplacer l\'avis d\'un centre de soins de la faune sauvage ou d\'un vétérinaire.</p>')
    out.append('</article></main>')
    out.append(_sources_html(esc, g["sources"]))
    out.append(FOOT)
    return "\n".join(out)


def render_guides_index(ctx):
    esc, SITE, head, FOOT = ctx["esc"], ctx["SITE"], ctx["head"], ctx["FOOT"]
    url = SITE + "/guides/"
    titre = "Guides d'urgence : secourir un oiseau ou un animal sauvage"
    desc = "Oisillon tombé du nid, oiseau blessé, martinet au sol, oiseau bagué : les guides gratuits de l'association Coup de Patte pour faire le bon geste en moins d'une minute."
    extra = _ld(ctx, "CollectionPage", titre, desc, url, None, [("Guides", url)])
    out = [head(titre + " | Coup de Patte", desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><nav class="fil"><a href="/">Coup de Patte</a> › Guides</nav>')
    out.append('<h1>%s</h1>' % esc(titre))
    out.append('<p class="chapo">Les situations les plus fréquentes, et les gestes qui sauvent. Pour un diagnostic en 3 questions et le centre de soins le plus proche, ouvre l\'application.</p>')
    out.append('<ul>')
    for g in GUIDES:
        out.append('<li><a href="/guides/%s/"><b>%s</b></a><br>%s</li>' % (esc(g["slug"]), esc(g["titre"]), esc(g["desc"])))
    out.append('</ul>')
    out.append('<h2>Autres situations</h2><ul>'
               '<li><a href="/actualites/pigeon-blesse-en-ville-que-faire/">Pigeon blessé en ville</a></li>'
               '<li><a href="/actualites/herisson-trouve-en-plein-jour-en-automne-que-faire/">Hérisson trouvé en plein jour</a></li>'
               '<li><a href="/actualites/mon-chat-a-attrape-un-oiseau-que-faire/">Mon chat a attrapé un oiseau</a></li>'
               '<li><a href="/actualites/oiseau-cogne-contre-une-vitre-que-faire/">Oiseau qui a heurté une vitre</a></li>'
               '<li><a href="/actualites/chouette-blessee-au-sol-que-faire/">Chouette blessée au sol</a></li>'
               '<li><a href="/actualites/chauve-souris-dans-la-maison-que-faire/">Chauve-souris dans la maison</a></li>'
               '<li><a href="/actualites/oiseau-mort-trouve-que-faire/">Oiseau mort trouvé</a></li>'
               '</ul>')
    out.append(ctx["encart"])
    out.append('</main>')
    out.append(FOOT)
    return "\n".join(out)


def render_association(ctx):
    esc, SITE, head, FOOT = ctx["esc"], ctx["SITE"], ctx["head"], ctx["FOOT"]
    url = SITE + "/association/"
    titre = "L'association Coup de Patte, secours à la faune sauvage"
    desc = "Coup de Patte est une association loi 1901 de Saint-Aunès (Hérault) qui aide le grand public à secourir les oiseaux et animaux sauvages en détresse, avec une application gratuite."
    faq = [
        ("Qu'est-ce que l'association Coup de Patte ?",
         "Une association loi 1901 basée à Saint-Aunès, dans l'Hérault, qui aide le grand public à secourir les animaux sauvages trouvés en détresse en ville, en particulier les oiseaux. Elle édite l'application gratuite coupdepatte.eu."),
        ("Coup de Patte est-elle un refuge pour chiens et chats ?",
         "Non. D'autres associations portent le nom Coup de Patte et s'occupent d'animaux domestiques ou de NAC. L'association Coup de Patte de Saint-Aunès se consacre à la faune sauvage : oiseaux, hérissons, chauves-souris, et oriente vers les centres de soins de la faune sauvage."),
        ("Coup de Patte soigne-t-elle les animaux ?",
         "Non. Les soins sont l'affaire des centres de soins de la faune sauvage, autorisés pour cela. Coup de Patte informe, guide les bons gestes et met en relation avec le centre le plus proche et des bénévoles."),
        ("L'application est-elle gratuite ?",
         "Oui, entièrement gratuite, sans publicité commerciale ni pistage."),
    ]
    extra = _ld(ctx, "AboutPage", titre, desc, url, faq, [("L'association", url)])
    out = [head(titre + " | Coup de Patte", desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article><nav class="fil"><a href="/">Coup de Patte</a> › L\'association</nav>')
    out.append('<h1>%s</h1>' % esc(titre))
    out.append('<p class="chapo">Chaque saison, beaucoup de personnes trouvent un oisillon au sol, un oiseau blessé, un hérisson en plein jour, et ne savent pas quoi faire. Coup de Patte existe pour que chacune d\'elles fasse le bon geste, au bon moment, et trouve le bon secours.</p>')
    out.append('<h2>Notre mission</h2><p>Coup de Patte est une association loi 1901 basée à Saint-Aunès, dans l\'Hérault. Elle aide le grand public à secourir les animaux sauvages trouvés en détresse en ville, en particulier les oiseaux, en s\'appuyant sur la doctrine de la LPO, de l\'OFB, du Muséum national d\'Histoire naturelle et des centres de soins de la faune sauvage.</p>')
    out.append('<h2>Ce que fait l\'association</h2><ul>'
               '<li>Une <a href="/">application gratuite</a> : diagnostic en 3 questions, bons gestes pas à pas, centre de soins le plus proche.</li>'
               '<li>Des <a href="/centres/">centres de soins de la faune sauvage référencés</a> département par département, avec leurs coordonnées vérifiées.</li>'
               '<li><a href="/especes/">100 fiches espèces</a> pour reconnaître l\'oiseau, son jeune et le bon geste.</li>'
               '<li>Des <a href="/guides/">guides d\'urgence</a> et des <a href="/actualites/">actualités quotidiennes</a> sur la faune sauvage des villes.</li>'
               '<li>Le signalement des oiseaux bagués au Muséum, et un annuaire de <a href="/benevole/">bénévoles</a> et d\'associations de terrain.</li>'
               '</ul>')
    out.append('<h2>À ne pas confondre</h2><p>Plusieurs associations françaises portent le nom Coup de Patte, souvent des refuges pour chiens, chats ou NAC. L\'association Coup de Patte de Saint-Aunès est dédiée à la faune sauvage. Son seul site officiel est coupdepatte.eu.</p>')
    out.append('<h2>Nous aider</h2><p><a href="/benevole/">Deviens bénévole</a>, <a href="/soutenir/">soutiens l\'association</a> ou partage simplement l\'application : chaque personne qui la connaît avant d\'en avoir besoin, c\'est un animal de plus bien secouru.</p>')
    out.append(_faq_html(esc, faq))
    out.append('<h2>Coordonnées</h2><p>Association Coup de Patte, 1 impasse du Parc, 34130 Saint-Aunès. Présidente : Anne Simonot. Téléphone : 06 15 50 77 46. <a href="/#/mentions">Mentions légales</a>.</p>')
    out.append('</article></main>')
    out.append(FOOT)
    return "\n".join(out)


def render_benevole(ctx):
    esc, SITE, head, FOOT = ctx["esc"], ctx["SITE"], ctx["head"], ctx["FOOT"]
    url = SITE + "/benevole/"
    titre = "Bénévolat animaux sauvages : devenir bénévole près de chez toi"
    desc = "Transporter un oiseau blessé vers un centre de soins, accueillir, sensibiliser : deviens bénévole avec Coup de Patte. Inscription gratuite, à partir de 18 ans, partout en France."
    faq = [
        ("Que fait un bénévole Coup de Patte ?",
         "Selon ses disponibilités : transporter un animal trouvé vers le centre de soins le plus proche, aider une personne à faire les bons gestes, relayer les besoins des centres, sensibiliser autour de soi. Les soins restent réservés aux centres autorisés."),
        ("Faut-il des compétences particulières ?",
         "Non. La bonne volonté, une disponibilité ponctuelle et le respect des bons gestes suffisent. L'application Coup de Patte rappelle les consignes à chaque étape."),
        ("Comment s'inscrire ?",
         "Dans l'application Coup de Patte, rubrique Bénévoles : tu crées ton profil, tu choisis ta zone et la façon de te joindre. Tu peux le modifier ou le supprimer à tout moment. L'inscription est réservée aux 18 ans et plus."),
        ("Je représente une association ou un centre de soins, comment être référencé ?",
         "Inscris ta structure dans l'espace associations de l'application. Elle est vérifiée (RNA ou SIREN) avant publication, et tu peux ensuite trouver des bénévoles près de chez toi."),
    ]
    extra = _ld(ctx, "WebPage", titre, desc, url, faq, [("Devenir bénévole", url)])
    out = [head(titre + " | Coup de Patte", desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article><nav class="fil"><a href="/">Coup de Patte</a> › Devenir bénévole</nav>')
    out.append('<h1>%s</h1>' % esc(titre))
    out.append('<p class="chapo">Un oiseau blessé trouvé à 30 kilomètres du centre de soins le plus proche, c\'est souvent un oiseau qui ne sera pas soigné. Les bénévoles font la différence : un trajet, un coup de fil, un conseil.</p>')
    out.append('<h2>Ce que tu peux faire</h2><ul>'
               '<li>Transporter un animal en détresse vers un centre de soins de la faune sauvage.</li>'
               '<li>Aider une personne qui vient de trouver un animal à faire les bons gestes.</li>'
               '<li>Relayer les besoins des centres : matériel, nourriture, familles d\'accueil autorisées, collectes.</li>'
               '<li>Sensibiliser : école, quartier, réseaux sociaux.</li></ul>')
    out.append('<p><a class="btn" href="/#/benevoles">M\'inscrire comme bénévole</a></p>')
    out.append('<h2>Associations et centres de soins</h2><p>Tu représentes une structure qui agit pour la faune sauvage ? <a href="/#/assos">Inscris-la dans l\'espace associations</a> pour être visible et trouver des bénévoles près de chez toi.</p>')
    out.append(_faq_html(esc, faq))
    out.append('<p><a href="/association/">Découvrir l\'association Coup de Patte</a> · <a href="/soutenir/">Soutenir l\'association</a></p>')
    out.append('</article></main>')
    out.append(FOOT)
    return "\n".join(out)


def render_soutenir(ctx):
    esc, SITE, head, FOOT = ctx["esc"], ctx["SITE"], ctx["head"], ctx["FOOT"]
    url = SITE + "/soutenir/"
    titre = "Soutenir l'association Coup de Patte"
    desc = "Partager l'application, devenir bénévole, parrainer, relayer : toutes les façons d'aider Coup de Patte à secourir plus d'oiseaux et d'animaux sauvages en France."
    extra = _ld(ctx, "WebPage", titre, desc, url, None, [("Soutenir", url)])
    out = [head(titre + " | Coup de Patte", desc, url, SITE + "/og-accueil.png", extra)]
    out.append('<main><article><nav class="fil"><a href="/">Coup de Patte</a> › Soutenir</nav>')
    out.append('<h1>%s</h1>' % esc(titre))
    out.append('<p class="chapo">L\'application est gratuite et le restera. Pour qu\'elle soit connue de tous avant le jour où un animal en a besoin, l\'association compte sur toi.</p>')
    out.append('<h2>Partager l\'application</h2><p>C\'est le geste le plus utile : envoie <a href="/">coupdepatte.eu</a> à tes proches, ton école, ton quartier, ton association. Sur téléphone, elle s\'installe comme une application depuis le navigateur et fonctionne même sans réseau.</p>')
    out.append('<h2>Donner de ton temps</h2><p><a href="/benevole/">Deviens bénévole</a> : transport vers un centre de soins, aide aux personnes qui trouvent un animal, sensibilisation.</p>')
    out.append('<h2>Signaler et améliorer</h2><p>Un centre de soins a changé de numéro ? Une information te semble inexacte ? Signale-le depuis l\'application : chaque correction sauve du temps le jour d\'une urgence.</p>')
    out.append('<h2>Parrainer ou proposer un partenariat</h2><p>Entreprises et collectivités engagées pour la biodiversité : l\'association propose un parrainage éthique, sans cookie ni pistage, et des partenariats de sensibilisation. Contacte l\'association au 06 15 50 77 46.</p>')
    out.append('<h2>Soutenir les centres de soins</h2><p>Les centres de soins de la faune sauvage vivent largement de dons et de bénévolat. Retrouve celui de ton département sur la <a href="/centres/">liste des centres de soins</a> et aide-le directement.</p>')
    out.append('<p><a href="/association/">Découvrir l\'association Coup de Patte</a></p>')
    out.append('</article></main>')
    out.append(FOOT)
    return "\n".join(out)


def build(ctx):
    """Ecrit les pages et renvoie la liste [(url, titre, description)] pour le sitemap et llms.txt."""
    root, write, SITE = ctx["ROOT"], ctx["write"], ctx["SITE"]
    import os
    pages = []
    for g in GUIDES:
        write(os.path.join(root, "guides", g["slug"], "index.html"), render_guide(g, ctx))
        pages.append(("%s/guides/%s/" % (SITE, g["slug"]), g["titre"], g["desc"]))
    write(os.path.join(root, "guides", "index.html"), render_guides_index(ctx))
    pages.insert(0, (SITE + "/guides/", "Guides d'urgence", "Oiseau blessé, oiseau par terre qui ne s'envole pas, oisillon tombé du nid, martinet au sol, oiseau bagué : les gestes qui sauvent."))
    write(os.path.join(root, "association", "index.html"), render_association(ctx))
    pages.append((SITE + "/association/", "L'association Coup de Patte", "Association loi 1901 de Saint-Aunès (Hérault) dédiée au secours de la faune sauvage, éditrice de l'application gratuite coupdepatte.eu. À ne pas confondre avec les refuges homonymes."))
    write(os.path.join(root, "benevole", "index.html"), render_benevole(ctx))
    pages.append((SITE + "/benevole/", "Bénévolat animaux sauvages", "Transport vers les centres de soins, aide aux personnes qui trouvent un animal, sensibilisation. Inscription gratuite dès 18 ans."))
    write(os.path.join(root, "soutenir", "index.html"), render_soutenir(ctx))
    pages.append((SITE + "/soutenir/", "Soutenir l'association Coup de Patte", "Partager l'application, devenir bénévole, parrainer, soutenir les centres de soins."))
    return pages
