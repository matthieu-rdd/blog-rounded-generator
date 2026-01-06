# Guide de Déploiement Streamlit Cloud - Étape par Étape

## ✅ Checklist avant déploiement

- [ ] Code poussé sur GitHub
- [ ] Tous les fichiers nécessaires sont dans le repo
- [ ] `requirements.txt` est à jour
- [ ] `app.py` est le fichier principal
- [ ] Les fichiers `data/*.json` sont présents

## 🚀 Déploiement

### 1. Accéder à Streamlit Cloud

Allez sur : **https://share.streamlit.io/**

### 2. Se connecter

- Cliquez sur "Sign in"
- Autorisez l'accès à votre compte GitHub
- Sélectionnez le compte qui a accès au repository `matthieu-rdd/blog-rounded-generator`

### 3. Créer une nouvelle app

- Cliquez sur **"New app"**
- **Repository :** Sélectionnez `matthieu-rdd/blog-rounded-generator`
- **Branch :** `main`
- **Main file path :** `app.py`
- Cliquez sur **"Deploy"**

### 4. Configurer les Secrets (IMPORTANT)

Une fois l'app créée :

1. Cliquez sur **"Settings"** (⚙️ en haut à droite)
2. Allez dans l'onglet **"Secrets"**
3. Ajoutez ces variables :

```toml
OPENAI_API_KEY = "sk-..."
PERPLEXITY_API_KEY = "pplx-..."
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "development"
SANITY_TOKEN = "..."
```

4. Cliquez sur **"Save"**

### 5. Redémarrer l'app

- Retournez au dashboard
- Cliquez sur **"Manage app"**
- Cliquez sur **"⋮"** (menu) → **"Restart app"**

## 🔍 Vérification

Votre app devrait être accessible sur :
`https://[nom-de-votre-app].streamlit.app`

## ❌ Problèmes courants

### Erreur : "Module not found"

**Cause :** Fichiers manquants dans le repository

**Solution :**
```bash
# Vérifier que tous les fichiers sont commités
git add scripts/ utils/ data/
git commit -m "Add required files"
git push
```

### Erreur : "API Key not found"

**Cause :** Secrets non configurés dans Streamlit Cloud

**Solution :** Allez dans Settings → Secrets et ajoutez toutes les clés API

### Erreur : "File not found: data/articles_existants.json"

**Cause :** Les fichiers JSON ne sont pas dans le repository

**Solution :**
```bash
git add data/
git commit -m "Add data files"
git push
```

### L'app se charge mais affiche une erreur

**Solution :** 
1. Allez dans "Manage app" → "Logs"
2. Regardez les erreurs dans les logs
3. Vérifiez que tous les secrets sont configurés

## 📝 Structure requise

Votre repository doit contenir :

```
blog-rounded-generator/
├── app.py                    ✅ Fichier principal
├── requirements.txt          ✅ Dépendances
├── .streamlit/
│   └── config.toml          ✅ Configuration
├── scripts/
│   └── generate_article.py  ✅ Script de génération
├── utils/
│   └── sanity_utils.py      ✅ Utilitaires
└── data/
    ├── articles_existants.json ✅ Base de données
    └── keywords.json         ✅ Mots-clés
```

## 🆘 Besoin d'aide ?

Si vous avez une erreur spécifique, partagez :
1. Le message d'erreur exact
2. Les logs de Streamlit Cloud (Manage app → Logs)
3. Une capture d'écran si possible

