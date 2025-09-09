import os
import json
import sys
import asyncio
import asyncpg
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from database import Database
from embedding import EmbeddingService
from chatbot import Chatbot, StreamingChatbot

# Load environment variables with explicit path checking
env_file_path = "D:\\OneDrive - 1CloudHub\\Desktop\\Files\\BBlog\\chatbot\\.env"

if not Path(env_file_path).exists():
    print(f"ERROR: .env file not found at {env_file_path}")
    print("Please check your absolute path.")
else:
    loaded = load_dotenv(dotenv_path=env_file_path, verbose=True)
    if not loaded:
        print("WARNING: Failed to load environment variables from .env file")
    else:
        print(f"Successfully loaded environment variables from {env_file_path}")

# Initialize service instances
db = Database()
embedding_service = EmbeddingService()

# Initialize both regular and streaming chatbots
regular_chatbot = Chatbot()  # For REST API compatibility
streaming_chatbot = None     # Will be initialized after services are ready

# Global variable to track the background notification listener task
notification_listener_task = None

# WebSocket Connection Manager for handling multiple clients
# Tracks all active connections and manages sending/receiving messages
class ConnectionManager:
    """
    Manages multiple WebSocket connections for concurrent chat sessions
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📱 New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"📱 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")

# Initialize connection manager
manager = ConnectionManager()

async def listen_for_blog_notifications():
    try:
        # Create separate database connection dedicated to listening for notifications
        conn = await asyncpg.connect(db.database_url)
        
        # Define callback function that handles incoming notifications
        async def handle_new_blog(connection, pid, channel, payload):
            """
            Callback function triggered when 'blog_added' notification is received
            Fetches the new blog from database and indexes it immediately
            """
            try:
                # Parse blog ID from notification payload
                blog_id = int(payload)
                print(f"🔔 New blog notification received: ID {blog_id}")
                
                # Fetch complete blog data from database using the ID
                blog = await db.get_blog_by_id(blog_id)
                if blog:
                    # Index the new blog immediately in Pinecone
                    await index_single_blog_immediately(blog)
                    print(f"✅ Successfully auto-indexed blog: {blog['title']}")
                else:
                    print(f"⚠️ Blog ID {blog_id} not found")
            except Exception as e:
                print(f"❌ Error handling blog notification: {e}")
        
        # Register our callback function to listen for 'blog_added' notifications
        await conn.add_listener('blog_added', handle_new_blog)
        print("🎧 Listening for new blog notifications...")
        
        # Keep the connection alive indefinitely to continue receiving notifications
        while True:
            await asyncio.sleep(30)
            
    except asyncio.CancelledError:
        # Handle graceful shutdown when task is cancelled
        print("📴 Blog notification listener stopped")
        if 'conn' in locals():
            await conn.close()
    except Exception as e:
        print(f"❌ Error in blog notification listener: {e}")

async def index_single_blog_immediately(blog):
    """
    Index a single blog immediately when notified of its creation
    """
    try:
        # Ensure embedding service is properly initialized
        embedding_service.initialize()
        
        # Combine blog title and content for comprehensive indexing
        text = f"{blog['title']} {blog['contents']}"
        
        # Generate vector embedding for the blog content
        embedding = embedding_service.get_embedding(text)
        
        # Prepare vector object with metadata for Pinecone
        vector = {
            'id': str(blog['id']),
            'values': embedding,
            'metadata': {
                'title': blog['title'],
                'blog_id': blog['id']
            }
        }
        
        # Upload vector to Pinecone index immediately
        embedding_service.index.upsert(vectors=[vector], namespace="")
        print(f"Successfully indexed new blog: {blog['title']}")
        
        return True
    except Exception as e:
        print(f"Error indexing blog {blog.get('title', 'Unknown')}: {e}")
        return False

# Import context manager for FastAPI lifespan events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager that handles startup and shutdown events
    Manages database connections, initial indexing, and background task lifecycle
    """
    global notification_listener_task, streaming_chatbot
    
    print("🚀 Starting up chatbot application...")
    
    # Connect to PostgreSQL database
    await db.connect()
    
    # Fetch all existing blogs for initial indexing
    blogs = await db.get_all_blogs()
    
    # Determine indexing strategy based on environment variable
    force_reindex = os.getenv("FORCE_REINDEX", "false").lower() == "true"
    
    if force_reindex:
        # Perform complete rebuild of vector index
        print("Force reindex enabled - rebuilding entire index")
        await embedding_service.force_reindex_all_blogs(blogs)
    else:
        # Perform incremental indexing (only new blogs)
        print("Using incremental indexing")
        new_count = await embedding_service.index_blogs_incremental(blogs)
        
        # If no new blogs found, check if index is completely empty
        if new_count == 0:
            print("No new blogs found - checking if index is empty")
            try:
                embedding_service.initialize()
                stats = embedding_service.index.describe_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                
                # If index is empty, perform initial full indexing
                if total_vectors == 0:
                    print("Index is empty - performing initial indexing")
                    await embedding_service.force_reindex_all_blogs(blogs)
            except Exception as e:
                print(f"Could not check index stats: {e}")
    
    # Initialize streaming chatbot after all services are ready
    streaming_chatbot = StreamingChatbot(db, embedding_service)
    print("✅ Streaming chatbot initialized")
    
    # Start background task to listen for database notifications
    notification_listener_task = asyncio.create_task(listen_for_blog_notifications())
    print("✅ Application startup complete")
    
    # Yield control to FastAPI (application runs here)
    yield
    
    # === SHUTDOWN SEQUENCE ===
    print("🛑 Shutting down chatbot application...")
    
    # Cancel background notification listener task
    if notification_listener_task:
        notification_listener_task.cancel()
        try:
            await notification_listener_task
        except asyncio.CancelledError:
            pass
    
    # Close database connection pool
    await db.close()
    print("✅ Application shutdown complete")

