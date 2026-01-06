#!/usr/bin/env python3
"""
Script d'automatisation pour générer et publier des articles de blog sur Sanity
Reproduit le workflow n8n décrit dans la configuration
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuration des APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID", "8y6orojx")
SANITY_DATASET = os.getenv("SANITY_DATASET", "development")
SANITY_USE_DRAFT = os.getenv("SANITY_USE_DRAFT", "true").lower() == "true"
SANITY_TOKEN = os.getenv("SANITY_TOKEN")
SANITY_API_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2021-06-07"
REVALIDATE_URL = os.getenv("REVALIDATE_URL", "https://www.lamignonnecouverture.fr/api/revalidate")

# Initialisation des clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)


class BlogAutomation:
    """Classe principale pour automatiser la génération et publication d'articles"""
    
    def __init__(self):
        self.current_date = datetime.now()
        self.year = self.current_date.year
        self.readable_date = self.current_date.strftime("%d/%m/%Y")
        
    def search_web(self, query: str) -> str:
        """Effectue une recherche web via Perplexity"""
        print(f"🔍 Recherche web: {query}")
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides recent and accurate information."
                },
                {
                    "role": "user",
                    "content": query
                }
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
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ Erreur recherche Perplexity: {e}")
            return ""
    
    def generate_article(self, topic: str) -> str:
        """Génère l'article initial avec recherche web"""
        print(f"📝 Génération de l'article sur: {topic}")
        
        # Recherche web préalable
        search_query = f"Recherche des données récentes, études de cas, chiffres, retours d'expérience 2025 sur {topic}, agents vocaux IA, automatisation des appels, support client"
        web_results = self.search_web(search_query)
        
        system_prompt = f"""✍️ Blog Article Generator (1 000+ mots, optimisé pour la rétention) — version "Rounded / Voice Agents"
📅 Contexte temporel

IMPORTANT : la date du jour est {self.readable_date}. Tout contenu doit refléter les tendances, données, et références actuelles de {self.year}.
Ne mentionne pas de statistiques antérieures à {self.year} sauf pour un contexte historique. Utilise des expressions comme : "en {self.year}", "cette année", "tendances récentes", "actuel", "le plus récent", pour assurer que le contenu soit perçu comme à jour et pertinent.

🎯 Rôle & objectif

Tu es un rédacteur professionnel spécialisé dans l'IA vocale et les technologies de téléphonie automatisée. Ton travail est de créer des articles de blog engageants, bien structurés, et documentés — conçus pour capter l'attention, apporter une valeur réelle, et convertir des lecteurs en leads ou utilisateurs de Rounded.

⭐ Consigne de marque (branding subtil)

Dans chaque article, mentionne régulièrement Rounded — comme référence crédible de solution d'agent vocal IA, en expliquant comment elle s'intègre dans les usages décrits, sans forcer la promotion. L'objectif est de positionner Rounded comme expert et pionnier du voice-automation, tout en fournissant une information utile et honnête.

✅ Objectifs principaux

Pour chaque article :

Commencer par effectuer une recherche en ligne (via web) pour rassembler des données récentes, des exemples, des statistiques, et des tendances 2025 sur les agents vocaux, l'IA vocale, la téléphonie automatisée, les usages entreprises, etc.

Adapter le contenu au profil cible : responsables CRM, marketing, relation client, dirigeants PME/ETI, responsables support, tout décideur intéressé par la voix comme canal de service ou vente.

Fournir un texte de minimum 1 000 mots pour offrir de la profondeur et un vrai levier SEO.

Utiliser toujours l'année en cours pour les références temporelles, sauf pour l'historique.

🧠 Guidelines de rédaction

L'article doit :

Commencer par une introduction percutante, qui explique l'enjeu (ex : "Pourquoi l'IA vocale change la donne en 2025 pour les entreprises").

Adopter un ton professionnel, clair, fluide, facile à lire — éviter le jargon excessif, privilégier la lisibilité.

S'appuyer sur exemples concrets, données récentes, études, citations ou statistiques pour asseoir la crédibilité.

Être structuré :

Titres H2 / H3 explicites et SEO-friendly

Paragraphes courts + listes à puces / numérotées quand pertinent

Format "scannable" (facile à lire en diagonale)

Utiliser des émojis de façon très modérée (1 à 3 max), uniquement si cela enrichit le ton ou clarifie l'idée.

Conclure par une section forte : résumé des points-clés, appels à l'action (inscription, test de Rounded, contact, etc.), éventuellement des liens vers des guides ou outils.

⚙️ Règles de sortie

Tu ne renvoies que le texte final de l'article, en Markdown, avec les balises de titres appropriées.

Au moins 1 000 mots — sauf demande explicite de l'utilisateur.

Pas de notes internes, pas de commentaires "méta".
"""
        
        user_prompt = f"""Sujet de l'article : {topic}

Données de recherche web récentes :
{web_results}

Génère un article complet selon les consignes ci-dessus."""
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erreur génération article: {e}")
            raise
    
    def apply_style(self, article_content: str) -> str:
        """Applique le style éditorial Rounded à l'article"""
        print("🎨 Application du style éditorial")
        
        style_prompt = """🎤 Guide de ton & style pour Rounded — "Inform – Amuse – Convertis"
🎭 Voix & personnalité

Tu es un rédacteur drôle, un peu espiègle, mais sérieux dans l'info — un peu comme cet oncle sympa qui te parle tech entre deux blagues (et parfois un soupçon de sarcasme). Tu peux glisser des références pop-culture, des petites blagues ou analogies absurdes, tout en restant pertinent et crédible. L'idée : rendre l'univers parfois aride de l'IA vocale vivant, accessible, humain.

🧑‍🏫 Style d'écriture

Commence fort : un hook drôle, une anecdote légère ou une phrase un peu absurde — pour accrocher direct l'attention.

N'hésite pas à faire des remarques auto-dérisoires ou jouer la carte de la modestie : "Oui, je parle d'un script téléphonique… mais promis, c'est (un peu) sexy."

Utilise un ton conversatif, décontracté, comme si tu discutais autour d'un café :

"Allez, on remet les… poulains sur le ring."

"Tu me suis ? On repart en 3…2…1."

Pose des questions rhétoriques, parle à ton lecteur directement : "Toujours là ? Wow, tu es officiellement mon·ma préfér·é·e."

Quand il faut passer à du contenu sérieux ou technique, : change de registre — mais garde le clin d'œil, le petit sourire : tu restes ce prof un peu cool, pas ce prof relou.

Termine chaque bloc / section — ou du moins régulièrement — par un petit "takeaway" (conclusion drôle, métaphore, conseil simple) : comme si tu finis un chapitre avec un high-five mental.

🎯 Pourquoi ça marche / ce que ça apporte

Un style non conventionnel retient l'attention — plus engageant qu'un article "sec et corporate". Cela rend l'IA vocale (un sujet tech) plus humain, plus abordable.

Cela pose une voix de marque reconnaissable : entre sérieux, expertise, et décontraction — ce qui peut aider Rounded à se différencier.

Ce ton favorise l'accessibilité : quand un texte semble "vivant", plus de lecteurs restent jusqu'au bout et reteniennent l'essentiel.

🧩 Ce qu'un guide de style éditorial Rounded pourrait contenir

Définition de la voix de marque (expert friendly, accessible, un brin drôle, pas pompeux)

Exemples d'phrases-type / punchlines / hooks d'intro (mais aussi ce qu'il faut éviter — jargon trop lourd, ton pompeux, blague "trop spin modérée", etc.)

Règles de structure d'article : titres H2/H3 clairs, paragraphes courts, sections "takeaway", listes, etc. (pour le scannable) — ce qui rejoint les bonnes pratiques de blog B2B.

Consignes sur le niveau de jargon technique : accessible au décideur non-tech + possibilité de glisser un petit encart "pour les geeks" si besoin

Règles d'équilibre entre ton léger / humour et contenu sérieux / valeur — pour préserver crédibilité et clarté"""
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": style_prompt},
                    {"role": "user", "content": f"Please write this blog in the style above:\n{article_content}"}
                ],
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Erreur application style: {e}")
            raise
    
    def optimize_seo(self, styled_article: str) -> Dict[str, Any]:
        """Optimise l'article pour le SEO et structure les données"""
        print("🔍 Optimisation SEO")
        
        system_prompt = """You are an expert SEO copywriter. Your task is to rewrite the input text to match a specified **writing style** while optimizing it for the given **SEO keywords**.  

Your output should:
- Retain the original meaning and intent.  
- Follow the requested writing style (e.g., formal, casual, persuasive, punchy, friendly), changing the least amount possible
- Naturally and effectively include the provided SEO keywords, without stuffing.  
- Use proper grammar and smooth transitions.  
- Be engaging and easy to read.  

Return only the improved version of the text.  

## ✅ Output Behavior

- Rewritten in the defined style  
- Keywords naturally embedded  
- Clear, engaging copy
"""
        
        output_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A concise and engaging blog post title (3–8 words, maximum 60 characters for SEO)"
                },
                "summary": {
                    "type": "string",
                    "description": "A short 1–2 sentence summary optimized for SEO (acts as meta description, maximum 155–160 characters)"
                },
                "blog_post": {
                    "type": "string",
                    "description": "The full blog post content in HTML format (use <h2>, <h3>, <p>, <ul>, <li>). Minimum 1,000 words."
                },
                "slug": {
                    "type": "string",
                    "description": "A clean, SEO-friendly URL slug generated from the title (lowercase, hyphen-separated, no special characters)"
                },
                "readTime": {
                    "type": "string",
                    "description": "Estimated reading time (e.g. \"5 min\", \"10 min\")"
                },
                "tag": {
                    "type": "string",
                    "description": "One category slug selected from the following list (MUST match exactly): conseils-entretien, renovation-reparation, materiaux-couverture, charpente, isolation-performance-energetique, zinguerie-etancheite, reglementation-normes, climat-environnement, guides-pratiques, actualites-tendances"
                },
                "metaTitle": {
                    "type": "string",
                    "description": "Title for SEO (optional, max 60 chars)"
                },
                "metaDescription": {
                    "type": "string",
                    "description": "SEO Description (optional, max 160 chars)"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of SEO keywords (e.g. [\"DJ Paris\", \"mariage\"])"
                },
                "focusKeyword": {
                    "type": "string",
                    "description": "Main keyword for the article"
                },
                "ogTitle": {
                    "type": "string",
                    "description": "Social media title (Open Graph)"
                },
                "ogDescription": {
                    "type": "string",
                    "description": "Social media description"
                },
                "structuredData": {
                    "type": "string",
                    "description": "JSON-LD Structured Data (optional)"
                }
            },
            "required": ["title", "summary", "blog_post", "slug", "readTime", "tag"]
        }
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please write this blog in the style above:\n{styled_article}"},
                    {"role": "assistant", "content": json.dumps(output_schema, indent=2)}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ Erreur optimisation SEO: {e}")
            raise
    
    def generate_image_prompt(self, article_data: Dict[str, Any]) -> Dict[str, str]:
        """Génère un prompt pour l'image de l'article"""
        print("🖼️  Génération du prompt d'image")
        
        system_prompt = """Your goal is to analyze a blog post and create a single, comprehensive image prompt that represents the main topic and theme of the entire article. The image should capture the essence of the blog post in one powerful visual. Also generate alt text and caption for accessibility and SEO."""
        
        article_content = article_data.get("blog_post", "")
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": article_content},
                    {"role": "assistant", "content": """Please output the following data in JSON format with the following structure:
{
"blog_post_images": {
  "prompt": "...",
  "alt_text": "...",
  "caption": "..."
}
}"""}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("blog_post_images", {})
        except Exception as e:
            print(f"❌ Erreur génération prompt image: {e}")
            raise
    
    def generate_image(self, image_prompt_data: Dict[str, str]) -> bytes:
        """Génère l'image via Google Gemini"""
        print("🎨 Génération de l'image")
        
        prompt = f"""You are a high-quality illustration generator for a modern AI voice agent blog (Rounded).
Always generate images in this exact style:

Flat design, simplified shapes

Cartoon-style characters with minimal facial details

Bold outlines, smooth curves

Dominant orange background (#FF7A00 style)

Black or dark outlines, white / cream highlights

Minimalist, clean, high-contrast composition

Icons related to voice, phone, sound waves, AI, automation

Scenes showing callers, assistants, agents, interactions

No realism, no photography, no 3D, no gradients

Only simple, crisp, vector-like illustrations

Focus on clarity and concept more than detail

Generate: {image_prompt_data.get('prompt', '')}"""
        
        try:
            # Tentative avec le modèle image de Gemini
            # Note: L'API peut varier selon la version, adaptation nécessaire
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "image/png"
                    }
                )
                
                # Vérification de la réponse
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            return base64.b64decode(part.inline_data.data)
                        elif hasattr(part, 'data'):
                            return part.data
                
                # Si la réponse contient une URL
                if hasattr(response, 'text') and response.text:
                    # Tentative de téléchargement depuis URL
                    import re
                    url_match = re.search(r'https?://[^\s]+', response.text)
                    if url_match:
                        img_url = url_match.group(0)
                        img_response = requests.get(img_url, timeout=60)
                        img_response.raise_for_status()
                        return img_response.content
                
            except Exception as e1:
                print(f"⚠️  Tentative modèle image échouée: {e1}")
                # Fallback: utiliser l'API REST de Gemini
                try:
                    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "response_mime_type": "image/png"
                        }
                    }
                    
                    response = requests.post(url, json=payload, timeout=120)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extraction de l'image depuis la réponse
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                if 'inlineData' in part:
                                    return base64.b64decode(part['inlineData']['data'])
                                elif 'data' in part:
                                    return part['data']
                                    
                except Exception as e2:
                    print(f"⚠️  Tentative API REST échouée: {e2}")
            
            raise Exception("Impossible de générer l'image avec Gemini. Vérifiez votre clé API et la disponibilité du modèle.")
            
        except Exception as e:
            print(f"❌ Erreur génération image: {e}")
            print("💡 Astuce: Vérifiez que GOOGLE_GEMINI_API_KEY est correcte et que le modèle image est disponible")
            raise
    
    def upload_to_sanity(self, image_data: bytes, filename: str = "blog-image.png") -> Dict[str, Any]:
        """Upload l'image sur Sanity"""
        print("📤 Upload de l'image sur Sanity")
        
        # Pour les assets/images, on utilise le dataset normal
        # Les assets ne nécessitent pas de préfixe drafts, seuls les documents en ont besoin
        url = f"{SANITY_API_URL}/assets/images/{SANITY_DATASET}"
        
        headers = {
            "Authorization": f"Bearer {SANITY_TOKEN}"
        }
        
        files = {
            "file": (filename, image_data, "image/png")
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erreur upload Sanity: {e}")
            raise
    
    def fetch_sanity_references(self, category_slug: str) -> Dict[str, Optional[str]]:
        """Récupère les références (category, author) depuis Sanity"""
        print(f"🔗 Récupération des références Sanity pour catégorie: {category_slug}")
        
        # Pour les queries, on utilise le dataset standard
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
            "params": {
                "categorySlug": category_slug
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
        except Exception as e:
            print(f"❌ Erreur récupération références: {e}")
            return {"category": None, "author": None}
    
    def create_sanity_post(self, article_data: Dict[str, Any], image_asset_id: str, 
                          references: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Crée le post dans Sanity"""
        mode_text = "brouillon" if SANITY_USE_DRAFT else "production"
        print(f"📝 Création du post dans Sanity ({mode_text})")
        
        import random
        import string
        import uuid
        
        def generate_key():
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        def generate_document_id():
            """Génère un ID unique pour le document"""
            # Génère un ID basé sur le slug ou un UUID
            slug = article_data.get("slug", "")
            base_id = slug.replace("-", "_") if slug else str(uuid.uuid4())[:8]
            # IMPORTANT: Pour créer un DRAFT (non publié), préfixe avec "drafts."
            # Sans préfixe, le document est PUBLIÉ et visible dans le dashboard
            if SANITY_USE_DRAFT:
                return f"drafts.{base_id}"  # Draft (non publié, visible avec perspective='raw' ou 'drafts')
            return base_id  # Publié (visible dans dashboard avec perspective='published')
        
        category_id = references.get("category")
        author_id = references.get("author")
        
        # Construction des références
        category_ref = None
        if category_id:
            category_ref = {
                "_key": generate_key(),
                "_type": "reference",
                "_ref": category_id
            }
        
        author_ref = None
        if author_id:
            author_ref = {
                "_type": "reference",
                "_ref": author_id
            }
        
        # Récupération du contenu
        body_content = article_data.get("blog_post", "")
        if not body_content or body_content.strip() == "":
            raise ValueError("Body content is empty or null")
        
        title = article_data.get("title", "")
        slug = article_data.get("slug", "")
        excerpt = article_data.get("summary", "")
        
        if not title or not slug:
            raise ValueError("Title or slug is missing")
        
        # Génération de l'ID du document avec préfixe drafts. si nécessaire
        document_id = generate_document_id()
        
        # Construction du body en format Sanity
        # Conversion HTML vers format Sanity Block Content
        # Simplification: on crée un bloc simple avec le texte
        post_data = {
            "_id": document_id,
            "_type": "post",
            "title": str(title),
            "slug": {
                "_type": "slug",
                "current": str(slug)
            },
            "excerpt": str(excerpt),
            "body": [{
                "_key": generate_key(),
                "_type": "block",
                "style": "normal",
                "children": [{
                    "_key": generate_key(),
                    "_type": "span",
                    "text": body_content,
                    "marks": []
                }],
                "markDefs": []
            }],
            "publishedAt": datetime.now().isoformat()
        }
        
        if image_asset_id:
            post_data["mainImage"] = {
                "_type": "image",
                "asset": {
                    "_type": "reference",
                    "_ref": image_asset_id
                }
            }
        
        if author_ref:
            post_data["author"] = author_ref
        
        if category_ref:
            post_data["categories"] = [category_ref]
        
        mutation = {
            "mutations": [{
                "create": post_data
            }]
        }
        
        # Utiliser l'endpoint standard du dataset (les drafts sont gérés via le préfixe _id)
        url = f"{SANITY_API_URL}/data/mutate/{SANITY_DATASET}"
        
        headers = {
            "Authorization": f"Bearer {SANITY_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=mutation, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erreur création post: {e}")
            print(f"Payload: {json.dumps(mutation, indent=2)}")
            raise
    
    def revalidate_site(self, slug: str) -> bool:
        """Révalide le site Next.js"""
        print(f"🔄 Révalidation du site pour slug: {slug}")
        
        try:
            response = requests.post(
                REVALIDATE_URL,
                json={"slug": slug},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"⚠️  Erreur révalidation (non bloquante): {e}")
            return False
    
    def run(self, topic: str):
        """Exécute le workflow complet"""
        print("🚀 Démarrage de l'automatisation du blog")
        print(f"📅 Date: {self.readable_date} ({self.year})")
        print(f"📌 Sujet: {topic}\n")
        
        try:
            # 1. Génération de l'article
            article_content = self.generate_article(topic)
            
            # 2. Application du style
            styled_article = self.apply_style(article_content)
            
            # 3. Optimisation SEO
            article_data = self.optimize_seo(styled_article)
            print(f"✅ Article optimisé: {article_data.get('title')}")
            
            # 4. Génération du prompt d'image
            image_prompt_data = self.generate_image_prompt(article_data)
            
            # 5. Génération de l'image
            image_data = self.generate_image(image_prompt_data)
            
            # 6. Upload de l'image sur Sanity
            image_asset = self.upload_to_sanity(image_data)
            image_asset_id = image_asset.get("document", {}).get("_id")
            print(f"✅ Image uploadée: {image_asset_id}")
            
            # 7. Récupération des références
            category_slug = article_data.get("tag", "")
            references = self.fetch_sanity_references(category_slug)
            print(f"✅ Références récupérées: {references}")
            
            # 8. Création du post
            post_result = self.create_sanity_post(article_data, image_asset_id, references)
            print(f"✅ Post créé avec succès")
            
            # 9. Révalidation du site
            slug = article_data.get("slug", "")
            self.revalidate_site(slug)
            
            print("\n🎉 Workflow terminé avec succès!")
            print(f"📝 Article publié: {article_data.get('title')}")
            print(f"🔗 Slug: {slug}")
            
            return {
                "success": True,
                "article": article_data,
                "post": post_result
            }
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'exécution: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Point d'entrée principal"""
    import sys
    
    # Récupération du sujet depuis les arguments ou prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Entrez le sujet de l'article de blog: ")
    
    if not topic:
        print("❌ Un sujet est requis")
        sys.exit(1)
    
    # Vérification des variables d'environnement essentielles
    required_vars = ["OPENAI_API_KEY", "PERPLEXITY_API_KEY", "GOOGLE_GEMINI_API_KEY", "SANITY_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing)}")
        print("Veuillez créer un fichier .env avec ces variables")
        sys.exit(1)
    
    # Exécution
    automation = BlogAutomation()
    result = automation.run(topic)
    
    if result["success"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

