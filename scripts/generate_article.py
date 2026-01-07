#!/usr/bin/env python3
"""
Générateur d'articles avec :
- Vérification des sujets existants sur callrounded.com/blog
- Recherche web via Perplexity
- Génération avec OpenAI (style Rounded)
- Validation avant publication
"""

import os
import sys
import json
import requests
import uuid
import random
import string
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sanity_utils import html_to_sanity_blocks

load_dotenv()

def convert_text_to_sanity_blocks(text: str) -> list:
    """
    Convertit du texte brut (markdown-like) en format Sanity Block Content
    """
    import random
    import string
    
    def gen_key():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    blocks = []
    lines = text.split('\n')
    
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                blocks.append({
                    "_key": gen_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": [{"_key": gen_key(), "_type": "span", "text": para_text, "marks": []}],
                    "markDefs": []
                })
                current_paragraph = []
            continue
        
        # H2 (##)
        if line.startswith('## '):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                blocks.append({
                    "_key": gen_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": [{"_key": gen_key(), "_type": "span", "text": para_text, "marks": []}],
                    "markDefs": []
                })
                current_paragraph = []
            blocks.append({
                "_key": gen_key(),
                "_type": "block",
                "style": "h2",
                "children": [{"_key": gen_key(), "_type": "span", "text": line[3:].strip(), "marks": []}],
                "markDefs": []
            })
            continue
        
        # H3 (###)
        if line.startswith('### '):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                blocks.append({
                    "_key": gen_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": [{"_key": gen_key(), "_type": "span", "text": para_text, "marks": []}],
                    "markDefs": []
                })
                current_paragraph = []
            blocks.append({
                "_key": gen_key(),
                "_type": "block",
                "style": "h3",
                "children": [{"_key": gen_key(), "_type": "span", "text": line[4:].strip(), "marks": []}],
                "markDefs": []
            })
            continue
        
        # Liste (• ou - ou numéro)
        if line.startswith('• ') or line.startswith('- ') or re.match(r'^\d+\.\s', line):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                blocks.append({
                    "_key": gen_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": [{"_key": gen_key(), "_type": "span", "text": para_text, "marks": []}],
                    "markDefs": []
                })
                current_paragraph = []
            
            item_text = re.sub(r'^(•|-|\d+\.)\s+', '', line)
            children = parse_marks_for_blocks(item_text)
            
            blocks.append({
                "_key": gen_key(),
                "_type": "block",
                "style": "normal",
                "listItem": "bullet",
                "children": children,
                "markDefs": []
            })
            continue
        
        current_paragraph.append(line)
    
    if current_paragraph:
        para_text = ' '.join(current_paragraph)
        children = parse_marks_for_blocks(para_text)
        blocks.append({
            "_key": gen_key(),
            "_type": "block",
            "style": "normal",
            "children": children,
            "markDefs": []
        })
    
    if not blocks:
        blocks.append({
            "_key": gen_key(),
            "_type": "block",
            "style": "normal",
            "children": [{"_key": gen_key(), "_type": "span", "text": text, "marks": []}],
            "markDefs": []
        })
    
    return blocks


def parse_marks_for_blocks(text: str) -> list:
    """Parse le texte et extrait les marques (gras **texte**)"""
    import random
    import string
    
    def gen_key():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    children = []
    pattern = r'\*\*(.+?)\*\*'
    parts = re.split(pattern, text)
    
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 1:  # Gras
            children.append({
                "_key": gen_key(),
                "_type": "span",
                "text": part,
                "marks": ["strong"]
            })
        else:
            if part.strip():
                children.append({
                    "_key": gen_key(),
                    "_type": "span",
                    "text": part,
                    "marks": []
                })
    
    if not children:
        children.append({
            "_key": gen_key(),
            "_type": "span",
            "text": text,
            "marks": []
        })
    
    return children

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID", "8y6orojx")
SANITY_DATASET = os.getenv("SANITY_DATASET", "development")
SANITY_TOKEN = os.getenv("SANITY_TOKEN")
SANITY_API_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-12-11"

# URLs
ROUNDED_BLOG_URL = "https://callrounded.com/blog"
ROUNDED_DONNA_URL = "https://callrounded.com/cas-usage/secretariat-medical"

# Dossier pour sauvegarder les articles (relatif à la racine du projet)
BASE_DIR = Path(__file__).parent.parent
ARTICLES_DIR = BASE_DIR / "articles"
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


def get_existing_blog_topics() -> List[str]:
    """Récupère les sujets existants depuis la base de connaissances locale et le site web"""
    print("🔍 Vérification des sujets existants sur le blog Rounded...")
    
    titles = []
    
    # 1. Charger depuis le fichier JSON local (base de connaissances)
    try:
        json_path = BASE_DIR / "data" / "articles_existants.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                titles.extend([article["titre"] for article in articles])
            print(f"✅ {len(titles)} articles chargés depuis la base de connaissances locale")
    except Exception as e:
        print(f"⚠️  Erreur chargement base locale: {e}")
    
    # 2. Compléter avec le scraping du site web (optionnel)
    try:
        url = f"{ROUNDED_BLOG_URL}?_cb={int(datetime.now().timestamp() * 1000)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        
        # Extraire les titres des articles
        patterns = [
            r'<h[23][^>]*>([^<]+)</h[23]>',
            r'Lire l\'article[^>]*>([^<]+)</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            titles.extend([m.strip() for m in matches if len(m.strip()) > 10])
        
    except Exception as e:
        print(f"⚠️  Scraping web échoué (non bloquant): {e}")
    
    # Nettoyer et dédupliquer
    titles = list(set([t for t in titles if t and len(t) > 10]))
    
    print(f"✅ {len(titles)} articles existants trouvés au total")
    if titles:
        print("   Exemples:", titles[:3])
    
    return titles


def check_topic_exists(topic: str, existing_topics: List[str]) -> bool:
    """Vérifie si un sujet est trop similaire aux articles existants"""
    if not existing_topics:
        return False
    
    topic_lower = topic.lower()
    
    # Mots-clés du sujet (enlever les mots communs)
    stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'à', 'en', 'pour', 'avec', 'sur', 'dans', 'par', 'comment', 'pourquoi', 'quand', 'que', 'qui', 'quoi'}
    topic_words = set([w for w in topic_lower.split() if w not in stop_words and len(w) > 2])
    
    similar_articles = []
    
    for existing in existing_topics:
        existing_lower = existing.lower()
        existing_words = set([w for w in existing_lower.split() if w not in stop_words and len(w) > 2])
        
        # Vérifier le chevauchement des mots-clés importants
        if len(topic_words) > 0:
            overlap = len(topic_words & existing_words)
            # Similarité basée sur les mots significatifs
            similarity = overlap / max(len(topic_words), len(existing_words))
            
            # Si plus de 35% de similarité, c'est probablement trop similaire
            if similarity > 0.35:
                similar_articles.append((existing, similarity))
    
    if similar_articles:
        # Trier par similarité décroissante
        similar_articles.sort(key=lambda x: x[1], reverse=True)
        print(f"\n⚠️  {len(similar_articles)} article(s) similaire(s) trouvé(s):")
        for article, sim in similar_articles[:3]:
            print(f"   - '{article}' (similarité: {sim:.0%})")
        return True
    
    return False


def search_web(query: str) -> str:
    """Recherche web via Perplexity - retourne le contenu"""
    result = search_web_with_sources(query)
    return result.get("content", "") if isinstance(result, dict) else result

