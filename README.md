# 🤖 Automatisation de Publication de Blog Rounded

Système automatisé pour générer et publier des articles de blog sur Sanity.io avec support multilingue (FR/EN).

## 🚀 Démarrage rapide

### Installation

```bash
pip install -r requirements.txt
cp env.example .env
# Éditez .env avec vos clés API
```

### Génération d'un article

```bash
python3 scripts/generate_article.py
```

### Publication d'un article

```bash
python3 scripts/publish_from_file.py articles/nom-du-fichier.md
```

## 📁 Structure du Projet

```
.
├── scripts/
│   ├── generate_article.py     ⭐ Script principal (RECOMMANDÉ)
│   └── publish_from_file.py    📤 Publier un article depuis un fichier
├── utils/
│   └── sanity_utils.py         🔧 Utilitaires Sanity (conversion Block Content)
├── articles/                   📁 Articles générés (pour review avant publication)
├── data/
│   └── articles_existants.json 📊 Base de connaissances des articles (anti-doublons)
├── docs/                       📚 Documentation
│   ├── README.md               Documentation principale
│   ├── CHAMPS_SANITY.md        Champs Sanity remplis
│   ├── SETUP_ENV.md            Configuration des variables d'environnement
│   ├── GUIDE_GENERATION.md     Guide de génération d'articles
│   └── CONFIGURATION_N8N.md    Configuration pour n8n
├── .env                        Variables d'environnement (non versionné)
├── env.example                 Exemple de configuration
├── requirements.txt            Dépendances Python
└── README.md                   Ce fichier
```

## ✨ Fonctionnalités

### Génération d'articles
- ✅ Recherche web avec Perplexity
- ✅ Génération avec OpenAI (style Rounded)
- ✅ Vérification des doublons (scrape callrounded.com/blog)
- ✅ Génération bilingue (FR + EN) avec même Translation Group
- ✅ SEO optimisé (meta titles, descriptions, OG tags)
- ✅ Conversion automatique en format Sanity Block Content

### Publication
- ✅ Format Block Content avec titres (H2, H3), paragraphes, listes
- ✅ Gestion du gras (**texte** → strong)
- ✅ Liens markdown [texte](url) → liens cliquables
- ✅ Support multilingue avec slugs adaptés (FR + EN avec `-en`)
- ✅ Révalidation automatique Next.js

## 🎨 Style des Articles

Les articles générés suivent le style Rounded :
- **Structure** : Titres numérotés (1., 2., 3., etc.) en H2
- **Sous-titres** : H3 pour les sous-sections
- **Ton** : Professionnel mais accessible, humain
- **Contenu** : Exemples concrets, situations réelles
- **Mention Donna** : Naturelle et subtile (surtout en conclusion)
- **Liens** : Vers https://callrounded.com/cas-usage/secretariat-medical
- **Longueur** : Minimum 1200 mots

## 📝 Utilisation

### 1. Générer un article

```bash
python3 scripts/generate_article.py
```

Le script va :
1. Demander le sujet de l'article
2. Vérifier s'il existe déjà
3. Rechercher des sources web
4. Générer l'article (FR + EN)
5. Sauvegarder dans `articles/` pour review

### 2. Publier un article

```bash
python3 scripts/publish_from_file.py articles/20251211_140618_mon-article.md
```

Ou sans argument (utilise le dernier article généré) :
```bash
python3 scripts/publish_from_file.py
```

## 🔧 Configuration

Voir `docs/SETUP_ENV.md` pour configurer les variables d'environnement nécessaires :
- `OPENAI_API_KEY` : Clé API OpenAI
- `PERPLEXITY_API_KEY` : Clé API Perplexity
- `SANITY_TOKEN` : Token Sanity
- `SANITY_PROJECT_ID` : ID du projet Sanity
- `SANITY_DATASET` : Dataset (production/development)
- `REVALIDATE_URL` : URL de revalidation Next.js (optionnel)

## 📚 Documentation

- **GUIDE_GENERATION.md** : Guide détaillé pour générer des articles
- **CHAMPS_SANITY.md** : Liste complète des champs Sanity remplis
- **SETUP_ENV.md** : Configuration des variables d'environnement
- **CONFIGURATION_N8N.md** : Référence pour configurer n8n

## 🎯 Workflow Recommandé

1. **Génération** : `python3 scripts/generate_article.py`
2. **Review** : Vérifier le fichier dans `articles/`
3. **Publication** : `python3 scripts/publish_from_file.py articles/nom-fichier.md`
4. **Vérification** : Vérifier sur le site que tout s'affiche correctement

## 🔍 Vérification des Doublons

Le script vérifie automatiquement :
- Scrape `callrounded.com/blog` pour les sujets existants
- Compare avec la base de connaissances locale (`data/articles_existants.json`)
- Avertit si un sujet similaire existe

## 🌍 Support Multilingue

Chaque article est généré en deux versions :
- **FR** : Version française avec slug standard
- **EN** : Version anglaise avec slug `-en`
- **Translation Group** : Les deux versions partagent le même ID pour être liées dans Sanity

## 📦 Format des Articles Générés

Les articles sont sauvegardés dans `articles/` au format :
```
YYYYMMDD_HHMMSS_slug.md
```

Chaque fichier contient :
- Métadonnées Sanity (FR + EN)
- Contenu complet (FR + EN)
- Format Block Content prêt pour Sanity
