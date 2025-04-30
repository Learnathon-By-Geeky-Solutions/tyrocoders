"""
Custom Exceptions for External API Errors

This module defines custom exceptions for handling errors when interacting with
external APIs such as HuggingFace and Ollama. These exceptions encapsulate the
HTTP status code and response body for easier debugging and error handling.

Classes:
    HuggingFaceAPIError: Raised when an error response is returned from the HuggingFace API.
    OllamaAPIError: Raised when an error response is returned from the Ollama API.
"""

class HuggingFaceAPIError(Exception):
    """
    Exception raised for errors related to the HuggingFace API.

    Attributes:
        status_code (int): The HTTP status code returned by the HuggingFace API.
        response_text (str): The response body returned by the HuggingFace API.
    """
    def __init__(self, status_code: int, response_text: str):
        """
        Initializes the HuggingFaceAPIError with status code and response text.

        Args:
            status_code (int): The HTTP status code.
            response_text (str): The error message or response body.
        """
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"HuggingFace API error: {status_code} - {response_text}")


class OllamaAPIError(Exception):
    """
    Exception raised for errors related to the Ollama API.

    Attributes:
        status_code (int): The HTTP status code returned by the Ollama API.
        response_text (str): The response body returned by the Ollama API.
    """
    def __init__(self, status_code: int, response_text: str):
        """
        Initializes the OllamaAPIError with status code and response text.

        Args:
            status_code (int): The HTTP status code.
            response_text (str): The error message or response body.
        """
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Ollama API error: {status_code} - {response_text}")
