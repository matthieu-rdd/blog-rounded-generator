# ✅ Solution avec Validation (GRATUITE)

## 🎯 Fonctionnalités

Cette solution vous permet de :

1. ✅ **Générer un article complet** (recherche web + AI + style + SEO)
2. ✅ **Recevoir l'article** sauvegardé dans un fichier local
3. ✅ **Lire l'article complet** avant validation
4. ✅ **Valider ou annuler** avant publication
5. ✅ **Publier en PRODUCTION** si validé (visible immédiatement dans Sanity)

## 🚀 Utilisation

```bash
python3 workflow_validation.py "Sujet de votre article"
```

Ou en mode interactif :

```bash
python3 workflow_validation.py
# Le script vous demandera le sujet
```

## 📋 Déroulement

1. **Génération** : Le script génère l'article complet
2. **Sauvegarde** : L'article est sauvegardé dans `articles_to_review/` avec toutes les infos
3. **Affichage** : Un résumé s'affiche dans le terminal
4. **Review** : Vous pouvez ouvrir le fichier `.md` pour lire l'article complet
5. **Validation** : Vous tapez `o` pour publier ou `n` pour annuler
6. **Publication** : Si validé, l'article est publié en PRODUCTION

## 💾 Fichiers sauvegardés

Les articles sont sauvegardés dans `articles_to_review/` avec le format :

```
YYYYMMDD_HHMMSS_slug.md
```

Chaque fichier contient :
- Titre et métadonnées
- Résumé SEO
- Mots-clés
- Contenu HTML complet
- Contenu Markdown original

## ⚙️ Configuration

Assurez-vous d'avoir un fichier `.env` avec :

```env
OPENAI_API_KEY=votre_cle
PERPLEXITY_API_KEY=votre_cle
SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_TOKEN=votre_token
```

## ✅ Avantages

- ✅ **100% Gratuit** : Utilise des fichiers locaux, pas besoin de Google Docs
- ✅ **Simple** : Un seul script
- ✅ **Complet** : Vous avez tout le contenu dans un fichier
- ✅ **Sûr** : Validation avant publication
- ✅ **Visible** : Publication directe en production (visible dans dashboard)

## 📁 Structure des fichiers

```
articles_to_review/
  ├── 20250115_143022_mon-article.md
  ├── 20250115_150145_autre-article.md
  └── ...
```

## 💡 Astuce

Pour ouvrir rapidement un article :

```bash
# Sur Mac
open articles_to_review/NOM_DU_FICHIER.md

# Sur Linux
xdg-open articles_to_review/NOM_DU_FICHIER.md
```

Ou utilisez votre éditeur préféré (VS Code, Sublime, etc.)

