class HuggingFaceAPIError(Exception):
    """Exception raised for errors related to the HuggingFace API."""
    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"HuggingFace API error: {status_code} - {response_text}")

class OllamaAPIError(Exception):
    """Exception raised for errors related to the Ollama API."""
    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Ollama API error: {status_code} - {response_text}")