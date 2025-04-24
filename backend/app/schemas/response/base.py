from pydantic import BaseModel


class DefaultResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Any Success Message",
            }
        }


class DefaultErrorResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Any Custom Error Message",
            }
        }


class ValidationErrorResponse(BaseModel):
    message: str
    errors: list

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Payload Validation failed",
                "errors": [
                    {"field": "username", "message": "field required"},
                    {"field": "password", "message": "field required"},
                ],
            }
        }