def search_web_with_sources(query: str) -> dict:
    """Recherche web via Perplexity avec extraction des sources"""
    if not PERPLEXITY_API_KEY:
        return {"content": "", "sources": []}
    
    print("🔍 Recherche web via Perplexity...")
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in medical practices, healthcare technology, and voice AI assistants."},
            {"role": "user", "content": query}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        # Extraire le contenu
        content = data["choices"][0]["message"]["content"]
        
        # Extraire les citations/sources
        sources = []
        
        # Perplexity retourne les citations dans différents formats selon le modèle
        # Format 1: Dans la réponse principale
        if "citations" in data:
            sources = data["citations"]
        # Format 2: Dans le message
        elif "choices" in data and len(data["choices"]) > 0:
            message = data["choices"][0]["message"]
            if "citations" in message:
                sources = message["citations"]
        
        # Format 3: Dans les métadonnées de la réponse
        if not sources and "choices" in data:
            choice = data["choices"][0]
            if "citations" in choice:
                sources = choice["citations"]
        
        # Si pas de citations structurées, essayer d'extraire les URLs du contenu
        if not sources:
            import re
            from urllib.parse import urlparse
            
            # Chercher les URLs dans le contenu (format [1], [2], etc. ou URLs directes)
            url_pattern = r'https?://[^\s\)\]\>]+'
            urls = re.findall(url_pattern, content)
            if urls:
                # Nettoyer les URLs (enlever les caractères de fin)
                cleaned_urls = []
                for url in urls:
                    # Enlever les caractères de ponctuation à la fin
                    url = url.rstrip('.,;:!?)')
                    if url not in cleaned_urls:
                        cleaned_urls.append(url)
                
                # Créer des objets source avec domaine extrait
                sources = []
                for url in cleaned_urls:
                    try:
                        parsed = urlparse(url)
                        domain = parsed.netloc
                        sources.append({
                            "url": url,
                            "domain": domain,
                            "name": domain.replace("www.", "")
                        })
                    except:
                        sources.append({"url": url})
        
        # Normaliser les sources (s'assurer qu'elles sont toutes des dicts avec métadonnées)
        normalized_sources = []
        for source in sources:
            if isinstance(source, dict):
                # Enrichir avec des métadonnées si manquantes
                if "url" in source and "domain" not in source:
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(source["url"])
                        source["domain"] = parsed.netloc
                        if "name" not in source:
                            source["name"] = parsed.netloc.replace("www.", "")
                    except:
                        pass
                
                # S'assurer qu'il y a au moins un titre/name
                if "title" not in source and "name" not in source:
                    if "domain" in source:
                        source["name"] = source["domain"].replace("www.", "")
                    elif "url" in source:
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(source["url"])
                            source["name"] = parsed.netloc.replace("www.", "")
                        except:
                            source["name"] = "Source"
                
                normalized_sources.append(source)
            elif isinstance(source, str):
                # Si c'est juste une URL string, créer un dict
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(source)
                    normalized_sources.append({
                        "url": source,
                        "domain": parsed.netloc,
                        "name": parsed.netloc.replace("www.", "")
                    })
                except:
                    normalized_sources.append({"url": source, "name": "Source"})
        
        print("✅ Recherche terminée")
        return {
            "content": content,
            "sources": normalized_sources
        }
    except Exception as e:
        print(f"⚠️  Erreur recherche Perplexity: {e}")
        return {"content": "", "sources": []}


def load_existing_articles() -> List[Dict[str, Any]]:
    """Charge tous les articles existants depuis data/articles_existants.json"""
    json_path = BASE_DIR / "data" / "articles_existants.json"
    try:
        if not json_path.exists():
            return []
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        return articles if isinstance(articles, list) else []
    except Exception as e:
        print(f"⚠️  Erreur chargement articles existants: {e}")
        return []


