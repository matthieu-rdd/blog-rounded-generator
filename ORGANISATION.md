# 📁 Organisation du Projet

## Structure des Dossiers

```
.
├── 📄 README.md              Documentation principale
├── 📄 requirements.txt       Dépendances Python
├── 📄 env.example            Exemple de configuration
├── 📄 .gitignore             Fichiers ignorés par Git
│
├── 📂 scripts/               Scripts Python principaux
│   ├── generate_article.py   ⭐ Génération d'articles (PRINCIPAL)
│   ├── publish_from_file.py  📤 Publication depuis fichier
│   ├── workflow_validation.py Validation d'articles
│   └── archive/              Scripts obsolètes
│       └── automate_blog_post.py
│
├── 📂 utils/                 Utilitaires
│   ├── __init__.py
│   └── sanity_utils.py       Conversion Block Content Sanity
│
├── 📂 articles/              Articles générés (pour review)
│   └── *.md                  Fichiers Markdown avec métadonnées
│
├── 📂 data/                  Données et configurations
│   └── articles_existants.json Base de connaissances (anti-doublons)
│
└── 📂 docs/                  Documentation
    ├── CHAMPS_SANITY.md      Champs Sanity remplis
    ├── SETUP_ENV.md          Configuration des variables d'environnement
    ├── GUIDE_GENERATION.md   Guide de génération
    ├── CONFIGURATION_N8N.md  Configuration n8n
    └── ...
```

## 🚀 Utilisation

### Générer un article
```bash
python3 scripts/generate_article.py
```

### Publier un article
```bash
python3 scripts/publish_from_file.py articles/nom-fichier.md
```

## 📝 Notes

- Les scripts sont dans `scripts/` pour une organisation claire
- Les articles générés sont dans `articles/` pour review
- La documentation est dans `docs/` pour consultation facile
- Les données sont dans `data/` séparées du code
