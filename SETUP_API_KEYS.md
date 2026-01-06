# Configuration des Clés API

Ce document liste toutes les clés API nécessaires pour faire fonctionner l'application.

## Clés API Requises

### 1. OpenAI API Key
- **Variable d'environnement :** `OPENAI_API_KEY`
- **Format :** `sk-...`
- **Usage :** Génération d'articles avec GPT-4o-mini
- **Où l'obtenir :** https://platform.openai.com/api-keys
- **Coût :** Payant (facturé à l'usage)

### 2. Perplexity API Key
- **Variable d'environnement :** `PERPLEXITY_API_KEY`
- **Format :** `pplx-...`
- **Usage :** Recherche web pour enrichir les articles
- **Où l'obtenir :** https://www.perplexity.ai/settings/api
- **Coût :** Payant (facturé à l'usage)

### 3. Sanity Configuration
- **Variables d'environnement :**
  - `SANITY_PROJECT_ID` : ID du projet Sanity (ex: `8y6orojx`)
  - `SANITY_DATASET` : Dataset à utiliser (`development` ou `production`)
  - `SANITY_TOKEN` : Token d'accès Sanity avec permissions d'écriture
- **Où les obtenir :** 
  - Project ID : Dans votre dashboard Sanity
  - Token : https://www.sanity.io/manage (Settings > API > Tokens)
- **Permissions requises :** `Editor` ou `Administrator`

### 4. Google Gemini API Key (Optionnel)
- **Variable d'environnement :** `GOOGLE_GEMINI_API_KEY`
- **Usage :** Alternative à OpenAI (non utilisé actuellement)
- **Où l'obtenir :** https://makersuite.google.com/app/apikey

### 5. Revalidation URL (Optionnel)
- **Variable d'environnement :** `REVALIDATE_URL`
- **Usage :** URL pour revalider le cache Next.js après publication
- **Format :** `https://votre-site.com/api/revalidate`

## Configuration pour Streamlit Cloud

Pour déployer sur Streamlit Cloud, ajoutez ces variables dans les **Secrets** de votre app :

1. Allez sur https://share.streamlit.io/
2. Sélectionnez votre app
3. Cliquez sur "Settings" → "Secrets"
4. Ajoutez les variables suivantes :

```toml
OPENAI_API_KEY = "sk-..."
PERPLEXITY_API_KEY = "pplx-..."
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "development"
SANITY_TOKEN = "..."
REVALIDATE_URL = "https://..." # Optionnel
```

## Configuration Locale

Pour le développement local, créez un fichier `.env` à la racine du projet :

```bash
cp env.example .env
```

Puis éditez `.env` avec vos clés API.

## Sécurité

⚠️ **IMPORTANT :**
- Ne jamais commiter le fichier `.env` dans Git
- Ne jamais partager vos clés API publiquement
- Utilisez des tokens avec les permissions minimales nécessaires
- Régénérez vos tokens si vous pensez qu'ils ont été compromis

## Coûts Estimés

- **OpenAI GPT-4o-mini :** ~$0.15-0.30 par article (génération FR + EN)
- **Perplexity :** ~$0.01-0.05 par recherche web
- **Total par article :** ~$0.20-0.35

## Support

En cas de problème avec les clés API :
1. Vérifiez que les variables d'environnement sont correctement configurées
2. Vérifiez que les tokens ont les bonnes permissions
3. Vérifiez les quotas et limites de votre compte API

