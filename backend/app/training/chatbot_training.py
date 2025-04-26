import os
import openai
from typing import List, Dict
import logging

class ContextualChatbot:
    def __init__(self, products: List[Dict], chatbot_id: str):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set")
        
        self.chatbot_id = chatbot_id
        self.products = products
        
        # Prepare context for the LLM
        self.product_context = self._prepare_product_context()
        
        # Maintain conversation history
        self.reset_conversation()

    def _prepare_product_context(self, max_products: int = 20) -> str:
        """
        Prepare a concise context of products for the LLM
        Limits the number of products to avoid overwhelming the context
        """
        context = "Product Catalog:\n"
        for idx, product in enumerate(self.products[:max_products], 1):
            context += (
                f"{idx}. {product.get('name', 'Unnamed Product')}\n"
                f"   Price: {product.get('price', 'Price not available')}\n"
                f"   Description: {product.get('description', 'No description')}\n"
                f"   URL: {product.get('url', 'No URL')}\n\n"
            )
        return context

    def generate_response(self, query: str) -> str:
        """
        Generate a response using OpenAI's GPT model
        """
        try:
            # Add user query to conversation history
            self.conversation_history.append({
                "role": "user", 
                "content": query
            })

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=300,
                temperature=0.7
            )

            # Extract the assistant's response
            assistant_response = response.choices[0].message['content']

            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": assistant_response
            })

            return assistant_response

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)}"

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = [
            {
                "role": "system", 
                "content": f"""You are an AI assistant specialized in providing information about products from an e-commerce store. 
                You have access to the following product catalog:
                {self.product_context}
                
                Guidelines:
                - Always base your responses on the available product information
                - If a query cannot be answered using the product catalog, politely explain that
                - Provide helpful, conversational, and accurate product information
                - If asked about a product, include details like name, price, and key features
                """
            }
        ]