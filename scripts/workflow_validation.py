#!/usr/bin/env python3
"""
Solution GRATUITE avec validation :
1. Génère l'article complet
2. Sauvegarde dans un fichier local pour review
3. Affiche un résumé
4. Demande validation
5. Si validé → publie à Sanity en PRODUCTION
"""

import os
import sys
import json
import requests
import uuid
import random
import string
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID", "8y6orojx")
SANITY_DATASET = os.getenv("SANITY_DATASET", "development")
SANITY_TOKEN = os.getenv("SANITY_TOKEN")
SANITY_API_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-12-11"

# Dossier pour sauvegarder les articles
ARTICLES_DIR = Path("articles_to_review")
ARTICLES_DIR.mkdir(exist_ok=True)

# Initialiser OpenAI
openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except:
        pass


def generate_key():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def search_web(query: str) -> str:
    """Recherche web via Perplexity"""
    if not PERPLEXITY_API_KEY:
        return ""
    
    print("🔍 Recherche web...")
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except:
        return ""


def generate_article(topic: str) -> str:
    """Génère l'article avec OpenAI"""
    if not openai_client:
        raise ValueError("OPENAI_API_KEY non configurée dans .env")
    
    print("📝 Génération de l'article...")
    
    current_date = datetime.now()
    year = current_date.year
    readable_date = current_date.strftime("%d/%m/%Y")
    
    web_results = search_web(
        f"Recherche des données récentes, études de cas, chiffres, retours d'expérience 2025 sur {topic}, agents vocaux IA, automatisation des appels, support client"
    )
    
    system_prompt = f"""Tu es un rédacteur professionnel spécialisé dans l'IA vocale et les technologies de téléphonie automatisée.

IMPORTANT: La date actuelle est {readable_date} ({year}). Utilise des expressions comme "en {year}", "cette année", "tendances récentes".

Crée un article de blog complet (minimum 1000 mots) sur le sujet donné. Mentionne Rounded de manière subtile comme référence crédible dans le domaine.

Structure: Introduction percutante, sections avec titres H2/H3, conclusion forte.
Ton: Professionnel, clair, accessible.
Format: Markdown avec titres."""
    
    user_prompt = f"""Sujet: {topic}

Données de recherche:
{web_results[:2000] if web_results else "Aucune donnée"}

Génère un article complet de minimum 1000 mots."""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def apply_style(article: str) -> str:
    """Applique le style Rounded"""
    if not openai_client:
        return article
    
    print("🎨 Application du style éditorial...")
    
    style_prompt = """Tu es un rédacteur drôle, accessible, mais sérieux dans l'info. 
Ton conversatif, décontracté. Commence fort avec un hook, utilise des questions rhétoriques, 
termine chaque section par un "takeaway" drôle ou métaphorique. 
Reste professionnel mais accessible."""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": style_prompt},
            {"role": "user", "content": f"Réécris cet article dans le style ci-dessus:\n\n{article}"}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content


def optimize_seo(article: str) -> Dict[str, Any]:
    """Optimise SEO et retourne les métadonnées"""
    if not openai_client:
        # Fallback simple
        slug = article[:50].lower().replace(' ', '-').replace("'", '').replace(",", '')
        return {
            "title": article.split('\n')[0].replace('#', '').strip()[:60],
            "summary": article[:155],
            "blog_post": article,
            "slug": slug,
            "readTime": "5 min",
            "tag": "actualites-tendances"
        }
    
    print("🔍 Optimisation SEO...")
    
    system_prompt = """You are an expert SEO copywriter. Optimize the article for SEO and return JSON with:
- title: SEO title (max 60 chars)
- summary: Meta description (155-160 chars)
- blog_post: Full HTML content with <h2>, <h3>, <p>, <ul>, <li> tags
- slug: URL-friendly slug
- readTime: Reading time
- tag: Category from: conseils-entretien, renovation-reparation, materiaux-couverture, charpente, isolation-performance-energetique, zinguerie-etancheite, reglementation-normes, climat-environnement, guides-pratiques, actualites-tendances
- keywords: Array of keywords
- focusKeyword: Main keyword"""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)


