from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from app.api.v1.endpoints import auth_router
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
# app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_TITLE}!"}

# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
#other routes will go here    

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.IS_RELOAD,
    )