def generate_topic_variants(
    topic: str,
    existing_articles: List[Dict[str, Any]],
    target_keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Génère 3 variantes de sujets à partir d'un sujet brut :
    - titre en une phrase
    - angle éditorial
    - mini-plan (3–5 points)
    """
    if not openai_client:
        raise ValueError("OPENAI_API_KEY non configurée dans .env")

    print("\n🧠 Génération de 3 variantes de sujets (titre + mini-plan)...")

    existing_titles = [art.get("titre", "") for art in existing_articles if art.get("titre")]
    existing_titles_snippet = "\n".join(f"- {t}" for t in existing_titles[:20]) if existing_titles else ""

    keywords_snippet = ", ".join(target_keywords or []) if target_keywords else ""

    system_prompt = """Tu es un content strategist SEO pour une startup SaaS spécialisée dans les agents vocaux IA (comme Donna chez Rounded).

Ton rôle : proposer des idées d'articles de blog B2B très ciblées, différenciées de l'existant, adaptées aux décideurs (direction, responsables opérations, médecins, etc.). 
Tu ne cites JAMAIS de concurrents ni de marques tierces (airagent.ai, etc.). Tu t'en inspires uniquement pour le niveau de sophistication, jamais dans le nom.

Contraintes :
- Ne JAMAIS répéter exactement un titre existant.
- Éviter les doublons de sujets déjà traités.
- Intégrer naturellement les mots-clés fournis quand c'est pertinent (sans keyword stuffing).
- Chaque variante doit avoir un angle bien distinct (problématique, comparatif, cas d'usage, ROI, etc.).

Format de sortie : un objet JSON avec un tableau 'variants' de 3 éléments. 
Chaque élément doit avoir :
- title: string (titre en une phrase, max 90 caractères)
- angle: string (1–2 phrases qui expliquent l'angle éditorial)
- outline: array de 3 à 5 puces (mini-plan de l'article)
"""

    # Détecter le secteur cible depuis le sujet
    sector_hint = ""
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ["syndic", "copropriété", "gestionnaire immobilier", "immobilier"]):
        sector_hint = "syndics immobiliers / gestionnaires de copropriétés"
    elif any(word in topic_lower for word in ["médical", "médecin", "cabinet médical", "secrétaire médicale"]):
        sector_hint = "cabinets médicaux / secrétariat médical"
    elif any(word in topic_lower for word in ["agence immobilière", "immobilier"]):
        sector_hint = "agences immobilières"
    else:
        sector_hint = "entreprises / professionnels cherchant à automatiser leur accueil téléphonique"
    
    user_prompt = {
        "topic_seed": topic,
        "existing_titles": existing_titles_snippet,
        "target_keywords": keywords_snippet,
        "instructions": f"Propose 3 idées d'articles différentes mais cohérentes avec le sujet de départ '{topic}', en évitant les doublons avec les titres existants. L'article doit être adapté au secteur : {sector_hint}. Concentre-toi STRICTEMENT sur le secteur mentionné dans le sujet de départ, ne dévie pas vers d'autres secteurs."
    }

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=1200,
        )
        
        # Tracker les tokens
        if hasattr(response, 'usage') and response.usage:
            try:
                from utils.token_tracker import track_openai_usage
                track_openai_usage(
                    operation="generate_variants",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    topic=topic
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens: {e}")
        
        data = json.loads(response.choices[0].message.content)
        variants = data.get("variants") or data.get("ideas") or []
        # Normaliser un minimum
        cleaned: List[Dict[str, Any]] = []
        for v in variants[:3]:
            title = v.get("title") or v.get("titre") or ""
            angle = v.get("angle") or ""
            outline = v.get("outline") or v.get("plan") or []
            if not isinstance(outline, list):
                outline = [str(outline)]
            if title:
                cleaned.append(
                    {
                        "title": title.strip(),
                        "angle": angle.strip(),
                        "outline": [str(p).strip() for p in outline if str(p).strip()],
                    }
                )
        # S'assurer d'avoir 3 éléments (au pire dupliqués)
        while len(cleaned) < 3 and cleaned:
            cleaned.append(cleaned[len(cleaned) - 1])

        print("✅ 3 variantes de sujets générées")
        return cleaned[:3]
    except Exception as e:
        print(f"❌ Erreur génération variantes de sujets: {e}")
        raise


def generate_article(
    variant: Dict[str, Any],
    web_results: str = "",
    target_keywords: Optional[List[str]] = None,
) -> str:
    """Génère l'article complet à partir d'une variante (titre + angle + mini-plan)."""
    if not openai_client:
        raise ValueError("OPENAI_API_KEY non configurée dans .env")

    title = variant.get("title", "").strip()
    angle = variant.get("angle", "").strip()
    outline = variant.get("outline", []) or []

    print(f"📝 Génération de l'article complet pour la variante choisie : {title}")

    current_date = datetime.now()
    year = current_date.year
    readable_date = current_date.strftime("%d/%m/%Y")

    keywords_snippet = ", ".join(target_keywords or []) if target_keywords else ""

    # Style basé sur les exemples fournis
    system_prompt = f"""Tu es un rédacteur professionnel spécialisé dans les agents vocaux IA, le secrétariat médical, et les technologies de téléphonie automatisée pour les cabinets médicaux.

DATE ACTUELLE: {readable_date} ({year})

STYLE ET TON:
- Professionnel mais accessible, humain
- Structure claire avec des points numérotés (1., 2., 3., etc.) pour les sections principales uniquement
- Évite les numéros dans les sous-titres et sous-sections
- Chaque point commence par un titre court et percutant
- Utilise des exemples concrets et des situations réelles
- Ton rassurant et pratique pour les professionnels de santé
- Mentionne Donna (l'assistante vocale médicale de Rounded) de manière naturelle quand pertinent
- Ne force jamais la promotion, sois subtil et informatif
- INTERDICTION ABSOLUE : Ne jamais mentionner de concurrents ou d'autres entreprises (CareCall, Plateya, Talan, airagent.ai, etc.). Utilise des formulations génériques comme "des études récentes", "certaines solutions IA", etc.

STRUCTURE TYPE:
1. Introduction : contexte du problème (2-3 paragraphes)
2. Points principaux numérotés (3-6 points avec titres courts)
3. Conclusion : résumé + mention de Donna si pertinent + lien vers https://callrounded.com/cas-usage/secretariat-medical

MENTIONS DE DONNA:
- Mentionne Donna UNIQUEMENT si l'article traite spécifiquement de l'IA vocale dans le secrétariat médical
- Si l'article parle d'un autre secteur (immobilier, copropriété, etc.) ou d'un sujet non lié à l'IA vocale médicale, NE PAS mentionner Donna
- Si pertinent (IA vocale + secrétariat médical), dans la conclusion, propose le lien : Découvrir Donna : https://callrounded.com/cas-usage/secretariat-medical
- Ne pas sur-promouvoir, rester informatif
- Si le sujet n'est PAS en rapport avec l'IA vocale pour secrétariat médical, NE PAS ajouter de lien vers Donna

FORMAT:
- Minimum 1200 mots
- Utilise Markdown avec # pour les titres principaux
- ## pour les sous-titres de sections
- **gras** pour les points importants
- Listes à puces quand pertinent
- Paragraphes courts et aérés

CONTEXTE:
Tu écris pour des professionnels de santé (secrétaires médicales, médecins, responsables de cabinets) qui cherchent des solutions pratiques pour améliorer leur organisation.

SEO:
- Intègre naturellement les mots-clés suivants quand c'est pertinent (sans sur-optimisation) : {keywords_snippet}."""

    plan_str = "\n".join(f"- {p}" for p in outline) if outline else ""

    user_prompt = f"""Titre de l'article: {title}

Angle éditorial à adopter:
{angle}

Plan (structure principale à respecter, tu peux détailler mais pas changer l'intention des points) :
{plan_str}

Données de recherche web récentes (utiliser comme source d'informations, sans copier/coller brut) :
{web_results[:3000] if web_results else "Aucune donnée spécifique fournie. Utilise tes connaissances actuelles."}

IMPORTANT:
- Écris un article complet de minimum 1200 mots
- Utilise le plan fourni comme colonne vertébrale de l'article
- Structure avec des points numérotés clairs (1., 2., 3.) pour les sections principales uniquement
- Évite les numéros dans les sous-titres
- Style professionnel mais accessible
- Mentionne Donna UNIQUEMENT si l'article traite spécifiquement de l'IA vocale dans le secrétariat médical
- Si l'article parle d'un autre secteur (immobilier, copropriété, etc.) ou d'un sujet non lié à l'IA vocale médicale, NE PAS mentionner Donna du tout
- INTERDICTION ABSOLUE : Ne jamais citer de concurrents ou d'autres entreprises. Utilise des formulations génériques.
- Termine par une conclusion qui résume les points clés
- Si et SEULEMENT SI pertinent (IA vocale + secrétariat médical), termine par un appel à découvrir Donna avec le lien https://callrounded.com/cas-usage/secretariat-medical
- Si le sujet n'est PAS en rapport avec l'IA vocale pour secrétariat médical, NE PAS ajouter de lien vers Donna dans la conclusion

Génère l'article maintenant."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=4000,
        )
        
        # Tracker les tokens
        if hasattr(response, 'usage') and response.usage:
            try:
                from utils.token_tracker import track_openai_usage
                variant_title = variant.get("title", "")
                track_openai_usage(
                    operation="generate_article",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    article_title=variant_title
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens: {e}")
        
        article = response.choices[0].message.content
        print("✅ Article complet généré")
        return article
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        raise


def apply_style_refinement(article: str) -> str:
    """
    Applique un raffinement de style à l'article généré.

    Objectif :
    - Donner du "grain" au texte
    - Rendre la lecture plus rythmée et concrète
    """
    if not openai_client:
        # Si pas de client OpenAI, on renvoie l'article tel quel
        return article

    style_prompt = """
Tu es un rédacteur senior B2B français, ton de marque Rounded : expert, direct, un peu mordant mais jamais vulgaire.

Tu reçois ci-dessous un article déjà structuré (H2/H3, paragraphes, listes). 
Ta mission : RÉÉCRIRE l’article COMPLET en respectant ces règles :

1) Structure des phrases
- Varie la ponctuation : points, virgules, deux-points, points-virgules, parenthèses (avec modération).
- Évite les phrases trop longues : idéalement 12–22 mots, rarement plus de 30.
- Commence autant que possible chaque phrase par l’idée clé (thèse), puis 
  seulement ensuite l’explication, puis un exemple, un chiffre ou une mini-citation.

2) Ton & voix
- Garde un ton professionnel, clair, orienté business.
- Autorisé : un peu de sarcasme / ironie légère pour pointer les absurdités du réel 
  (par ex. “évidemment, personne n’a jamais eu un appel perdu un lundi matin…”).
- 1 à 3 blagues maxi sur tout l’article, subtiles, jamais lourdes, jamais sur les patients.

3) Progression & transitions
- Ajoute UNE courte phrase de transition entre chaque H2 pour faire le lien logique
  (ex : “Avant de parler coûts, regardons d’abord ce qui coince au quotidien.”).
- Les transitions doivent être naturelles et orienter la suite de la lecture.

4) Anecdotes & concret
- Quand c’est pertinent, ajoute de petites anecdotes réalistes (2–3 phrases) :
  - situations de secrétariat médical
  - appels ratés, débordement, patients frustrés, médecins débordés, etc.
- Ces anecdotes doivent rester crédibles, pas romancées.

5) Sources & chiffres clés
- Si l’article contient déjà des chiffres, études, pourcentages : 
  - mets-les davantage en valeur (formulations percutantes, “En clair…”, “Concrètement…”).
- Si tu vois passer des noms d’études, organismes, sources : 
  - reformule en une phrase qui donne du contexte (“Une étude de [organisme] montre que…”).
- NE PAS inventer de chiffres qui ne sont pas déjà présents dans le texte.

6) Mise en forme
- Garde STRICTEMENT la structure H2/H3 / listes.
- Ne change pas le sens business général ni les messages clés.
- Ne rajoute PAS de nouveaux liens vers Donna ou Rounded au-delà de ce qui est prévu
  dans la version originale.