def save_article_for_review(article_data: Dict[str, Any], topic: str) -> Path:
    """Sauvegarde l'article dans un fichier pour review"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = article_data.get("slug", "article")
    filename = f"{timestamp}_{slug}.md"
    filepath = ARTICLES_DIR / filename
    
    # Contenu à sauvegarder
    content = f"""# {article_data.get('title', 'Article')}

**Slug:** {article_data.get('slug', 'N/A')}  
**Catégorie:** {article_data.get('tag', 'N/A')}  
**Temps de lecture:** {article_data.get('readTime', 'N/A')}  
**Focus Keyword:** {article_data.get('focusKeyword', 'N/A')}  
**Généré le:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}  
**Sujet original:** {topic}

---

## Résumé

{article_data.get('summary', 'N/A')}

---

## Mots-clés

{', '.join(article_data.get('keywords', []))}

---

## Contenu HTML

{article_data.get('blog_post', 'N/A')}

---

## Contenu Markdown (version originale)

{article_data.get('original_content', 'N/A')}
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath


def display_summary(article_data: Dict[str, Any], filepath: Path):
    """Affiche un résumé de l'article"""
    print("\n" + "=" * 70)
    print("📋 ARTICLE GÉNÉRÉ - À VALIDER")
    print("=" * 70)
    print()
    print(f"📌 Titre: {article_data.get('title', 'N/A')}")
    print(f"🔗 Slug: {article_data.get('slug', 'N/A')}")
    print(f"📋 Catégorie: {article_data.get('tag', 'N/A')}")
    print(f"⏱️  Temps de lecture: {article_data.get('readTime', 'N/A')}")
    print(f"🔑 Focus Keyword: {article_data.get('focusKeyword', 'N/A')}")
    print()
    print(f"📝 Résumé:")
    print(f"   {article_data.get('summary', 'N/A')}")
    print()
    print("─" * 70)
    print("PREVIEW DU CONTENU (premiers 800 caractères):")
    print("─" * 70)
    content = article_data.get('blog_post', '')
    # Nettoyer HTML pour preview
    preview = content.replace('<p>', '').replace('</p>', '\n\n')
    preview = preview.replace('<h2>', '\n## ').replace('</h2>', '\n\n')
    preview = preview.replace('<h3>', '\n### ').replace('</h3>', '\n\n')
    preview = preview.replace('<ul>', '').replace('</ul>', '')
    preview = preview.replace('<li>', '• ').replace('</li>', '\n')
    preview = preview.replace('<strong>', '**').replace('</strong>', '**')
    preview = preview[:800] + "..." if len(preview) > 800 else preview
    print(preview)
    print("─" * 70)
    print()
    print(f"💾 Article sauvegardé dans : {filepath}")
    print(f"   Vous pouvez ouvrir ce fichier pour lire l'article complet")
    print()
    print("─" * 70)
    print()


def ask_validation() -> bool:
    """Demande validation à l'utilisateur"""
    print("❓ Voulez-vous publier cet article en PRODUCTION ?")
    print("   - Tapez 'o' pour publier")
    print("   - Tapez 'n' pour annuler")
    print("   - Tapez 'o' puis Entrée pour valider")
    print()
    
    try:
        response = input("   Publier ? (o/n) [n]: ").strip().lower()
        return response == 'o'
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️  Annulé")
        return False