# Create FastAPI application instance with lifespan management
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type"]
)

# Define Pydantic models for API request/response validation
class Query(BaseModel):
    """Model for incoming chat requests"""
    text: str  # User's question or message

class ChatResponse(BaseModel):
    """Model for chat responses"""
    answer: str      # Generated response text
    has_answer: bool # Whether response contains useful information

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming chat
    Handles connection lifecycle and message streaming
    """
    await manager.connect(websocket) # Each client gets own connection
    print(f"🔌 Connected: {websocket.client}")

    try:
        while True: # Independent message loop per connection
            # Receive user message from WebSocket
            data = await websocket.receive_text() # Process this client's message independently

            try:
                # Parse JSON message (expecting {"message": "user query"})
                message_data = json.loads(data) if data.startswith('{') else {"message": data}
                user_query = message_data.get("message", data)
                
                if not user_query.strip():
                    await manager.send_personal_message("❌ Empty message received", websocket)
                    continue
                
                print(f"💬 WebSocket received: {user_query}")
                
                # Search for relevant blogs (same as regular chat endpoint)
                results = embedding_service.search(user_query)
                
                # Retrieve full blog content
                relevant_blogs = []
                for match in results:
                    try:
                        blog_id = match.metadata["blog_id"]
                        blog = await db.get_blog_by_id(blog_id)
                        if blog and 'contents' in blog:
                            relevant_blogs.append(blog)
                    except Exception as e:
                        print(f"Error processing blog result: {str(e)}")
                
                # Send typing indicator
                await manager.send_personal_message(json.dumps({
                    "type": "typing",
                    "message": "BloQ is thinking..."
                }), websocket)
                
                # Stream the response using enhanced chatbot
                if streaming_chatbot:
                    await streaming_chatbot.get_streaming_answer(user_query, relevant_blogs, websocket, manager)
                else:
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "content": "Streaming chatbot not initialized"
                    }), websocket)
                
                
            except json.JSONDecodeError:
                # Handle plain text messages
                await manager.send_personal_message("Received plain text message", websocket)
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
                await manager.send_personal_message(f"❌ Error: {str(e)}", websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8005))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
