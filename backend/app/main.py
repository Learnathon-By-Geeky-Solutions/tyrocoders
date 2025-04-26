from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.mongodb import connect_to_mongo, close_mongo_connection
from api.v1.endpoints import (
    auth_router,
    chatbot_router, 
    chatbot_conversation_router, 
    user_router, 
    chatbot_embed_router,
    subscription_router
)
import uvicorn

# later to be replaced by .env file
class Settings:
    PROJECT_NAME = "Ebuddy"
    PROJECT_VERSION = "1.0.0"
    PROJECT_TITLE = "Ecommerce AI Agent(Ebuddy)"
    BACKEND_PORT = 8000
    IS_RELOAD = True

settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
    docs_url="/api/docs",
    debug=True,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files (e.g., JS, CSS)
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")

# Startup and shutdown events
async def startup_handler():
    await connect_to_mongo()


async def shutdown_handler():
    await close_mongo_connection()


app.add_event_handler("startup", startup_handler)
app.add_event_handler("shutdown", shutdown_handler)

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_TITLE}!"}

app.include_router(auth_router, prefix="/api/v1/user", tags=["Auth"])
app.include_router(user_router, prefix="/api/v1/user", tags=["User"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])
app.include_router(
    chatbot_conversation_router,
    prefix="/api/v1/chatbot-conversation",
    tags=["Chatbot Conversation"],
)
app.include_router(
    chatbot_embed_router,
    prefix="/api/v1/chatbot-embed",
    tags=["Chatbot Embed"],
)
app.include_router(
    subscription_router,
    prefix="/api/v1/subscription",
    tags=["Subscription"],
)
#other routes will go here    

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.IS_RELOAD,
    )