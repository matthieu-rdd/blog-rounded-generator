# 🤖 Guide de Génération d'Articles

## 🎯 Script Principal : `generate_article.py`

Ce script génère des articles de blog avec :
- ✅ **Vérification des sujets existants** sur callrounded.com/blog
- ✅ **Recherche web** via Perplexity pour les sources
- ✅ **Rédaction** avec OpenAI selon le style Rounded
- ✅ **Validation** avant publication
- ✅ **Publication** en PRODUCTION dans Sanity

## ⚙️ Configuration

### 1. Clés API dans `.env`

Ajoutez vos clés API dans le fichier `.env` :

```env
OPENAI_API_KEY=sk-...

PERPLEXITY_API_KEY=pplx-...

SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_TOKEN=votre_token_sanity
```

## 🚀 Utilisation

### Générer un article

```bash
python3 generate_article.py "Pourquoi les secrétaires médicales ont besoin d'un agent vocal IA"
```

Ou en mode interactif :

```bash
python3 generate_article.py
# Le script vous demandera le sujet
```

## 📋 Workflow

1. **Vérification des sujets existants**
   - Scrape callrounded.com/blog
   - Compare avec le nouveau sujet
   - Avertit si similaire (vous pouvez continuer ou annuler)

2. **Recherche web via Perplexity**
   - Collecte des données récentes
   - Statistiques, études de cas, tendances 2025

3. **Génération avec OpenAI**
   - Style Rounded (professionnel, accessible)
   - Structure avec points numérotés
   - Mention naturelle de Donna si pertinent

4. **Optimisation SEO**
   - Titre optimisé
   - Meta description
   - Conversion Markdown → HTML
   - Slug URL-friendly

5. **Sauvegarde pour review**
   - Fichier dans `articles_to_review/`
   - Format : `YYYYMMDD_HHMMSS_slug.md`

6. **Validation**
   - Résumé affiché
   - Vous lisez l'article complet
   - Vous validez ou annulez

7. **Publication**
   - Si validé → Publication en PRODUCTION
   - Visible immédiatement dans Sanity Studio

## 🎨 Style des Articles

Le script génère des articles dans le style Rounded :

- **Structure** : Points numérotés (1., 2., 3., etc.)
- **Ton** : Professionnel mais accessible, humain
- **Contenu** : Exemples concrets, situations réelles
- **Mention Donna** : Naturelle et subtile (surtout en conclusion)
- **Liens** : Vers https://callrounded.com/cas-usage/secretariat-medical

## ⚠️ Vérification des Doublons

Le script vérifie automatiquement les sujets existants. Si un sujet similaire est trouvé :
- ⚠️ Un avertissement s'affiche
- Vous pouvez continuer ou annuler
- Permet d'éviter les doublons

## 📁 Fichiers Générés

Les articles sont sauvegardés dans `articles_to_review/` avec :
- Titre et métadonnées
- Résumé SEO
- Mots-clés
- Contenu HTML (pour Sanity)
- Contenu Markdown original

## 💡 Exemples de Sujets

Bons sujets pour le blog Rounded :
- "Comment réduire les appels manqués dans un cabinet médical"
- "Agent vocal IA vs télésecrétariat : lequel choisir ?"
- "Pourquoi les patients continuent d'appeler malgré les agendas en ligne"
- "Les 5 erreurs à éviter avec un agent vocal médical"
- "Comment améliorer l'expérience patient avec l'IA vocale"

## ✅ Conseils

1. **Sujets spécifiques** : Plus le sujet est précis, meilleur sera l'article
2. **Check doublons** : Le script vérifie, mais vérifiez aussi manuellement
3. **Review obligatoire** : Toujours lire l'article avant publication
4. **Style cohérent** : Le script adapte le style, mais vérifiez la cohérence

