#!/usr/bin/env python3
"""
Système de suivi des tokens OpenAI
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).parent.parent
TOKEN_HISTORY_FILE = BASE_DIR / "data" / "token_history.json"


def load_token_history() -> List[Dict[str, Any]]:
    """Charge l'historique des tokens"""
    if not TOKEN_HISTORY_FILE.exists():
        return []
    
    try:
        with open(TOKEN_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        return history if isinstance(history, list) else []
    except Exception as e:
        print(f"⚠️  Erreur chargement historique tokens: {e}")
        return []


def save_token_history(history: List[Dict[str, Any]]):
    """Sauvegarde l'historique des tokens"""
    try:
        TOKEN_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde historique tokens: {e}")


def track_openai_usage(
    operation: str,
    model: str,
    usage: Dict[str, Any],
    topic: Optional[str] = None,
    article_title: Optional[str] = None
) -> None:
    """
    Enregistre l'utilisation de tokens OpenAI
    
    Args:
        operation: Type d'opération (ex: "generate_variants", "generate_article", "optimize_seo", "translate")
        model: Modèle utilisé (ex: "gpt-4o-mini")
        usage: Objet usage de la réponse OpenAI (contient prompt_tokens, completion_tokens, total_tokens)
        topic: Sujet de l'article (optionnel)
        article_title: Titre de l'article (optionnel)
    """
    history = load_token_history()
    
    # Extraire les tokens
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)
    
    # Créer l'entrée
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }
    
    if topic:
        entry["topic"] = topic
    if article_title:
        entry["article_title"] = article_title
    
    history.append(entry)
    
    # Garder seulement les 1000 dernières entrées
    if len(history) > 1000:
        history = history[-1000:]
    
    save_token_history(history)


def get_token_statistics() -> Dict[str, Any]:
    """Retourne des statistiques sur l'utilisation des tokens"""
    history = load_token_history()
    
    if not history:
        return {
            "total_entries": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "by_operation": {},
            "by_model": {},
            "recent_entries": []
        }
    
    total_tokens = sum(entry.get("total_tokens", 0) for entry in history)
    total_prompt_tokens = sum(entry.get("prompt_tokens", 0) for entry in history)
    total_completion_tokens = sum(entry.get("completion_tokens", 0) for entry in history)
    
    # Par opération
    by_operation = {}
    for entry in history:
        op = entry.get("operation", "unknown")
        if op not in by_operation:
            by_operation[op] = {
                "count": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0
            }
        by_operation[op]["count"] += 1
        by_operation[op]["total_tokens"] += entry.get("total_tokens", 0)
        by_operation[op]["prompt_tokens"] += entry.get("prompt_tokens", 0)
        by_operation[op]["completion_tokens"] += entry.get("completion_tokens", 0)
    
    # Par modèle
    by_model = {}
    for entry in history:
        model = entry.get("model", "unknown")
        if model not in by_model:
            by_model[model] = {
                "count": 0,
                "total_tokens": 0
            }
        by_model[model]["count"] += 1
        by_model[model]["total_tokens"] += entry.get("total_tokens", 0)
    
    # 10 dernières entrées
    recent_entries = history[-10:]
    
    return {
        "total_entries": len(history),
        "total_tokens": total_tokens,
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "by_operation": by_operation,
        "by_model": by_model,
        "recent_entries": recent_entries
    }


def estimate_cost(total_tokens: int, model: str = "gpt-4o-mini") -> float:
    """
    Estime le coût en USD basé sur les tokens
    
    Prix GPT-4o-mini (janvier 2025):
    - Input: $0.15 / 1M tokens
    - Output: $0.60 / 1M tokens
    """
    # Pour simplifier, on utilise une moyenne de $0.30 / 1M tokens
    # En réalité, il faudrait séparer prompt et completion
    cost_per_million = 0.30
    return (total_tokens / 1_000_000) * cost_per_million

