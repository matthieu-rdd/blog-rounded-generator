#!/usr/bin/env python3
"""
Analytics et reporting pour les articles générés
- Statistiques d'évolution des scores
- Tendances des coûts
- Taux de publication
- Temps de génération
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re

BASE_DIR = Path(__file__).parent.parent
ARTICLES_DIR = BASE_DIR / "articles"
TOKEN_HISTORY_FILE = BASE_DIR / "data" / "token_history.json"
ANALYTICS_FILE = BASE_DIR / "data" / "analytics.json"


def load_analytics_data() -> Dict[str, Any]:
    """Charge les données analytics"""
    if not ANALYTICS_FILE.exists():
        return {
            "articles": [],
            "scores_history": [],
            "costs_history": []
        }
    
    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Erreur chargement analytics: {e}")
        return {
            "articles": [],
            "scores_history": [],
            "costs_history": []
        }


def save_analytics_data(data: Dict[str, Any]):
    """Sauvegarde les données analytics"""
    try:
        ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde analytics: {e}")


def extract_article_metadata(article_file: Path) -> Optional[Dict[str, Any]]:
    """Extrait les métadonnées d'un article depuis le fichier"""
    try:
        content = article_file.read_text(encoding="utf-8")
        
        # Extraire le slug
        slug_match = re.search(r'\*\*Slug:\*\* (.+)', content)
        slug = slug_match.group(1).strip() if slug_match else None
        
        # Extraire la date
        date_match = re.search(r'\*\*Généré le:\*\* (.+)', content)
        date_str = date_match.group(1).strip() if date_match else None
        
        # Extraire le titre
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else article_file.stem
        
        # Compter les mots
        word_count = len(content.split())
        
        # Estimer le temps de lecture
        read_time = max(3, round(word_count / 200))
        
        return {
            "filename": article_file.name,
            "title": title,
            "slug": slug,
            "date": date_str,
            "word_count": word_count,
            "read_time": read_time,
            "file_size": article_file.stat().st_size,
            "created_at": datetime.fromtimestamp(article_file.stat().st_mtime).isoformat()
        }
    except Exception as e:
        print(f"⚠️  Erreur extraction métadonnées {article_file.name}: {e}")
        return None


def get_all_articles_metadata() -> List[Dict[str, Any]]:
    """Récupère les métadonnées de tous les articles"""
    if not ARTICLES_DIR.exists():
        return []
    
    articles = []
    for article_file in ARTICLES_DIR.glob("*.md"):
        metadata = extract_article_metadata(article_file)
        if metadata:
            articles.append(metadata)
    
    # Trier par date de création (plus récent en premier)
    articles.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return articles


def get_score_evolution() -> List[Dict[str, Any]]:
    """Récupère l'évolution des scores au fil du temps"""
    analytics = load_analytics_data()
    return analytics.get("scores_history", [])


