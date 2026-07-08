# Coup d'Aile, application (Lot 1)

PWA installable et hors-ligne qui guide une personne ayant trouvé un oiseau ou un oisillon. Lot 1 couvre le coeur vital: écran d'accueil, parcours d'urgence (arbre de décision fondé sur la LPO), gestes à faire et à éviter, contact de secours, conseils de base, et réglages d'accessibilité (thème clair, sombre, automatique, police dyslexie, confort visuel).

## Contenu du dossier
- `index.html` : l'application, autonome.
- `manifest.webmanifest` : manifeste PWA (installation, icône, couleurs).
- `sw.js` : service worker (mise en cache hors-ligne du coeur vital).
- `icons/` : icônes de l'application.

## Tester en local
Ouvrir `index.html` dans un navigateur suffit pour l'aperçu. Pour tester l'installation et le hors-ligne, servir le dossier en local, par exemple:

```
npx serve coup-daile-app
```

puis ouvrir l'adresse indiquée, et sur mobile utiliser « Ajouter à l'écran d'accueil ».

## Déployer gratuitement sur Vercel
Deux options, à coût zéro:
1. Pousser ce dossier sur le dépôt GitHub, puis l'importer dans Vercel (déploiement automatique à chaque push).
2. Ou déposer le dossier directement dans Vercel.

Le sous-domaine cible est `coupdaile.vercel.app`.

## Sources du contenu de soin
Les consignes s'appuient sur la doctrine de la LPO (Ligue pour la Protection des Oiseaux) et de l'OFB (Office Français de la Biodiversité). Numéro national LPO indiqué dans l'app: 05 46 82 12 34, à revérifier avant mise en ligne publique.

## À venir (lots suivants)
Annuaire géolocalisé des centres, identification par photo, comptes et carnet, badges, bénévolat et associations, rappels météo, lieux d'observation, journal éditorial, multilingue. Voir le cahier des charges `App-Oiseaux_Prompt-Maitre_v1.md`.
