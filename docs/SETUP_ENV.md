# ⚙️ Configuration du fichier .env

## Créer le fichier .env

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Perplexity API
PERPLEXITY_API_KEY=pplx-...

# Google Gemini API (optionnel, pour les images)
GOOGLE_GEMINI_API_KEY=

# Sanity Configuration
SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_TOKEN=votre_token_sanity_ici

# Site Revalidation (optionnel)
REVALIDATE_URL=https://www.lamignonnecouverture.fr/api/revalidate
```

## Commandes

```bash
# Copier depuis env.example et modifier
cp env.example .env

# Ou créer directement
cat > .env << 'EOF'
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_TOKEN=votre_token_sanity_ici
EOF
```

⚠️ **Important** : Ajoutez votre `SANITY_TOKEN` dans le fichier `.env` pour pouvoir publier les articles.

