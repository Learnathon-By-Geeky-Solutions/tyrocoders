# agents/query_understanding.py
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class QueryUnderstandingAgent:
    """Analyzes and understands user queries with context"""
    
    def analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a query to understand intent and references"""
        query_lower = query.lower()
        
        # Check if query is about sorting or filtering
        is_sort_query = any(term in query_lower for term in [
            "sort", "order", "arrange", "filter", "show only", "list"
        ])
        
        # Extract sort criteria
        sort_criteria = None
        if is_sort_query:
            if "price" in query_lower:
                sort_criteria = "price"
                sort_direction = "asc" if "low" in query_lower else "desc"
            elif any(term in query_lower for term in ["new", "recent", "latest"]):
                sort_criteria = "date"
            elif "popular" in query_lower:
                sort_criteria = "popularity"
        
        # Check for price-related queries
        price_related = any(term in query_lower for term in [
            "price", "cost", "cheap", "expensive", "affordable", "discount"
        ])
        
        # Extract product mentions directly from query
        product_mention = self._extract_product_from_query(query)
        
        # If no direct product mention but there's context, this might be a follow-up
        is_followup = self._is_followup_question(query)
        
        # Determine if we should use previous product context
        use_previous_product = is_followup and not product_mention and context.get("current_product")
        
        # Build enhanced query using context if appropriate
        enhanced_query = query
        if use_previous_product:
            previous_product = context.get("current_product")
            if is_sort_query:
                # For sort queries with previous product, maintain product context
                enhanced_query = f"{previous_product} {query}"
                # Mark the previous product as the current product mention
                product_mention = previous_product
        
        # Extract attribute mentions
        attribute_mentions = self._extract_attributes(query)
        
        return {
            "original_query": query,
            "enhanced_query": enhanced_query,
            "is_sort_query": is_sort_query,
            "sort_criteria": sort_criteria,
            "sort_direction": sort_direction if is_sort_query and sort_criteria else None,
            "price_related": price_related,
            "product_mention": product_mention,
            "is_followup": is_followup,
            "use_previous_product": use_previous_product,
            "attribute_mentions": attribute_mentions
        }
    
    def _extract_product_from_query(self, query: str) -> str:
        """Extract potential product mentions from query"""
        product_indicators = ["show me", "looking for", "find", "search for", "information about", "about the"]
        query_lower = query.lower()
        
        # Check for direct product mentions
        for indicator in product_indicators:
            if indicator in query_lower:
                product_part = query_lower.split(indicator, 1)[1].strip()
                words = product_part.split()
                if len(words) > 2:
                    return " ".join(words[:3])
                return product_part
        
        # Look for product categories/types
        product_types = [
            "jeans", "shirt", "t-shirt", "shoe", "dress", "hat", "jacket", 
            "pants", "shorts", "socks", "sweater", "coat"
        ]
        
        for product_type in product_types:
            if product_type in query_lower:
                # Find the product with potential adjectives
                pattern = r"([a-z]+\s+){0,3}" + product_type
                match = re.search(pattern, query_lower)
                if match:
                    return match.group(0).strip()
                return product_type
        
        return ""
    
    def _is_followup_question(self, query: str) -> bool:
        """Determine if a query is likely a follow-up question"""
        followup_indicators = [
            "how much", "what about", "is it", "does it", "can it", 
            "tell me more", "more info", "price", "color", "size",
            "also", "too", "as well", "another", "different",
            "sort", "filter", "list", "show", "order", "arrange"
        ]
        
        query_lower = query.lower()
        
        # Check if query starts with a pronoun or lacks a subject
        if any(query_lower.startswith(word) for word in ["it", "that", "this", "they", "those"]):
            return True
            
        # Check for other follow-up indicators
        if any(indicator in query_lower for indicator in followup_indicators):
            return True
            
        return False
    
    def _extract_attributes(self, query: str) -> List[str]:
        """Extract product attributes mentioned in query"""
        attributes = []
        query_lower = query.lower()
        
        # Define common product attributes
        attribute_list = [
            "color", "size", "material", "style", "brand", "price", 
            "rating", "discount", "sale", "new", "popular"
        ]
        
        for attr in attribute_list:
            if attr in query_lower:
                attributes.append(attr)
                
        # Look for specific colors
        colors = ["red", "blue", "green", "black", "white", "yellow", "purple", "orange", "pink", "brown"]
        for color in colors:
            if color in query_lower:
                if "color" not in attributes:
                    attributes.append("color")
                break
        
        return attributes