Retourne UNIQUEMENT l’article réécrit, au format Markdown, sans commentaire autour.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": style_prompt},
                {
                    "role": "user",
                    "content": (
                        "Voici l'article à réécrire en appliquant STRICTEMENT les règles ci-dessus :\n\n"
                        f"{article}"
                    ),
                },
            ],
            temperature=0.8,
            max_tokens=4000,
        )

        styled_article = response.choices[0].message.content

        # Tracking tokens pour la passe de style
        if hasattr(response, "usage") and response.usage:
            try:
                from utils.token_tracker import track_openai_usage

                track_openai_usage(
                    operation="style_refinement",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens (style_refinement): {e}")

        return styled_article or article

    except Exception as e:
        print(f"⚠️  Erreur apply_style_refinement: {e}")
        # En cas de problème, on ne bloque pas : on garde l'article brut
        return article


def score_article_quality(article: str, topic: str, target_keywords: Optional[List[str]] = None, article_title: Optional[str] = None) -> Dict[str, Any]:
    """
    Évalue l'article et retourne un rapport de scoring (éditorial + SEO) au format structuré.

    Retour :
    {
        "global_score": int | None,
        "content_score": int | None,
        "readability_score": int | None,
        "seo_score": int | None,
        "conversion_score": int | None,
        "credibility_score": int | None,
        "markdown": str  # rapport complet en Markdown (style exemple utilisateur)
    }
    """
    if not openai_client:
        return {
            "global_score": None,
            "content_score": None,
            "readability_score": None,
            "seo_score": None,
            "conversion_score": None,
            "credibility_score": None,
            "markdown": "",
        }

    keywords_str = ", ".join(target_keywords or []) if target_keywords else ""

    scoring_system_prompt = """
Tu es un expert en évaluation de contenu éditorial et SEO pour des articles de blog B2B.

Ta mission : analyser CHAQUE article de manière INDIVIDUELLE et donner un scoring UNIQUE 
basé sur les caractéristiques RÉELLES de cet article spécifique.

IMPORTANT : 
- Chaque article doit avoir un scoring DIFFÉRENT selon son contenu réel
- Analyse en profondeur : longueur, structure, qualité des arguments, présence de chiffres, 
  anecdotes, transitions, CTA, FAQ, etc.
- Sois STRICT et VARIÉ dans tes scores : ne donne pas toujours les mêmes notes
- Un article avec beaucoup de chiffres et d'exemples concrets aura un meilleur score contenu
- Un article avec une FAQ et plusieurs CTA aura un meilleur score conversion
- Un article avec des phrases courtes et bien structurées aura un meilleur score lisibilité
- Adapte tes scores à la RÉALITÉ de l'article, pas à un standard générique
"""

    article_title_context = f"\n- Titre de l'article : {article_title}" if article_title else ""
    
    scoring_user_prompt = f"""
CONTEXTE :
- Sujet de l'article : {topic}
- Mots-clés ciblés : {keywords_str if keywords_str else "non précisés"}{article_title_context}

ARTICLE À ÉVALUER (analyse-le en profondeur, caractère par caractère) :
---
{article}
---

INSTRUCTIONS D'ÉVALUATION :

1. ANALYSE APPROFONDIE :
   - Compte réellement les mots, phrases, paragraphes
   - Identifie les chiffres, statistiques, exemples concrets
   - Repère les CTA, FAQ, transitions, anecdotes
   - Évalue la structure H2/H3, listes, formatage
   - Mesure la longueur réelle des phrases
   - Vérifie la présence et répétition des mots-clés

2. SCORING PERSONNALISÉ (sur 100 pour le global, sur 20 pour chaque dimension) :
   - Score global : basé sur la moyenne pondérée des dimensions
   - Qualité du contenu (0-20) : arguments solides, exemples concrets, chiffres, profondeur
   - Lisibilité & clarté (0-20) : phrases courtes, structure claire, vocabulaire adapté
   - SEO (0-30) : mots-clés présents, répétition stratégique, structure H2/H3, méta
   - Conversion & marketing (0-20) : CTA présents, FAQ, appels à l'action, bénéfices clairs
   - Crédibilité secteur santé (0-10) : ton respectueux, pas de promesses irréalistes

3. VARIATION DES SCORES :
   - Si l'article est court (< 800 mots) : pénalise le score contenu
   - Si l'article n'a pas de FAQ : pénalise le score conversion
   - Si les phrases sont très longues (> 30 mots) : pénalise la lisibilité
   - Si les mots-clés sont absents : pénalise fortement le SEO
   - Si l'article a beaucoup de chiffres et d'exemples : bon score contenu
   - ADAPTE les scores à la RÉALITÉ de cet article spécifique

4. RAPPORT DÉTAILLÉ :
   - Commence par le score global avec un commentaire personnalisé
   - Détaille chaque dimension avec des exemples CONCRETS tirés de l'article
   - Liste les points forts RÉELS de cet article
   - Liste les points faibles RÉELS de cet article
   - Propose 5 actions PRIORITAIRES pour améliorer CET article spécifique
   - Inclus un tableau "Score par type d'outil simulé" (SEO Review Tools, Hemingway, etc.)

FORMAT DU RAPPORT :
- Style professionnel avec emojis (📊, ✍️, 📖, 🔍, 🎯, 🏥)
- Titres clairs : "Score global", "Détail du scoring", "5 actions pour passer à 90+"
- Tableaux pour les scores par outil
- Listes à puces pour les recommandations
- En français, ton expert mais accessible

IMPORTANT - FORMAT JSON STRICT :
{{
  "global_score": <score entre 50 et 95, VARIÉ selon l'article>,
  "content_score": <score entre 10 et 20>,
  "readability_score": <score entre 10 et 20>,
  "seo_score": <score entre 15 et 30>,
  "conversion_score": <score entre 8 et 20>,
  "credibility_score": <score entre 8 et 10>,
  "markdown_report": "<rapport complet en Markdown, très détaillé et personnalisé pour CET article>"
}}

Ne renvoie QUE le JSON, sans texte autour.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": scoring_system_prompt},
                {"role": "user", "content": scoring_user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=2000,
        )

        data = json.loads(response.choices[0].message.content)

        result = {
            "global_score": data.get("global_score"),
            "content_score": data.get("content_score"),
            "readability_score": data.get("readability_score"),
            "seo_score": data.get("seo_score"),
            "conversion_score": data.get("conversion_score"),
            "credibility_score": data.get("credibility_score"),
            "markdown": data.get("markdown_report", ""),
        }

        # Tracking tokens
        if hasattr(response, "usage") and response.usage:
            try:
                from utils.token_tracker import track_openai_usage

                track_openai_usage(
                    operation="score_article",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                    topic=topic,
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens (score_article): {e}")

        return result

    except Exception as e:
        print(f"⚠️  Erreur score_article_quality: {e}")
        return {
            "global_score": None,
            "content_score": None,
            "readability_score": None,
            "seo_score": None,
            "conversion_score": None,
            "credibility_score": None,
            "markdown": "",
        }


def regenerate_article_with_scoring(
    article: str,
    scoring_markdown: str,
    topic: str,
    target_keywords: Optional[List[str]] = None,
    max_iterations: int = 3,
) -> str:
    """
    Régénère l'article en s'appuyant sur le scoring et les recommandations.

    - Objectif : passer d'un bon article à un article optimisé (90+ / 100).
    - Ne doit PAS changer le message de fond, mais améliorer :
      structure, SEO, conversion, clarté, impact.
    """
    if not openai_client:
        return article

    keywords_str = ", ".join(target_keywords or []) if target_keywords else ""

    system_prompt = """
Tu es un expert en copywriting B2B et SEO pour le secteur médical, travaillant pour Rounded.

Ta mission CRITIQUE : améliorer l'article en appliquant TOUTES les recommandations du scoring.

RÈGLES STRICTES :
1. L'article amélioré DOIT avoir un meilleur score que l'article initial
2. Applique TOUTES les recommandations du rapport de scoring :
   - Si le rapport dit "ajouter une FAQ" → AJOUTE une FAQ complète MAIS PLACE-LA À LA FIN, juste avant la conclusion
   - Si le rapport dit "renforcer les CTA" → AJOUTE des CTA clairs et visibles (mais pas en plein milieu du contenu)
   - Si le rapport dit "raccourcir les phrases" → RACCOURCIS les phrases longues
   - Si le rapport dit "répéter le mot-clé" → RÉPÈTE le mot-clé stratégiquement
   - Si le rapport dit "améliorer la conversion" → AJOUTE des appels à l'action en fin de sections pertinentes
3. STRUCTURE OBLIGATOIRE :
   - Introduction
   - Sections H2 principales (contenu de l'article)
   - FAQ (si recommandée) → TOUJOURS à la fin, juste avant la conclusion
   - Conclusion
4. Garde le même angle, la même cible et les mêmes messages business
5. Garde la structure générale (H2/H3, listes) mais améliore-la selon les recommandations
6. N'invente PAS de nouveaux chiffres précis si aucun chiffre n'était présent
7. Ne rajoute PAS de nouveaux liens externes non mentionnés dans l'article initial
8. NE PLACE JAMAIS la FAQ en plein milieu de l'article - elle doit être à la fin, juste avant la conclusion

OBJECTIF : L'article final DOIT être meilleur que l'initial sur TOUS les critères mentionnés dans le scoring, avec une structure propre et professionnelle.

Format attendu :
- Retourne UNIQUEMENT l'article réécrit et amélioré, en Markdown propre.
"""

    user_prompt = f"""
Contexte :
- Sujet : {topic}
- Mots-clés cibles indicatifs : {keywords_str}

ARTICLE INITIAL :
---
{article}
---

RAPPORT DE SCORING & RECOMMANDATIONS :
---
{scoring_markdown}
---

Maintenant, réécris l'article COMPLET en appliquant les recommandations.

STRUCTURE FINALE OBLIGATOIRE :
1. Introduction
2. Sections H2 principales (contenu de l'article)
3. FAQ (si recommandée dans le scoring) → PLACER ICI, juste avant la conclusion, JAMAIS en plein milieu
4. Conclusion

IMPORTANT : Si tu ajoutes une FAQ, elle DOIT être placée à la fin de l'article, juste avant la conclusion. 
NE PLACE JAMAIS la FAQ en plein milieu du contenu - cela casse la structure et n'est pas professionnel.

Retourne UNIQUEMENT l'article réécrit en Markdown, sans commentaire autour.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        improved_article = response.choices[0].message.content

        # Tracking tokens
        if hasattr(response, "usage") and response.usage:
            try:
                from utils.token_tracker import track_openai_usage

                track_openai_usage(
                    operation="regenerate_with_scoring",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                    topic=topic,
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens (regenerate_with_scoring): {e}")

        return improved_article or article

    except Exception as e:
        print(f"⚠️  Erreur regenerate_article_with_scoring: {e}")
    return article


def load_target_keywords() -> List[str]:
    """Charge les mots-clés cibles depuis data/keywords.json (si présent)"""
    json_path = Path("data/keywords.json")
    try:
        if not json_path.exists():
            return []
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Accepte soit une simple liste, soit un dict avec une clé "default"
        if isinstance(data, list):
            keywords = data
        elif isinstance(data, dict):
            # On prend "default" si présent, sinon le premier ensemble trouvé
            if "default" in data and isinstance(data["default"], list):
                keywords = data["default"]
            else:
                first = next((v for v in data.values() if isinstance(v, list)), [])
                keywords = first
        else:
            return []
        # Nettoyage simple
        return [str(k).strip() for k in keywords if str(k).strip()]
    except Exception as e:
        print(f"⚠️  Erreur chargement des mots-clés (data/keywords.json): {e}")
        return []


def select_target_keywords(topic: str, all_keywords: List[str], min_k: int = 2, max_k: int = 4) -> List[str]:
    """
    Sélectionne entre 2 et 4 mots-clés pertinents en fonction du sujet.

    Logique simple :
    - On score chaque mot-clé selon son recouvrement avec les mots du sujet
    - On prend les meilleurs scores en priorité
    - On garantit au moins min_k mots-clés (en complétant si besoin)
    """
    if not topic or not all_keywords:
        return all_keywords[:max_k]

    topic_lower = topic.lower()
    # Découper le sujet en mots significatifs
    topic_words = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9]+", topic_lower)
    topic_words_set = set(topic_words)

    scored: List[Tuple[int, str]] = []
    for kw in all_keywords:
        kw_lower = kw.lower()
        kw_words = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9]+", kw_lower)
        kw_words_set = set(kw_words)

        # Score = nombre de mots en commun + bonus si le mot-clé est un substring du sujet
        common_words = topic_words_set.intersection(kw_words_set)
        score = len(common_words)
        if kw_lower in topic_lower or any(w in topic_lower for w in kw_words_set):
            score += 1

        scored.append((score, kw))

    # Trier par score décroissant
    scored.sort(key=lambda x: x[0], reverse=True)

    # Garder uniquement les mots-clés avec un score > 0 en priorité
    positive = [kw for score, kw in scored if score > 0]

    selected: List[str] = []
    for kw in positive:
        if kw not in selected:
            selected.append(kw)
        if len(selected) >= max_k:
            break

    # Si on n'a pas assez de mots-clés, compléter avec les autres (sans doublon)
    if len(selected) < min_k:
        for _score, kw in scored:
            if kw not in selected:
                selected.append(kw)
            if len(selected) >= min_k:
                break

    return selected[:max_k]


def optimize_seo(article: str, target_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Optimise SEO et retourne les métadonnées complètes"""
    if not openai_client:
        # Fallback simple
        slug = article[:50].lower().replace(' ', '-').replace("'", '').replace(",", '').replace("?", '').replace(".", '')
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        title = article.split('\n')[0].replace('#', '').strip()[:60]
        summary = article[:155]
        return {
            "title": title,
            "summary": summary,
            "blog_post": article,
            "slug": slug,
            "readTime": "5 min",
            "tag": "actualites-tendances",
            "keywords": target_keywords or [],
            "metaTitle": title[:60],
            "metaDescription": summary[:160],
            "ogTitle": title,
            "ogDescription": summary[:160],
            "canonicalUrl": f"https://callrounded.com/blog/{slug}",
            "translationGroup": slug
        }
    
    print("🔍 Optimisation SEO...")
    
    system_prompt = """You are an expert SEO copywriter. Analyze the article and return JSON with ALL these fields:
- title: SEO-optimized title (max 65 chars, include main keyword)
- summary: Meta description for excerpt (155-160 chars, compelling)
- blog_post: Full HTML content with proper tags (<h2>, <h3>, <p>, <ul>, <li>, <strong>)
- slug: URL-friendly slug (lowercase, hyphens, no special chars)
- readTime: Reading time estimation (e.g., "5 min", "8 min")
- tag: Category from: actualites-tendances, guides-pratiques
- keywords: Array of 5-8 relevant keywords
- focusKeyword: Main keyword (1-2 words)
- metaTitle: SEO title for meta tag (50-60 chars)
- metaDescription: SEO meta description (155-160 chars)
- ogTitle: Open Graph title (can be same as title or slightly different)
- ogDescription: Open Graph description (155-160 chars)
- canonicalUrl: Full canonical URL (https://callrounded.com/blog/{slug})
- translationGroup: Translation group ID (same as slug)

Convert Markdown to HTML:
- # Title → <h2>Title</h2>
- ## Subtitle → <h3>Subtitle</h3>
- **bold** → <strong>bold</strong>
- * item → <ul><li>item</li></ul>
- Regular text → <p>text</p>"""
    # Si des mots-clés cibles existent, on les ajoute explicitement au prompt SEO
    if target_keywords:
        joined = ", ".join(target_keywords)
        system_prompt += f"\n\nIMPORTANT:\n- You MUST prioritize and naturally include the following SEO keywords when relevant: {joined}.\n- Return them in the 'keywords' array field (add more if useful, but always keep these)."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": article}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Tracker les tokens
        if hasattr(response, 'usage') and response.usage:
            try:
                from utils.token_tracker import track_openai_usage
                track_openai_usage(
                    operation="optimize_seo",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    article_title=result.get("title", "") if 'result' in locals() else None
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens: {e}")
        
        result = json.loads(response.choices[0].message.content)
        
        # Nettoyer les titres pour enlever les caractères problématiques
        title = result.get("title", "").strip()
        title = title.replace('\n', ' ').replace('\r', ' ')
        title = re.sub(r'\s+', ' ', title)
        result["title"] = title
        
        # S'assurer que tous les champs sont présents
        slug = result.get("slug", article[:50].lower().replace(' ', '-'))
        
        meta_title = result.get("metaTitle", title)[:60].strip()
        meta_title = meta_title.replace('\n', ' ').replace('\r', ' ')
        meta_title = re.sub(r'\s+', ' ', meta_title)
        result["metaTitle"] = meta_title
        
        og_title = result.get("ogTitle", title).strip()
        og_title = og_title.replace('\n', ' ').replace('\r', ' ')
        og_title = re.sub(r'\s+', ' ', og_title)
        result["ogTitle"] = og_title
        
        result.setdefault("metaDescription", result.get("summary", "")[:160].strip())
        result.setdefault("ogDescription", result.get("summary", "")[:160].strip())
        result.setdefault("canonicalUrl", f"https://callrounded.com/blog/{slug}")
        result.setdefault("translationGroup", slug)
        # Si l'IA ne renvoie pas de keywords, on prend ceux du fichier
        if "keywords" not in result or not isinstance(result["keywords"], list):
            result["keywords"] = target_keywords or []
        
        print("✅ SEO optimisé")
        return result
    except Exception as e:
        print(f"⚠️  Erreur SEO: {e}")
        # Fallback
        slug = article[:50].lower().replace(' ', '-').replace("'", '').replace(",", '').replace("?", '').replace(".", '')
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        title = article.split('\n')[0].replace('#', '').strip()[:60]
        summary = article[:155]
        return {
            "title": title,
            "summary": summary,
            "blog_post": article,
            "slug": slug,
            "readTime": "5 min",
            "tag": "actualites-tendances",
            "keywords": target_keywords or [],
            "metaTitle": title[:60],
            "metaDescription": summary[:160],
            "ogTitle": title,
            "ogDescription": summary[:160],
            "canonicalUrl": f"https://callrounded.com/blog/{slug}",
            "translationGroup": slug
        }


def save_article_for_review(article_data: Dict[str, Any], topic: str, english_data: Dict[str, Any] = None, custom_filename: str = None) -> Path:
    """Sauvegarde l'article dans un fichier pour review au format blog Rounded (FR + EN)."""
    if custom_filename:
        filename = custom_filename
        filepath = ARTICLES_DIR / filename
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = article_data.get("slug", "article")
        filename = f"{timestamp}_{slug}.md"
        filepath = ARTICLES_DIR / filename
    
    # Préparer les contenus FR
    title_fr = article_data.get("title", "Article")
    slug_fr = article_data.get("slug", "article")
    tag_fr = article_data.get("tag", "guides-pratiques")
    read_time = article_data.get("readTime", "N/A")
    focus_kw = article_data.get("focusKeyword", "N/A")
    summary_fr = article_data.get("summary", "")
    keywords = article_data.get("keywords", [])
    html_fr = article_data.get("blog_post", article_data.get("original_content", ""))
    markdown_fr = article_data.get("original_content", "")

    # Date de publication souhaitée : veille (J-1)
    published_date = datetime.now() - timedelta(days=1)

    # En-tête au format "blog Rounded" (comme l'exemple 20251211_135947...)
    content = f"""# {title_fr}

**Sujet original:** {topic}  
**Slug:** {slug_fr}  
**Catégorie:** {tag_fr}  
**Temps de lecture:** {read_time}  
**Focus Keyword:** {focus_kw}  
**Généré le:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

---

## Résumé SEO

{summary_fr}

---

## Mots-clés

{', '.join(keywords)}

---

## Contenu HTML (pour Sanity)

{html_fr}

---

## Contenu Markdown (version originale)

{markdown_fr}
"""

    # Ajouter une section EN après pour référence (optionnelle)
    if english_data:
        title_en = english_data.get("title", "")
        slug_en = english_data.get("slug", "")
        summary_en = english_data.get("summary", "")
        html_en = english_data.get("blog_post", english_data.get("original_content", ""))
        markdown_en = english_data.get("original_content", html_en)

        content += f"""
---

## Version ANGLAISE

### Title
{title_en}

### Slug
{slug_en}

### Résumé SEO (EN)

{summary_en}

### Contenu HTML EN (pour Sanity)

{html_en}

### Contenu Markdown EN (version originale)

{markdown_en}
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
    print(f"📝 Résumé SEO:")
    print(f"   {article_data.get('summary', 'N/A')}")
    print()
    print("─" * 70)
    print("PREVIEW DU CONTENU (premiers 1000 caractères):")
    print("─" * 70)
    content = article_data.get('blog_post', '')
    # Nettoyer HTML pour preview
    preview = content.replace('<p>', '').replace('</p>', '\n\n')
    preview = preview.replace('<h2>', '\n## ').replace('</h2>', '\n\n')
    preview = preview.replace('<h3>', '\n### ').replace('</h3>', '\n\n')
    preview = preview.replace('<ul>', '').replace('</ul>', '')
    preview = preview.replace('<li>', '• ').replace('</li>', '\n')
    preview = preview.replace('<strong>', '**').replace('</strong>', '**')
    preview = re.sub(r'<[^>]+>', '', preview)  # Enlever les autres balises HTML
    preview = preview[:1000] + "..." if len(preview) > 1000 else preview
    print(preview)
    print("─" * 70)
    print()
    print(f"💾 Article sauvegardé dans : {filepath}")
    print(f"   Ouvrez ce fichier pour lire l'article complet")
    print()
    print("─" * 70)
    print()


def ask_validation() -> bool:
    """Demande validation à l'utilisateur"""
    print("❓ Voulez-vous publier cet article en PRODUCTION ?")
    print("   - Tapez 'o' pour publier")
    print("   - Tapez 'n' pour annuler")
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


def add_article_to_knowledge_base(title: str, slug: str, date: str = None):
    """Ajoute un article à la base de connaissances pour éviter les doublons"""
    json_path = Path("data/articles_existants.json")
    
    try:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            articles = []
        
        # Vérifier si l'article existe déjà
        existing = any(art.get("titre") == title or art.get("slug") == slug for art in articles)
        if not existing:
            articles.append({
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "auteur": "Matthieu HUBERT",
                "titre": title,
                "slug": slug,
                "description": ""
            })
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Article ajouté à la base de connaissances")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout à la base: {e}")


def extract_title_from_markdown(content: str) -> str:
    """Extrait le titre depuis le contenu markdown (première ligne avec #)"""
    if not content:
        return ""
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            # Titre principal (H1)
            title = line[2:].strip()  # Enlever "# "
            return title
        elif line.startswith('## '):
            # Titre secondaire (H2) - utiliser si pas de H1
            if not any(l.strip().startswith('# ') for l in lines[:lines.index(line)]):
                title = line[3:].strip()  # Enlever "## "
                return title
    
    # Fallback : première ligne non vide
    for line in lines:
        if line.strip():
            return line.strip()
    
    return ""


def generate_english_version(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Génère une version anglaise de l'article"""
    if not openai_client:
        return None
    
    print("🌐 Génération de la version anglaise...")
    
    original_content = article_data.get("original_content", article_data.get("blog_post", ""))
    
    system_prompt = """You are a professional translator specializing in medical and healthcare technology content.

Translate the French article to English while:
- Maintaining the same structure and style
- Keeping the same tone (professional but accessible)
- Preserving all technical terms appropriately
- Keeping mentions of "Donna" and links to https://callrounded.com/cas-usage/secretariat-medical
- Maintaining the same formatting (headings, lists, paragraphs)
- Keeping the same length and depth

Return the translated article in the same format (Markdown with headings, paragraphs, lists)."""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this French article to English:\n\n{original_content}"}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Tracker les tokens
        if hasattr(response, 'usage') and response.usage:
            try:
                from utils.token_tracker import track_openai_usage
                track_openai_usage(
                    operation="translate_article",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    article_title=article_data.get("title", "")
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens: {e}")
        
        english_content = response.choices[0].message.content
        
        # Extraire le titre depuis le contenu markdown si l'IA ne le fournit pas correctement
        extracted_title = extract_title_from_markdown(english_content)
        
        # Générer les métadonnées SEO en anglais
        seo_prompt = """You are an expert SEO copywriter. Based on the English article, return JSON with:
- title: SEO-optimized title in English (max 65 chars)
- summary: Meta description in English (155-160 chars)
- slug: URL-friendly slug in English (lowercase, hyphens)
- metaTitle: SEO title (50-60 chars)
- metaDescription: SEO meta description (155-160 chars)
- ogTitle: Open Graph title
- ogDescription: Open Graph description (155-160 chars)
- canonicalUrl: Full canonical URL (https://callrounded.com/blog/{slug}-en)"""
        
        seo_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": seo_prompt},
                {"role": "user", "content": english_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Tracker les tokens
        if hasattr(seo_response, 'usage') and seo_response.usage:
            try:
                from utils.token_tracker import track_openai_usage
                track_openai_usage(
                    operation="optimize_seo",
                    model="gpt-4o-mini",
                    usage={
                        "prompt_tokens": seo_response.usage.prompt_tokens,
                        "completion_tokens": seo_response.usage.completion_tokens,
                        "total_tokens": seo_response.usage.total_tokens
                    },
                    article_title=article_data.get("title", "")
                )
            except Exception as e:
                print(f"⚠️  Erreur tracking tokens: {e}")
        
        english_seo = json.loads(seo_response.choices[0].message.content)
        
        # Nettoyer le titre pour enlever les caractères problématiques
        # Utiliser le titre extrait du markdown si le titre SEO est vide ou problématique
        title = english_seo.get("title", extracted_title).strip()
        if not title or len(title) < 5:
            title = extracted_title
        
        # Garder les caractères normaux mais s'assurer qu'il n'y a pas de problèmes d'encodage
        title = title.replace('\n', ' ').replace('\r', ' ')
        # Nettoyer les espaces multiples
        title = re.sub(r'\s+', ' ', title)
        # S'assurer que le titre ne dépasse pas 100 caractères (limite raisonnable)
        if len(title) > 100:
            title = title[:97] + "..."
        
        meta_title = english_seo.get("metaTitle", title).strip()[:60]
        meta_title = meta_title.replace('\n', ' ').replace('\r', ' ')
        meta_title = re.sub(r'\s+', ' ', meta_title)
        
        og_title = english_seo.get("ogTitle", title).strip()
        og_title = og_title.replace('\n', ' ').replace('\r', ' ')
        og_title = re.sub(r'\s+', ' ', og_title)
        
        return {
            "original_content": english_content,
            "blog_post": english_content,  # Plain text pour Sanity
            "title": title,
            "summary": english_seo.get("summary", "").strip(),
            "slug": english_seo.get("slug", article_data.get("slug", "") + "-en"),
            "metaTitle": meta_title,
            "metaDescription": english_seo.get("metaDescription", "")[:160].strip(),
            "ogTitle": og_title,
            "ogDescription": english_seo.get("ogDescription", "")[:160].strip(),
            "canonicalUrl": english_seo.get("canonicalUrl", f"https://callrounded.com/blog/{english_seo.get('slug', '')}"),
            "translationGroup": article_data.get("translationGroup", ""),  # Même Translation Group
            "language": "en"
        }
    except Exception as e:
        print(f"⚠️  Erreur génération version anglaise: {e}")
        return None


def convert_html_to_plain_text(html_content: str) -> str:
    """Convertit le HTML en texte brut pour l'éditeur Sanity"""
    # Nettoyer le HTML et convertir en texte simple
    text = html_content
    
    # Remplacer les balises par des sauts de ligne ou rien
    text = re.sub(r'<h2[^>]*>', '\n\n', text)  # H2 → double saut
    text = re.sub(r'</h2>', '\n', text)
    text = re.sub(r'<h3[^>]*>', '\n\n', text)  # H3 → double saut
    text = re.sub(r'</h3>', '\n', text)
    text = re.sub(r'<p[^>]*>', '\n', text)     # P → saut
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<ul[^>]*>', '\n', text)    # UL → saut
    text = re.sub(r'</ul>', '\n', text)
    text = re.sub(r'<li[^>]*>', '\n• ', text)  # LI → puce
    text = re.sub(r'</li>', '', text)
    text = re.sub(r'<strong[^>]*>', '**', text)  # Strong → markdown bold
    text = re.sub(r'</strong>', '**', text)
    
    # Enlever toutes les autres balises HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Nettoyer les espaces multiples et sauts de ligne
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 sauts consécutifs
    text = re.sub(r'[ \t]+', ' ', text)     # Espaces multiples → 1 espace
    text = text.strip()
    
    return text


def publish_to_production(article_data: Dict[str, Any], references: Dict[str, str], language: str = "fr") -> bool:
    """Publie directement en PRODUCTION avec tous les champs Sanity"""
    if not SANITY_TOKEN:
        print("❌ SANITY_TOKEN manquant dans .env")
        return False
    
    print("\n🚀 Publication en PRODUCTION...")
    
    slug = article_data.get("slug", "")
    base_id = slug.replace("-", "_") if slug else str(uuid.uuid4())[:8]
    document_id = base_id  # SANS préfixe drafts. = PRODUCTION
    
    # Convertir le contenu en format Block Content Sanity
    # On privilégie le HTML optimisé renvoyé par l'étape SEO,
    # puis on le convertit en blocks Sanity avec html_to_sanity_blocks
    content = article_data.get("blog_post", "")
    body_blocks = None

    if content and "<" in content and ">" in content:
        try:
            body_blocks = html_to_sanity_blocks(content)
        except Exception as e:
            print(f"⚠️  Erreur conversion HTML -> Block Content (html_to_sanity_blocks): {e}")
    
    if body_blocks is None:
        # Fallback : utiliser le contenu original en texte (Markdown-like)
        body_text = article_data.get("original_content", content)
        try:
            body_blocks = convert_text_to_sanity_blocks(body_text)
        except Exception as e:
            print(f"⚠️  Erreur conversion Block Content: {e}")
            # Fallback: bloc simple
            body_blocks = [{
                "_key": generate_key(),
                "_type": "block",
                "style": "normal",
                "children": [{"_key": generate_key(), "_type": "span", "text": body_text[:500], "marks": []}],
                "markDefs": []
            }]
    
    # Construire le document Sanity complet
    # Date de publication dans Sanity : veille (J-1)
    published_date = datetime.now() - timedelta(days=1)
    
    # Nettoyer le titre pour éviter les problèmes avec les caractères spéciaux
    title = article_data.get("title", "").strip()
    title = title.replace('\n', ' ').replace('\r', ' ')
    title = re.sub(r'\s+', ' ', title)
    
    meta_title = article_data.get("metaTitle", title)[:60].strip()
    meta_title = meta_title.replace('\n', ' ').replace('\r', ' ')
    meta_title = re.sub(r'\s+', ' ', meta_title)
    
    post_data = {
        "_id": document_id,
        "_type": "post",
        "title": title,
        "slug": {
            "_type": "slug",
            "current": slug
        },
        "excerpt": article_data.get("summary", "").strip(),
        "body": body_blocks,  # Format Block Content Sanity
        "publishedAt": published_date.isoformat(),
        
        # Métadonnées SEO
        "metaTitle": meta_title,
        "metaDescription": article_data.get("metaDescription", article_data.get("summary", ""))[:160].strip(),
        
        # Canonical URL
        "canonicalUrl": article_data.get("canonicalUrl", f"https://callrounded.com/blog/{slug}"),
        
        # Translation Group
        "translationGroup": article_data.get("translationGroup", slug),
        
        # Language
        "language": language
    }
    
    # Open Graph et Robots - commentés car pas dans le schéma
    # Si votre schéma les accepte, décommentez :
    # "ogTitle": article_data.get("ogTitle", article_data.get("title", "")),
    # "ogDescription": article_data.get("ogDescription", article_data.get("summary", ""))[:160],
    # "ogType": "article",
    # "robots": {
    #     "noindex": False,
    #     "nofollow": False
    # }
    
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
    
    # Main image (si disponible plus tard)
    # post_data["mainImage"] = {
    #     "_type": "image",
    #     "asset": {
    #         "_type": "reference",
    #         "_ref": image_asset_id
    #     },
    #     "alt": "Texte alternatif de l'image",
    #     "caption": "Légende de l'image"
    # }
    
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
            print(f"✅ Article publié en PRODUCTION ({language.upper()}) !")
            print(f"   ID: {document_id}")
            print(f"   Titre: {article_data.get('title', 'N/A')}")
            print(f"   Slug: {slug}")
            print(f"   Language: {language}")
            print(f"   Translation Group: {post_data.get('translationGroup', 'N/A')}")
            print(f"   Transaction: {result.get('transactionId', 'N/A')}")
            
            # Ajouter à la base de connaissances
            if language == "fr":
                add_article_to_knowledge_base(
                    article_data.get('title', ''),
                    slug,
                    datetime.now().strftime("%Y-%m-%d")
                )
            
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
    print("🤖 GÉNÉRATION D'ARTICLE AVEC VÉRIFICATION")
    print("=" * 70)
    print()
    
    # Récupérer le sujet et la variante éventuelle
    variant_arg = None
    topic = None
    
    if len(sys.argv) > 1:
        # Chercher --variant dans les arguments
        args = sys.argv[1:]
        if "--variant" in args:
            idx = args.index("--variant")
            if idx + 1 < len(args):
                variant_arg = args[idx + 1]
                args = args[:idx] + args[idx+2:]
            else:
                args = args[:idx]
        topic = " ".join(args) if args else None
    else:
        try:
            topic = input("📝 Entrez le sujet de l'article: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Annulé")
            sys.exit(1)
    
    if not topic:
        print("❌ Un sujet est requis")
        sys.exit(1)

    # Charger les mots-clés cibles (si disponibles)
    target_keywords = load_target_keywords()
    if target_keywords:
        print("✅ Mots-clés cibles chargés depuis data/keywords.json :")
        print("   " + ", ".join(target_keywords))
    else:
        print("ℹ️ Aucun mot-clé cible trouvé dans data/keywords.json (ou fichier vide) — l'IA choisira elle-même les keywords SEO.")
    
    # Charger les articles existants
    existing_articles = load_existing_articles()
    if existing_articles:
        print(f"✅ {len(existing_articles)} articles existants chargés depuis data/articles_existants.json")
    
    try:
        # 1. Vérifier les sujets existants (pour information / alerte doublons)
        print("\n📋 Étape 1/9: Vérification des sujets existants...")
        existing_topics = get_existing_blog_topics()
        if check_topic_exists(topic, existing_topics):
            print(f"\n⚠️  ATTENTION: Un article similaire existe déjà sur le blog.")
            print("   On va tout de même proposer de nouvelles idées de sujets/angles.\n")
        
        # 2. Recherche web globale sur le sujet
        print("\n🔍 Étape 2/9: Recherche web (Perplexity)...")
        search_query = f"Recherche des données récentes, études de cas, statistiques 2025 sur {topic}, agents vocaux IA, secrétariat médical, cabinets médicaux, automatisation téléphonique"
        web_results = search_web(search_query)
        
        # 3. Génération de 3 variantes de sujets (titre + angle + mini-plan)
        print("\n📝 Étape 3/9: Génération de 3 variantes de sujets (titre + mini-plan)...")
        topic_variants = generate_topic_variants(topic, existing_articles, target_keywords)
        
        print("\n" + "=" * 70)
        print("📋 PROPOSITIONS DE SUJETS - CHOISIS LA VARIANTE")
        print("=" * 70)
        print()
        for idx, v in enumerate(topic_variants, 1):
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📄 VARIANTE {idx}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📌 Titre :", v.get("title", "N/A"))
            print(f"🎯 Angle :", v.get("angle", "N/A"))
            outline = v.get("outline") or []
            if outline:
                print("🧱 Mini-plan :")
                for p in outline:
                    print(f"   - {p}")
            print()
        
        print("=" * 70)
        print()
        
        # 4. Demander de choisir la variante de sujet
        if variant_arg:
            try:
                chosen_num = int(variant_arg)
                if chosen_num not in [1, 2, 3]:
                    print(f"⚠️  Variante {variant_arg} invalide, utilisation de la variante 1 par défaut")
                    chosen_num = 1
            except ValueError:
                print(f"⚠️  Variante {variant_arg} invalide, utilisation de la variante 1 par défaut")
                chosen_num = 1
        else:
            try:
                choice = input("👉 Quelle variante de SUJET choisis-tu ? (1, 2 ou 3) [1]: ").strip()
                if not choice:
                    choice = "1"
                chosen_num = int(choice)
                if chosen_num not in [1, 2, 3]:
                    print("⚠️  Choix invalide, utilisation de la variante 1 par défaut")
                    chosen_num = 1
            except (ValueError, EOFError, KeyboardInterrupt):
                print("⚠️  Choix invalide ou annulé, utilisation de la variante 1 par défaut")
                chosen_num = 1
        
        chosen_variant = topic_variants[chosen_num - 1]
        print(f"\n✅ Variante de sujet {chosen_num} sélectionnée : {chosen_variant.get('title', 'N/A')}\n")
        
        # 5. Générer l'article complet pour la variante choisie
        print("📝 Étape 4/9: Génération de l'article complet...")
        raw_article = generate_article(chosen_variant, web_results, target_keywords)
        styled = apply_style_refinement(raw_article)
        print("✅ Article généré et stylisé\n")

        # 6. SEO pour l'article choisi
        print("🔍 Étape 5/9: Optimisation SEO...")
        article_data = optimize_seo(styled, target_keywords)
        article_data["original_content"] = styled
        print("✅ SEO optimisé\n")

        # 7. Générer version anglaise pour l'article choisi
        print("🌐 Étape 6/9: Génération de la version anglaise...")
        english_data = generate_english_version(article_data)
        if english_data:
            print("✅ Version anglaise générée\n")
        else:
            print("⚠️  Version anglaise non générée (sera créée lors de la publication)\n")
        
        # 8. Créer le fichier de review (FR + EN)
        print("💾 Étape 7/9: Création du fichier de review (FR + EN)...")
        final_filepath = save_article_for_review(article_data, chosen_variant.get("title", topic), english_data)
        print(f"✅ Fichier de review créé: {final_filepath.name}\n")
        
        # 9. Afficher résumé et demander validation
        print("👀 Étape 8/9: Review...")
        display_summary(article_data, final_filepath)
        
        validated = ask_validation()
        
        if validated:
            # 9. Récupérer références
            print("\n🔗 Étape 9/9: Récupération des références et publication...")
            category_slug = article_data.get("tag", "actualites-tendances")
            references = fetch_sanity_references(category_slug)
            print("✅ Références récupérées\n")
            
            # 10. Publication version FR en production
            print("📝 Publication version FRANÇAISE...")
            success_fr = publish_to_production(article_data, references, language="fr")
            
            if success_fr:
                # 11. Publier version anglaise si générée
                if english_data:
                    print("\n🌐 Publication version ANGLAISE...")
                    success_en = publish_to_production(english_data, references, language="en")
                    
                    if success_en:
                        print()
                        print("=" * 70)
                        print("✅ TERMINÉ - Articles publiés en production (FR + EN) !")
                        print("=" * 70)
                        print(f"\n💾 Le fichier de review reste disponible: {final_filepath}")
                        print(f"🔗 Translation Group: {article_data.get('translationGroup', 'N/A')}")
                    else:
                        print()
                        print("=" * 70)
                        print("⚠️  Version FR publiée, mais erreur sur version EN")
                        print("=" * 70)
                        print(f"\n💾 Le fichier de review reste disponible: {final_filepath}")
                else:
                    # Régénérer la version anglaise si elle n'a pas été générée avant
                    print("\n🌐 Génération et publication version ANGLAISE...")
                    english_data = generate_english_version(article_data)
                    
                    if english_data:
                        success_en = publish_to_production(english_data, references, language="en")
                        if success_en:
                            print()
                            print("=" * 70)
                            print("✅ TERMINÉ - Articles publiés en production (FR + EN) !")
                            print("=" * 70)
                        else:
                            print()
                            print("=" * 70)
                            print("⚠️  Version FR publiée, mais erreur sur version EN")
                            print("=" * 70)
                    else:
                        print()
                        print("=" * 70)
                        print("⚠️  Version FR publiée, mais génération EN échouée")
                        print("=" * 70)
                    print(f"\n💾 Le fichier de review reste disponible: {final_filepath}")
            else:
                print()
                print("=" * 70)
                print("❌ ERREUR lors de la publication FR")
                print("=" * 70)
                print(f"\n💾 Le fichier de review est disponible: {final_filepath}")
                sys.exit(1)
        else:
            print()
            print("=" * 70)
            print("⚠️  Publication annulée")
            print("=" * 70)
            print(f"\n💾 L'article reste sauvegardé dans: {final_filepath}")
            print("   Les 3 variantes sont disponibles dans le dossier articles/")
            print("   Vous pouvez le relancer plus tard si vous le souhaitez")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

