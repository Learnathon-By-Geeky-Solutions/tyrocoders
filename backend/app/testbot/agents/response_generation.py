import logging
import json
from typing import Dict, Any, List
from llm import process_query

logger = logging.getLogger(__name__)

class ResponseGenerationAgent:
    """Generates response with enhanced context-awareness and proper JSON formatting"""
    
    async def generate_response(self, 
                               chatbot_id: str, 
                               query: str, 
                               query_analysis: Dict[str, Any],
                               search_results: List[str],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response with enhanced context handling"""
        # Check if we need specialized handling for this query type
        if query_analysis.get("is_sort_query") and query_analysis.get("sort_criteria") == "price":
            # For price sorting with previous product context
            if query_analysis.get("use_previous_product"):
                return await self._generate_sorted_product_response(
                    chatbot_id, query, query_analysis, search_results, context
                )
        
        # For regular queries, use the standard process_query function with enhanced context
        client_history = context.get("history", [])
        
        # Generate response using the existing LLM infrastructure
        response_text = process_query(chatbot_id, query, search_results, client_history)
        
        # Clean up response to handle LLM-generated JSON
        cleaned_response = self._clean_llm_response(response_text)
        
        # Parse response to check if it's structured JSON
        try:
            json_content = self._extract_json_from_response(cleaned_response)
            if json_content:
                response_data = json.loads(json_content)
                concise_answer = response_data.get("answer", cleaned_response)
            else:
                concise_answer = cleaned_response
            
            # Remove any newline characters from the answer
            concise_answer = concise_answer.replace("\n", " ")
            
            return {
                "status": "complete",
                "answer": concise_answer
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {
                "status": "complete",
                "answer": cleaned_response.replace("\n", " ")
            }
    
    def _clean_llm_response(self, response: str) -> str:
        """Clean up LLM response text"""
        # Remove markdown code block markers if present
        response = response.replace("```json", "").replace("```", "")
        
        # Clean up escaped newlines and quotes
        response = response.replace("\\n", "\n").replace('\\"', '"')
        
        return response.strip()
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from response text"""
        import re
        
        json_pattern = r'(\{.*\})'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            potential_json = match.group(0)
            try:
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        return ""
    
    async def _generate_sorted_product_response(self,
                                              chatbot_id: str,
                                              query: str,
                                              query_analysis: Dict[str, Any],
                                              search_results: List[str],
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response for sorted product queries"""
        product_name = query_analysis.get("product_mention")
        product_data = self._extract_products_from_results(search_results, product_name)
        direction = query_analysis.get("sort_direction", "asc")
        sorted_products = sorted(product_data, key=lambda x: x.get("price", 0), 
                               reverse=(direction == "desc"))
        
        if sorted_products:
            response_data = {
                "product_name": product_name,
                "product_description": f"Showing {len(sorted_products)} results for {product_name}, sorted by price",
                "sorted_products": sorted_products,
                "answer": self._format_sorted_products_answer(sorted_products, product_name, direction)
            }
            concise_answer = response_data["answer"]
        else:
            response_data = {
                "product_name": product_name,
                "answer": f"I'm sorry, I couldn't find any products matching '{product_name}' to sort by price."
            }
            concise_answer = response_data["answer"]
        
        # Remove newline characters from the final answer
        concise_answer = concise_answer.replace("\n", " ")
        
        return {
            "status": "complete",
            "answer": concise_answer
        }
    
    def _extract_products_from_results(self, search_results: List[str], product_name: str) -> List[Dict[str, Any]]:
        """(Placeholder) Extract product information from search results."""
        # Implementation would extract product details based on product_name.
        # Here we return a dummy list for demonstration.
        return [
            {"price": 19.99, "name": product_name, "url": "http://example.com/product1"},
            {"price": 29.99, "name": product_name, "url": "http://example.com/product2"}
        ]
    
    def _format_sorted_products_answer(self, sorted_products: List[Dict[str, Any]], product_name: str, direction: str) -> str:
        """Format a concise answer string for sorted product results"""
        return f"Found {len(sorted_products)} {product_name} products sorted by price ({direction})."

# Updated websocket_server.py code for proper JSON formatting
async def handle_client(websocket):
    """Handle client connection and messages with proper JSON formatting"""
    client_id = id(websocket)
    logger.info(f"Client {client_id} connected")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received message from client {client_id}: {data}")
                
                chatbot_id = data.get("chatbot_id")
                query = data.get("query")
                
                if not chatbot_id or not query:
                    error_msg = {"status": "error", "message": "Missing required fields: chatbot_id and query"}
                    await websocket.send(json.dumps(error_msg, ensure_ascii=False))
                    continue
                
                await websocket.send(json.dumps({"status": "searching", "message": "Searching knowledge base..."}, ensure_ascii=False))
                
                try:
                    await websocket.send(json.dumps({"status": "thinking", "message": "Processing your query..."}, ensure_ascii=False))
                    
                    response = await conversation_manager.process_message(client_id, chatbot_id, query)
                    
                    # Now sending a concise response with newlines removed
                    await websocket.send(json.dumps(response, ensure_ascii=False))
                    
                except Exception as e:
                    logger.error(f"Error in multi-agent processing: {e}")
                    await websocket.send(json.dumps({
                        "status": "error", 
                        "message": f"Error processing your request: {str(e)}"
                    }, ensure_ascii=False))
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from client {client_id}")
                await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON format"}, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {e}")
                await websocket.send(json.dumps({"status": "error", "message": f"Server error: {str(e)}"}, ensure_ascii=False))
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Unexpected error with client {client_id}: {e}")