def get_cost_trends(days: int = 30) -> List[Dict[str, Any]]:
    """Récupère les tendances des coûts sur N jours"""
    try:
        with open(TOKEN_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        return []
    
    # Grouper par jour
    daily_costs = defaultdict(float)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for entry in history:
        try:
            timestamp = datetime.fromisoformat(entry.get("timestamp", ""))
            if timestamp < cutoff_date:
                continue
            
            date_key = timestamp.strftime("%Y-%m-%d")
            total_tokens = entry.get("total_tokens", 0)
            # Estimation coût: $0.30 / 1M tokens
            cost = (total_tokens / 1_000_000) * 0.30
            daily_costs[date_key] += cost
        except:
            continue
    
    # Convertir en liste triée
    trends = [
        {"date": date, "cost": round(cost, 4)}
        for date, cost in sorted(daily_costs.items())
    ]
    
    return trends


def get_publication_stats() -> Dict[str, Any]:
    """Calcule les statistiques de publication"""
    articles = get_all_articles_metadata()
    
    total_articles = len(articles)
    
    # Articles par mois
    monthly_count = defaultdict(int)
    for article in articles:
        try:
            date = datetime.fromisoformat(article.get("created_at", ""))
            month_key = date.strftime("%Y-%m")
            monthly_count[month_key] += 1
        except:
            continue
    
    # Moyenne de mots
    word_counts = [a.get("word_count", 0) for a in articles if a.get("word_count")]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    
    # Temps de lecture moyen
    read_times = [a.get("read_time", 0) for a in articles if a.get("read_time")]
    avg_read_time = sum(read_times) / len(read_times) if read_times else 0
    
    return {
        "total_articles": total_articles,
        "monthly_count": dict(monthly_count),
        "avg_word_count": round(avg_words, 0),
        "avg_read_time": round(avg_read_time, 1),
        "total_words": sum(word_counts)
    }


def get_generation_time_stats() -> Dict[str, Any]:
    """Calcule les statistiques de temps de génération"""
    try:
        with open(TOKEN_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        return {}
    
    # Grouper par opération "generate_article" (génération complète)
    generation_entries = [
        e for e in history
        if e.get("operation") in ["generate_article", "style_refinement", "optimize_seo"]
    ]
    
    if not generation_entries:
        return {}
    
    # Estimer le temps basé sur les tokens (approximation)
    # GPT-4o-mini: ~1000 tokens/seconde
    total_tokens = sum(e.get("total_tokens", 0) for e in generation_entries)
    estimated_time_seconds = total_tokens / 1000
    
    # Grouper par article (même topic/title)
    articles_times = defaultdict(list)
    for entry in generation_entries:
        article_id = entry.get("article_title") or entry.get("topic", "unknown")
        articles_times[article_id].append(entry.get("total_tokens", 0))
    
    # Temps moyen par article
    avg_tokens_per_article = sum(
        sum(tokens) for tokens in articles_times.values()
    ) / len(articles_times) if articles_times else 0
    
    avg_time_per_article = avg_tokens_per_article / 1000  # secondes
    
    return {
        "total_generations": len(articles_times),
        "total_time_seconds": round(estimated_time_seconds, 1),
        "avg_time_per_article_seconds": round(avg_time_per_article, 1),
        "avg_time_per_article_minutes": round(avg_time_per_article / 60, 1)
    }


def get_comprehensive_stats() -> Dict[str, Any]:
    """Retourne toutes les statistiques complètes"""
    articles = get_all_articles_metadata()
    publication_stats = get_publication_stats()
    generation_stats = get_generation_time_stats()
    cost_trends = get_cost_trends(30)
    score_evolution = get_score_evolution()
    
    # Coût total
    try:
        with open(TOKEN_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        total_tokens = sum(e.get("total_tokens", 0) for e in history)
        total_cost = (total_tokens / 1_000_000) * 0.30
    except:
        total_cost = 0
    
    return {
        "articles": {
            "total": len(articles),
            "metadata": articles[:10]  # 10 plus récents
        },
        "publication": publication_stats,
        "generation": generation_stats,
        "costs": {
            "total": round(total_cost, 4),
            "trends_30d": cost_trends
        },
        "scores": {
            "evolution": score_evolution
        },
        "timestamp": datetime.now().isoformat()
    }


def export_stats_csv(stats: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """Exporte les statistiques en CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(["Métrique", "Valeur"])
    
    # Statistiques générales
    writer.writerow(["Total Articles", stats["articles"]["total"]])
    writer.writerow(["Coût Total ($)", stats["costs"]["total"]])
    writer.writerow(["Temps Moyen Génération (min)", stats["generation"].get("avg_time_per_article_minutes", 0)])
    writer.writerow(["Mots Moyens par Article", stats["publication"].get("avg_word_count", 0)])
    
    # Tendances coûts
    writer.writerow([])
    writer.writerow(["Date", "Coût ($)"])
    for trend in stats["costs"]["trends_30d"]:
        writer.writerow([trend["date"], trend["cost"]])
    
    return output.getvalue()


def export_stats_json(stats: Dict[str, Any]) -> str:
    """Exporte les statistiques en JSON"""
    return json.dumps(stats, indent=2, ensure_ascii=False)
