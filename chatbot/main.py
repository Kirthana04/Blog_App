import os
import json
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from database import Database
from embedding import EmbeddingService
from chatbot import Chatbot

# Load environment variables with better error handling
env_path = Path(".env")
if not env_path.exists():
    print(f"ERROR: .env file not found in {os.getcwd()}")
    print("Please create a .env file with your configuration.")
    
loaded = load_dotenv(verbose=True)
if not loaded:
    print("WARNING: Failed to load environment variables from .env file")

# Initialize the app with a lifespan context
db = Database()
embedding_service = EmbeddingService()
chatbot = Chatbot()

# Define lifespan context manager
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the database and index blogs
    await db.connect()
    blogs = await db.get_all_blogs()
    await embedding_service.index_blogs(blogs)
    yield
    # Shutdown: Close database connection
    await db.close()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type"]
)

class Query(BaseModel):
    text: str

class ChatResponse(BaseModel):
    answer: str
    has_answer: bool

@app.post("/api/chat", response_model=ChatResponse)
async def chat(query: Query):
    # Search for relevant blogs
    results = embedding_service.search(query.text)
    
    # Get the actual blog content
    relevant_blogs = []
    for match in results:
        try:
            blog_id = match.metadata["blog_id"]
            blog = await db.get_blog_by_id(blog_id)
            if blog and 'contents' in blog:  # Ensure blog has 'contents' field
                relevant_blogs.append(blog)
        except Exception as e:
            print(f"Error processing blog result: {str(e)}")
    
    # Get answer from LLM
    response = await chatbot.get_answer(query.text, relevant_blogs)
    return response

@app.get("/api/health")
async def health_check():
    # Basic health status
    status = {"status": "ok", "services": {}}
    
    # Check Pinecone connection
    try:
        pinecone_status = "unknown"
        if embedding_service.pc:
            indexes = embedding_service.pc.list_indexes().names()
            pinecone_status = f"connected, indexes: {indexes}"
        status["services"]["pinecone"] = pinecone_status
    except Exception as e:
        status["services"]["pinecone"] = f"error: {str(e)}"
    
    # Check Groq API key
    try:
        groq_status = "unknown"
        if chatbot.api_key:
            groq_status = chatbot.groq_api_key_format()
        status["services"]["groq"] = groq_status
    except Exception as e:
        status["services"]["groq"] = f"error: {str(e)}"
        
    return status

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)