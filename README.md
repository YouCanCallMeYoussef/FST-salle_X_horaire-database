# Salles FST

Site statique (une seule page) qui affiche, à partir des emplois du temps publiés par la Faculté des Sciences de Tunis :

- les **salles libres** pour un jour et un créneau donnés (filtres par bloc / type de salle, recherche, bouton « Maintenant ») ;
- l'**emploi du temps de chaque groupe** ;
- le **tableau complet** des séances ;
- les **conflits de salle** : deux groupes différents placés dans la même salle sur des créneaux qui se chevauchent.

Données actuelles : S1, A.U. 2026-2027 uniquement — Licence 1–3, Ingénieur, Cycle préparatoire (BG1-A, BG2, PC1-A, PC2-A/B, MPI1 A–E, MI2 A/B/C, PI2 A/B).

## Structure

```
index.html                         page générée (ne pas éditer à la main)
data/sessions-S1-2026-2027.json    toutes les séances (une ligne = une séance)
tools/template.html                gabarit de la page (HTML/CSS/JS)
tools/build.py                     génère index.html depuis le gabarit + les données
tools/extract_et_pdf.py            extraction des PDF « ET-*.pdf » (Licence / Ingénieur, générés par Index Éducation)
tools/prepa_landscape.py           horaires des PDF prépa intégrée (MPI, MI, PI — format paysage Excel)
tools/prepa_portrait.py            horaires des PDF prépa (BG, PC — format portrait Excel)
```

Format d'une séance :

```json
{"group":"Prépa intégré MI2-A","cycle":"Cycle Préparatoire","day":"Lundi",
 "start":"08:15","end":"09:45","room":"SE2A","subject":"Traitement de signal",
 "teacher":"Hanene Bouhadda","type":""}
```

`room` peut contenir plusieurs salles séparées par des virgules, ou être vide si la salle n'est pas précisée.

## Mettre à jour

```bash
# après avoir modifié data/*.json ou tools/template.html
python3 tools/build.py
git add -A && git commit -m "Mise à jour des emplois du temps" && git push
```

Pour un nouveau semestre : `python3 tools/extract_et_pdf.py ET-XXX.pdf > raw.json` pour les PDF Licence/Ingénieur (nécessite `pip install pdfplumber`). Les scripts prépa donnent les jours/horaires par géométrie ; les intitulés des cases en diagonale (demi-groupes) sont à vérifier à la main.

## Publier avec GitHub Pages

1. Pousser ce dossier à la racine d'un dépôt GitHub (branche `main`).
2. *Settings → Pages → Build and deployment* : **Deploy from a branch**, branche `main`, dossier `/ (root)`.
3. Domaine personnalisé : dans *Settings → Pages → Custom domain*, saisir le sous-domaine (ex. `salles.securinetsfst.org`) — GitHub crée le fichier `CNAME`. Chez le registrar/DNS, ajouter un enregistrement **CNAME** `salles` → `<utilisateur-ou-org>.github.io`. Puis cocher **Enforce HTTPS** une fois le certificat émis.

## Limites

- « Libre » = aucune séance de ces emplois du temps dans la salle : examens, réservations et autres départements ne sont pas couverts.
- Cycle préparatoire : la salle indiquée est celle de la section ; les TP (physique, chimie, biologie, géologie, programmation) ont lieu en laboratoire non précisé et ne bloquent pas la salle.
- Les salles `S.1`, `S.7`, `S.8` du cycle Ingénieur Chimie (ICAI) sont renommées `S.x (Ing. Chimie)` : ce sont a priori des salles distinctes de celles des licences portant le même nom. Les autres conflits restants sont à confirmer auprès de la scolarité.

Source : emplois du temps publiés sur fst.rnu.tn. Projet SecuriNets FST.
