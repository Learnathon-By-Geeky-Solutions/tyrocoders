# agents/knowledge_retrieval.py
import logging
from typing import Dict, Any, List, Optional
from kb import search_kb  # Original search function

logger = logging.getLogger(__name__)

class KnowledgeRetrievalAgent:
    """Enhanced knowledge retrieval with context awareness"""
    
    async def search(self, chatbot_id: str, query: str, context: Dict[str, Any]) -> List[str]:
        """Search the knowledge base with context-aware enhancements"""
        # Extract relevant context
        mentioned_entities = context.get("mentioned_entities", {})
        products = mentioned_entities.get("products", [])
        attributes = mentioned_entities.get("attributes", [])
        
        # Improve search query based on query analysis
        query_analysis = self._analyze_search_query(query, context)
        
        # Adjust search parameters based on query type
        k = 1000  # Default number of results
        
        # Use different strategies for different query types
        if query_analysis.get("is_sort_query"):
            # For sort queries we need more results to sort effectively
            k = 2000
            # Add sorting criteria if available
            if query_analysis.get("sort_criteria") == "price":
                logger.info(f"Using price-optimized search for query: {query}")
        
        # Perform knowledge base search
        context_docs = search_kb(chatbot_id, query, k=k)
        
        # Post-process results based on query analysis
        processed_results = self._post_process_results(context_docs, query_analysis)
        
        return processed_results
    
    def _analyze_search_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search query for specialized handling"""
        query_lower = query.lower()
        
        # Check if this is a sort/filter query
        is_sort_query = any(term in query_lower for term in [
            "sort", "order", "arrange", "filter", "show only", "list"
        ])
        
        # Determine sort criteria
        sort_criteria = None
        if "price" in query_lower:
            sort_criteria = "price"
            sort_direction = "asc" if "low" in query_lower else "desc"
        elif any(term in query_lower for term in ["new", "recent", "latest"]):
            sort_criteria = "date"
        elif "popular" in query_lower:
            sort_criteria = "popularity"
        
        return {
            "is_sort_query": is_sort_query,
            "sort_criteria": sort_criteria,
            "sort_direction": "asc" if sort_criteria and "low" in query_lower else "desc"
        }
    
    def _post_process_results(self, results: List[str], query_analysis: Dict[str, Any]) -> List[str]:
        """Post-process search results based on query analysis"""
        # If this is a sort query with price criteria, re-rank results
        if query_analysis.get("is_sort_query") and query_analysis.get("sort_criteria") == "price":
            # Extract price info from results and sort
            results_with_price = []
            for doc in results:
                price = self._extract_price_from_doc(doc)
                if price is not None:
                    results_with_price.append((price, doc))
            
            # Sort by price
            direction = query_analysis.get("sort_direction", "asc")
            sorted_results = sorted(results_with_price, key=lambda x: x[0], 
                                   reverse=(direction == "desc"))
            
            # Return sorted documents
            return [doc for _, doc in sorted_results]
        
        return results
    
    def _extract_price_from_doc(self, doc: str) -> Optional[float]:
        """Extract price information from a document"""
        # This is a simplified implementation
        # In production, use regex or better parsing
        price_indicators = ["price:", "$", "cost:", "priced at"]
        doc_lower = doc.lower()
        
        for indicator in price_indicators:
            if indicator in doc_lower:
                # Find the position of the price indicator
                pos = doc_lower.find(indicator) + len(indicator)
                # Extract the text after the indicator
                text_after = doc_lower[pos:pos+20].strip()
                # Try to extract a number
                import re
                price_match = re.search(r'(\d+(\.\d+)?)', text_after)
                if price_match:
                    try:
                        return float(price_match.group(1))
                    except ValueError:
                        pass
        
        return None