def fetch_sanity_references(category_slug: str) -> Dict[str, str]:
    """Récupère les références Sanity"""
    if not SANITY_TOKEN:
        return {"category": None, "author": None}
    
    url = f"{SANITY_API_URL}/data/query/{SANITY_DATASET}"
    headers = {
        "Authorization": f"Bearer {SANITY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    groq_query = """{
      "category": *[_type == "category" && slug.current == $categorySlug][0]._id,
      "author": *[_type == "author" && name == "Matthieu HUBERT"][0]._id
    }"""
    
    payload = {
        "query": groq_query,
        "params": {"categorySlug": category_slug}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("result", {})
    except:
        pass
    
    return {"category": None, "author": None}


def publish_to_production(article_data: Dict[str, Any], references: Dict[str, str]) -> bool:
    """Publie directement en PRODUCTION"""
    if not SANITY_TOKEN:
        print("❌ SANITY_TOKEN manquant dans .env")
        return False
    
    print("\n🚀 Publication en PRODUCTION...")
    
    slug = article_data.get("slug", "")
    base_id = slug.replace("-", "_") if slug else str(uuid.uuid4())[:8]
    document_id = base_id  # SANS préfixe drafts. = PRODUCTION
    
    html_content = article_data.get("blog_post", "")
    
    post_data = {
        "_id": document_id,
        "_type": "post",
        "title": article_data.get("title", ""),
        "slug": {
            "_type": "slug",
            "current": slug
        },
        "excerpt": article_data.get("summary", ""),
        "body": [{
            "_key": generate_key(),
            "_type": "block",
            "style": "normal",
            "children": [{
                "_key": generate_key(),
                "_type": "span",
                "text": html_content,
                "marks": []
            }],
            "markDefs": []
        }],
        "publishedAt": datetime.now().isoformat()
    }
    
    # Ajouter références
    if references.get("author"):
        post_data["author"] = {
            "_type": "reference",
            "_ref": references["author"]
        }
    if references.get("category"):
        post_data["categories"] = [{
            "_key": generate_key(),
            "_type": "reference",
            "_ref": references["category"]
        }]
    
    mutation = {
        "mutations": [{
            "create": post_data
        }]
    }
    
    url = f"{SANITY_API_URL}/data/mutate/{SANITY_DATASET}"
    headers = {
        "Authorization": f"Bearer {SANITY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=mutation, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Article publié en PRODUCTION !")
            print(f"   ID: {document_id}")
            print(f"   Titre: {article_data.get('title', 'N/A')}")
            print(f"   Slug: {slug}")
            print(f"   Transaction: {result.get('transactionId', 'N/A')}")
            print()
            print("🔍 L'article est maintenant visible dans votre dashboard Sanity Studio !")
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Workflow complet"""
    print("=" * 70)
    print("🚀 WORKFLOW AVEC VALIDATION (GRATUIT)")
    print("=" * 70)
    print()
    
    # Récupérer le sujet
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        try:
            topic = input("📝 Entrez le sujet de l'article: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            sys.exit(1)
    
    if not topic:
        print("❌ Un sujet est requis")
        sys.exit(1)
    
    try:
        # 1. Génération
        print("\n📝 Étape 1/5: Génération de l'article...")
        article = generate_article(topic)
        print("✅ Article généré\n")
        
        # 2. Style
        print("🎨 Étape 2/5: Application du style éditorial...")
        styled = apply_style(article)
        print("✅ Style appliqué\n")
        
        # 3. SEO
        print("🔍 Étape 3/5: Optimisation SEO...")
        article_data = optimize_seo(styled)
        # Sauvegarder le contenu original
        article_data["original_content"] = styled
        print("✅ SEO optimisé\n")
        
        # 4. Sauvegarder pour review
        print("💾 Étape 4/5: Sauvegarde pour review...")
        filepath = save_article_for_review(article_data, topic)
        print(f"✅ Article sauvegardé dans: {filepath}\n")
        
        # 5. Afficher résumé et demander validation
        print("👀 Étape 5/5: Review...")
        display_summary(article_data, filepath)
        
        validated = ask_validation()
        
        if validated:
            # 6. Récupérer références
            print("\n🔗 Récupération des références Sanity...")
            category_slug = article_data.get("tag", "")
            references = fetch_sanity_references(category_slug)
            print("✅ Références récupérées\n")
            
            # 7. Publication en production
            success = publish_to_production(article_data, references)
            
            if success:
                print()
                print("=" * 70)
                print("✅ TERMINÉ - Article publié en production !")
                print("=" * 70)
                print(f"\n💾 Le fichier de review reste disponible: {filepath}")
            else:
                print()
                print("=" * 70)
                print("❌ ERREUR lors de la publication")
                print("=" * 70)
                print(f"\n💾 Le fichier de review est disponible: {filepath}")
                sys.exit(1)
        else:
            print()
            print("=" * 70)
            print("⚠️  Publication annulée")
            print("=" * 70)
            print(f"\n💾 L'article reste sauvegardé dans: {filepath}")
            print("   Vous pouvez le relancer plus tard si vous le souhaitez")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

