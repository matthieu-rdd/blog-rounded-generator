# 🤖 Générateur d'Articles de Blog - Rounded

Système automatisé pour générer des articles de blog avec vérification des sujets existants, recherche web via Perplexity, et génération avec OpenAI.

## 🎯 Script Principal : `generate_article.py` ⭐

**Solution complète avec validation :**

1. ✅ Vérifie les sujets existants sur callrounded.com/blog
2. ✅ Recherche web via Perplexity pour les sources
3. ✅ Génère l'article avec OpenAI (style Rounded)
4. ✅ Sauvegarde dans `articles_to_review/` pour review
5. ✅ Demande validation avant publication
6. ✅ Publie en PRODUCTION dans Sanity si validé

### 🚀 Utilisation

```bash
python3 generate_article.py "Pourquoi les secrétaires médicales ont besoin d'un agent vocal IA"
```

Ou en mode interactif :

```bash
python3 generate_article.py
# Le script vous demandera le sujet
```

## ⚙️ Configuration

### Fichier `.env`

Le fichier `.env` a été créé avec vos clés API. Ajoutez votre `SANITY_TOKEN` :

```env
SANITY_TOKEN=votre_token_sanity
```

### Variables d'environnement

- `OPENAI_API_KEY` : Clé API OpenAI ✅ (configurée)
- `PERPLEXITY_API_KEY` : Clé API Perplexity ✅ (configurée)
- `SANITY_PROJECT_ID` : ID du projet Sanity (défaut: 8y6orojx)
- `SANITY_DATASET` : Dataset Sanity (défaut: development)
- `SANITY_TOKEN` : Token d'authentification Sanity ⚠️ (à ajouter)

## 📋 Scripts Disponibles

### 1. `generate_article.py` ⭐ **RECOMMANDÉ**

**Solution complète avec vérification des doublons**

- ✅ Vérifie les sujets existants sur le blog
- ✅ Recherche web via Perplexity
- ✅ Génération avec OpenAI (style Rounded)
- ✅ Validation avant publication
- ✅ Publication en production

### 2. `workflow_validation.py`

**Solution avec validation (sans vérification doublons)**

- Génère l'article complet
- Sauvegarde pour review
- Validation avant publication

### 3. `automate_blog_post.py`

**Solution automatique complète (avec images)**

- Génère l'article complet
- Génère une image
- Publie automatiquement

## 🎨 Style des Articles

Les articles générés suivent le style Rounded :

- **Structure** : Points numérotés (1., 2., 3., etc.)
- **Ton** : Professionnel mais accessible, humain
- **Contenu** : Exemples concrets, situations réelles
- **Mention Donna** : Naturelle et subtile (surtout en conclusion)
- **Liens** : Vers https://callrounded.com/cas-usage/secretariat-medical
- **Longueur** : Minimum 1200 mots

## 📁 Structure du Projet

```
.
├── generate_article.py         ⭐ Script principal (RECOMMANDÉ)
├── workflow_validation.py      Script avec validation
├── automate_blog_post.py       Script automatique complet
├── articles_to_review/         📁 Dossier pour les articles générés
├── .env                        Variables d'environnement (clés API)
├── env.example                 Exemple de configuration
├── requirements.txt            Dépendances Python
├── README.md                   Ce fichier
├── GUIDE_GENERATION.md         Guide détaillé de génération
└── CONFIGURATION_N8N.md        Référence pour n8n
```

## 💾 Articles Générés

Les articles sont sauvegardés dans `articles_to_review/` au format :

```
YYYYMMDD_HHMMSS_slug.md
```

Chaque fichier contient :
- Titre et métadonnées
- Résumé SEO
- Mots-clés
- Contenu HTML (pour Sanity)
- Contenu Markdown original

## 🔍 Fonctionnalités

### Vérification des Doublons

Le script `generate_article.py` :
- Scrape automatiquement callrounded.com/blog
- Compare les sujets existants avec le nouveau
- Avertit si un sujet similaire est trouvé
- Vous permet de continuer ou d'annuler

### Recherche Web

- Utilise Perplexity pour collecter des données récentes
- Statistiques, études de cas, tendances 2025
- Sources spécialisées en santé et IA vocale

### Génération IA

- OpenAI GPT-4o-mini pour la rédaction
- Style adapté aux exemples Rounded
- Structure claire et professionnelle

## 📖 Documentation

- **GUIDE_GENERATION.md** : Guide détaillé avec exemples
- **README_VALIDATION.md** : Documentation du workflow de validation

## ✅ Workflow Recommandé

1. **Générer** : `python3 generate_article.py "Votre sujet"`
2. **Vérifier** : Le script vérifie les doublons automatiquement
3. **Review** : Lire l'article dans `articles_to_review/`
4. **Valider** : Répondre `o` pour publier ou `n` pour annuler
5. **Publier** : L'article est publié en PRODUCTION dans Sanity

## 💡 Exemples de Sujets

Bons sujets pour le blog Rounded :
- "Comment réduire les appels manqués dans un cabinet médical"
- "Agent vocal IA vs télésecrétariat : lequel choisir ?"
- "Pourquoi les patients continuent d'appeler malgré les agendas en ligne"
- "Les 5 erreurs à éviter avec un agent vocal médical"
- "Comment améliorer l'expérience patient avec l'IA vocale"

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Le fichier .env est déjà créé avec vos clés API
# Ajoutez juste votre SANITY_TOKEN dans .env
```

## ⚠️ Notes Importantes

- ✅ Les clés API OpenAI et Perplexity sont configurées
- ⚠️ Ajoutez votre `SANITY_TOKEN` dans `.env` pour publier
- ✅ Le script vérifie automatiquement les doublons
- ✅ Validation toujours demandée avant publication
