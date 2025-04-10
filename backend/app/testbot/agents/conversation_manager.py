# agents/conversation_manager.py
import logging
from typing import Dict, Any, List, Optional
from .context_keeper import ContextKeeperAgent
from .query_understanding import QueryUnderstandingAgent
from .knowledge_retrieval import KnowledgeRetrievalAgent
from .response_generation import ResponseGenerationAgent

logger = logging.getLogger(__name__)

class ConversationManagerAgent:
    """Orchestrates the flow between different agents in the system"""
    
    def __init__(self):
        self.context_keeper = ContextKeeperAgent()
        self.query_understanding = QueryUnderstandingAgent()
        self.knowledge_retrieval = KnowledgeRetrievalAgent()
        self.response_generation = ResponseGenerationAgent()
    
    async def process_message(self, client_id: str, chatbot_id: str, query: str) -> Dict[str, Any]:
        """Process a user message through the agent pipeline"""
        # Step 1: Get conversation context
        conversation_context = self.context_keeper.get_context(client_id)
        
        # Step 2: Understand the query with context
        query_analysis = self.query_understanding.analyze_query(
            query, 
            conversation_context
        )
        
        # Step 3: Search knowledge base with enhanced context
        search_results = await self.knowledge_retrieval.search(
            chatbot_id,
            query_analysis["enhanced_query"],
            conversation_context
        )
        
        # Step 4: Generate response
        response = await self.response_generation.generate_response(
            chatbot_id,
            query,
            query_analysis,
            search_results,
            conversation_context
        )
        
        # Step 5: Update conversation context with new interaction
        self.context_keeper.update_context(
            client_id,
            query,
            response,
            query_analysis,
            search_results
        )
        
        return response
