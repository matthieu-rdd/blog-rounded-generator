# Résumé du Déploiement - Blog Rounded Generator

## 📦 Repository GitHub
**URL :** https://github.com/matthieu-rdd/blog-rounded-generator

## 🚀 Déploiement sur Streamlit Cloud

### Étape 1 : Accéder à Streamlit Cloud
1. Aller sur https://share.streamlit.io/
2. Se connecter avec votre compte GitHub
3. Autoriser l'accès au repository `blog-rounded-generator`

### Étape 2 : Créer une nouvelle app
1. Cliquer sur "New app"
2. **Repository :** `matthieu-rdd/blog-rounded-generator`
3. **Branch :** `main`
4. **Main file :** `app.py`
5. Cliquer sur "Deploy"

### Étape 3 : Configurer les Secrets (Variables d'environnement)

Dans les paramètres de l'app (Settings → Secrets), ajouter :

```toml
OPENAI_API_KEY = "sk-..."
PERPLEXITY_API_KEY = "pplx-..."
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "development"
SANITY_TOKEN = "..."
REVALIDATE_URL = "https://..." # Optionnel
```

**Voir le fichier `SETUP_API_KEYS.md` pour plus de détails sur chaque clé.**

### Étape 4 : Redémarrer l'app
Après avoir ajouté les secrets, redémarrer l'application depuis le dashboard Streamlit Cloud.

## 🔐 Authentification

L'application est protégée par authentification :
- **Nom d'utilisateur :** `rounded`
- **Mot de passe :** `Rounded18!`

## 📋 Fonctionnalités

- ✅ Génération d'articles de blog avec IA
- ✅ 3 variantes de sujets proposées
- ✅ Édition du contenu avant publication
- ✅ Publication automatique sur Sanity (FR + EN)
- ✅ Historique des articles générés
- ✅ Recherche et suppression d'articles
- ✅ Optimisation SEO automatique

## 🔧 Structure du Projet

```
blog-rounded-generator/
├── app.py                    # Application Streamlit principale
├── requirements.txt          # Dépendances Python
├── .streamlit/
│   └── config.toml          # Configuration Streamlit
├── scripts/
│   └── generate_article.py  # Script de génération d'articles
├── utils/
│   └── sanity_utils.py      # Utilitaires Sanity
├── data/
│   ├── articles_existants.json
│   └── keywords.json
└── articles/                # Articles générés (créé dynamiquement)
```

## 📝 Clés API Utilisées

### 1. OpenAI API
- **Usage :** Génération de contenu d'articles
- **Modèle :** GPT-4o-mini
- **Coût :** ~$0.15-0.30 par article

### 2. Perplexity API
- **Usage :** Recherche web pour enrichir les articles
- **Modèle :** sonar-pro
- **Coût :** ~$0.01-0.05 par recherche

### 3. Sanity CMS
- **Usage :** Publication des articles
- **Project ID :** 8y6orojx
- **Dataset :** development (ou production)

## 🌐 URL de l'Application

Une fois déployée, l'application sera accessible sur :
`https://[nom-de-votre-app].streamlit.app`

## 📚 Documentation

- `SETUP_API_KEYS.md` : Guide détaillé des clés API
- `README_DEPLOY.md` : Guide de déploiement
- `DEPLOYMENT.md` : Documentation complète

## ⚠️ Notes Importantes

1. **Sécurité :** Ne jamais commiter les clés API dans le code
2. **Coûts :** Surveiller l'utilisation des APIs pour éviter les surprises
3. **Sanity :** Vérifier que le token a les permissions d'écriture
4. **Articles :** Les articles sont sauvegardés localement dans `articles/`

## 🆘 Support

En cas de problème :
1. Vérifier les logs dans Streamlit Cloud
2. Vérifier que toutes les clés API sont correctement configurées
3. Vérifier les permissions du token Sanity

