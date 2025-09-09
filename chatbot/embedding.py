import os
import time
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="D:\\OneDrive - 1CloudHub\\Desktop\\Files\\BBlog\\chatbot\\.env")

class EmbeddingService:
    def __init__(self):
        # Embedding model will be set based on Pinecone index requirements
        self.model = None
        self.vector_dimension = None
        
        # Load Pinecone API credentials from environment
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENV")
        
        # Set fixed index name for blog content
        self.index_name = "blog-chatbot"
        
        # Track initialization state to avoid repeated setup
        self.initialized = False

    def initialize(self):
        """
        Set up Pinecone client and embedding model based on index requirements
        """
        if not self.initialized:
            # Create Pinecone client using API key
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Check if our target index already exists
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name in existing_indexes:
                # Use existing index and adapt to its dimensions
                index_info = self.pc.describe_index(self.index_name)
                self.vector_dimension = index_info.dimension
                
                if self.vector_dimension >= 768:
                    # Use larger model for high-dimensional embeddings (better accuracy)
                    self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
                    print(f"Using larger model (768 dimensions) and will adjust to {self.vector_dimension} dimensions")
                else:
                    # Use smaller model for lower-dimensional embeddings (faster)
                    self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                    print(f"Using smaller model (384 dimensions) and will adjust to {self.vector_dimension} dimensions")
            else:
                # Create new index with default dimension
                self.vector_dimension = 384  # Default for all-MiniLM-L6-v2 model
                
                # Create Pinecone index with serverless specification
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.vector_dimension,
                    metric="cosine",  # Use cosine similarity for text embeddings
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.pinecone_env
                    )
                )
                
                # Load default embedding model for new index
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Get reference to the Pinecone index for operations
            self.index = self.pc.Index(self.index_name)
            
            # Mark as initialized to prevent repeated setup
            self.initialized = True
            print(f"Embedding service initialized with dimension {self.vector_dimension}")

    def get_embedding(self, text):
        """
        Generate vector embedding for given text with dimension adjustment
        """
        # Generate embedding using the loaded SentenceTransformer model
        embedding = self.model.encode(text).tolist()
        original_dim = len(embedding)
        
        # Adjust embedding dimension to match Pinecone index requirements
        if original_dim != self.vector_dimension:
            if original_dim < self.vector_dimension:
                # Pad with zeros if embedding is smaller than required
                padding = [0.0] * (self.vector_dimension - original_dim)
                embedding = embedding + padding
            elif original_dim > self.vector_dimension:
                # Truncate if embedding is larger than required
                embedding = embedding[:self.vector_dimension]
        
        return embedding

    async def index_blogs(self, blogs):
        """
        Perform full indexing of all blogs (clear existing and add all)
        """
        # Ensure service is initialized before indexing
        self.initialize()
        
        # Clear existing vectors from index for fresh start
        try:
            self.index.delete(delete_all=True, namespace="")
        except Exception as e:
            print(f"Note: Could not clear index - likely new or empty: {str(e)}")
        
        # Process each blog and create vector representations
        vectors = []
        for blog in blogs:
            # Combine title and content for comprehensive context
            text = f"{blog['title']} {blog['contents']}"
            
            # Generate embedding for the combined text
            embedding = self.get_embedding(text)
            
            # Create vector object with metadata for retrieval
            vectors.append({
                'id': str(blog['id']),          # Unique identifier
                'values': embedding,            # Vector representation
                'metadata': {                   # Searchable metadata
                    'title': blog['title'],
                    'blog_id': blog['id']
                }
            })
            
            # Upload in batches to avoid rate limits and memory issues
            if len(vectors) >= 100:
                self.index.upsert(vectors=vectors, namespace="")
                vectors = []  # Reset batch
        
        # Upload any remaining vectors in final batch
        if vectors:
            self.index.upsert(vectors=vectors, namespace="")
        
        print(f"Indexed {len(blogs)} blogs")

    def search(self, query, top_k=3):
        """
        Search the vector index for documents most similar to query
        """
        # Ensure service is initialized before searching
        self.initialize()
        
        # Convert query text to embedding for similarity comparison
        query_embedding = self.get_embedding(query)
        
        # Query Pinecone index for most similar vectors
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,                    # Return top N most similar
            include_metadata=True,          # Include blog metadata in results
            namespace=""                    # Use default namespace
        )
        
        # Return matched documents with similarity scores
        return results.matches

    async def get_existing_blog_ids(self):
        """
        Retrieve set of blog IDs that are already indexed in Pinecone, used for incremental indexing to avoid duplicates
        """
        try:
            self.initialize()
            
            # Since Pinecone doesn't provide direct ID listing, Create dummy query vector to retrieve all indexed items
            dummy_query = [0.0] * self.vector_dimension
            
            # Query with high top_k to get all existing vectors
            results = self.index.query(
                vector=dummy_query,
                top_k=10000,                # Adjust based on expected blog count
                include_metadata=True,
                namespace=""
            )
            
            # Extract blog IDs from metadata of all matches
            return {match.metadata.get('blog_id') for match in results.matches 
                    if match.metadata.get('blog_id')}
            
        except Exception as e:
            print(f"Could not get existing blog IDs: {str(e)}")
            return set()

    async def index_blogs_incremental(self, blogs):
        """
        Index only new blogs that haven't been indexed yet
        """
        self.initialize()
        
        # Get set of blog IDs already in the index
        existing_blog_ids = await self.get_existing_blog_ids()
        print(f"Found {len(existing_blog_ids)} already indexed blogs")
        
        # Identify blogs that need indexing (not in existing set)
        vectors_to_upsert = []
        new_blogs_count = 0
        
        for blog in blogs:
            blog_id = blog['id']
            
            # Only process blogs that aren't already indexed
            if blog_id not in existing_blog_ids:
                # Prepare blog content and generate embedding
                text = f"{blog['title']} {blog['contents']}"
                embedding = self.get_embedding(text)
                
                # Create vector for new blog
                vectors_to_upsert.append({
                    'id': str(blog_id),
                    'values': embedding,
                    'metadata': {
                        'title': blog['title'],
                        'blog_id': blog_id
                    }
                })
                new_blogs_count += 1
                
                # Batch upload to avoid overwhelming the service
                if len(vectors_to_upsert) >= 100:
                    self.index.upsert(vectors=vectors_to_upsert, namespace="")
                    vectors_to_upsert = []
        
        # Upload remaining vectors in final batch
        if vectors_to_upsert:
            self.index.upsert(vectors=vectors_to_upsert, namespace="")
        
        print(f"Incrementally indexed {new_blogs_count} new blogs")
        return new_blogs_count

    async def force_reindex_all_blogs(self, blogs):
        return await self.index_blogs(blogs)

    async def index_single_blog(self, blog):
        """
        Index a single blog immediately, called when new blogs are added to the system
        """
        # Ensure service is initialized
        self.initialize()
        
        # Prepare blog content for embedding
        text = f"{blog['title']} {blog['contents']}"
        embedding = self.get_embedding(text)
        
        # Create vector with metadata
        vector = {
            'id': str(blog['id']),
            'values': embedding,
            'metadata': {
                'title': blog['title'],
                'blog_id': blog['id']
            }
        }
        
        # Upsert single vector to Pinecone index
        self.index.upsert(vectors=[vector], namespace="")
        print(f"Successfully indexed new blog: {blog['title']}")
        
        return True
