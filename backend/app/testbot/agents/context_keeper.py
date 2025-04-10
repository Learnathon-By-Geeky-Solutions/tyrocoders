# agents/context_keeper.py
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class ContextKeeperAgent:
    """Maintains and manages conversation context"""
    
    def __init__(self, max_history: int = 10):
        self.conversation_history = defaultdict(list)
        self.product_contexts = {}
        self.max_history = max_history
    
    def get_context(self, client_id: str) -> Dict[str, Any]:
        """Get the current conversation context for a client"""
        return {
            "history": self.conversation_history.get(client_id, []),
            "current_product": self.product_contexts.get(client_id, None),
            "last_search_results": None,  # Will be populated if available
            "mentioned_entities": self._extract_entities_from_history(client_id)
        }
    
    def update_context(self, client_id: str, query: str, response: Any, 
                      query_analysis: Dict[str, Any], search_results: List[str]) -> None:
        """Update the conversation context with new interaction"""
        # Extract response data
        response_text = response.get("answer", "")
        structured_data = response.get("structured_data", {})
        
        # Store the interaction in conversation history
        self.conversation_history[client_id].append({
            "query": query,
            "response": response_text,
            "structured_data": structured_data,
            "query_analysis": query_analysis,
        })
        
        # Update product context if a product was mentioned
        if query_analysis.get("product_mention"):
            self.product_contexts[client_id] = query_analysis["product_mention"]
            
        # Store search results metadata (not the full results to save memory)
        if "last_search_results_meta" not in self.conversation_history[client_id][-1]:
            self.conversation_history[client_id][-1]["last_search_results_meta"] = {
                "count": len(search_results),
                "query_used": query_analysis.get("enhanced_query", query)
            }
        
        # Limit conversation history size
        if len(self.conversation_history[client_id]) > self.max_history:
            self.conversation_history[client_id] = self.conversation_history[client_id][-self.max_history:]
    
    def _extract_entities_from_history(self, client_id: str) -> Dict[str, List[str]]:
        """Extract mentioned entities from conversation history"""
        entities = {"products": [], "attributes": [], "price_mentions": []}
        
        if client_id not in self.conversation_history:
            return entities
            
        # Extract entities from history
        for exchange in self.conversation_history[client_id]:
            query_analysis = exchange.get("query_analysis", {})
            
            # Add product mentions
            if "product_mention" in query_analysis and query_analysis["product_mention"]:
                if query_analysis["product_mention"] not in entities["products"]:
                    entities["products"].append(query_analysis["product_mention"])
            
            # Add attribute mentions
            for attribute in query_analysis.get("attribute_mentions", []):
                if attribute not in entities["attributes"]:
                    entities["attributes"].append(attribute)
                    
            # Add price mentions
            if query_analysis.get("price_related", False):
                entities["price_mentions"].append(True)
                
        return entities