import os
import time
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        # We'll set the model properly in initialize() based on index dimension
        self.model = None
        self.vector_dimension = None
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENV")
        self.index_name = "blog-chatbot"
        self.initialized = False
        
    def initialize(self):
        if not self.initialized:
            # Use the new Pinecone client approach
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Use an existing index or create new one
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name in existing_indexes:
                # Use existing index with its dimensions
                index_info = self.pc.describe_index(self.index_name)
                self.vector_dimension = index_info.dimension
                
                # Rather than trying to match models to dimensions perfectly,
                # we'll pad or truncate the embeddings to match the index dimension
                # Use a good model that we know works well
                if self.vector_dimension >= 768:
                    self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # Produces 768 dimensions
                    print(f"Using larger model (768 dimensions) and will adjust to {self.vector_dimension} dimensions")
                else:
                    self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # Produces 384 dimensions
                    print(f"Using smaller model (384 dimensions) and will adjust to {self.vector_dimension} dimensions")
            else:
                # Create new index with our preferred dimension
                self.vector_dimension = 384  # Default dimension for all-MiniLM-L6-v2
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.vector_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.pinecone_env
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            self.initialized = True
            print(f"Embedding service initialized with dimension {self.vector_dimension}")
    
    def get_embedding(self, text):
        """Generate embedding for text and adjust dimensions to match index requirements"""
        embedding = self.model.encode(text).tolist()
        original_dim = len(embedding)
        
        # Adjust dimensions if needed
        if original_dim != self.vector_dimension:
            if original_dim < self.vector_dimension:
                # Pad with zeros if the model produces smaller embeddings
                padding = [0.0] * (self.vector_dimension - original_dim)
                embedding = embedding + padding
                
            elif original_dim > self.vector_dimension:
                # Truncate if the model produces larger embeddings
                embedding = embedding[:self.vector_dimension]
            
            # Optional debug info
            # print(f"Adjusted embedding from {original_dim} to {len(embedding)} dimensions")
            
        return embedding
    
    async def index_blogs(self, blogs):
        """Index all blogs in the vector database"""
        self.initialize()
        
        # Clear the index first - handle with try/except in case it's a new index
        try:
            # For newer Pinecone SDK - use namespace="" for default namespace
            self.index.delete(delete_all=True, namespace="")
        except Exception as e:
            print(f"Note: Could not clear index - likely new or empty: {str(e)}")
        
        # Create vectors from blog contents
        vectors = []
        for blog in blogs:
            # Use title and contents for better context
            text = f"{blog['title']} {blog['contents']}"
            embedding = self.get_embedding(text)
            
            vectors.append({
                'id': str(blog['id']),
                'values': embedding,
                'metadata': {
                    'title': blog['title'],
                    'blog_id': blog['id']
                }
            })
            
            # Upsert in batches of 100 to avoid hitting rate limits
            if len(vectors) >= 100:
                self.index.upsert(vectors=vectors, namespace="")
                vectors = []
        
        # Upsert any remaining vectors
        if vectors:
            self.index.upsert(vectors=vectors, namespace="")
        
        print(f"Indexed {len(blogs)} blogs")
    
    def search(self, query, top_k=3):
        """Search for relevant blog content based on the query"""
        self.initialize()
        
        query_embedding = self.get_embedding(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=""
        )
        
        return results.matches