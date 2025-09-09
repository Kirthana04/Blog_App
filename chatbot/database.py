import os
import asyncpg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="D:\\OneDrive - 1CloudHub\\Desktop\\Files\\BBlog\\chatbot\\.env")

class Database:
    def __init__(self):
        # Connection pool will be created when connect() is called
        self.pool = None
        # Get database connection URL from environment variables
        self.database_url = os.getenv("DATABASE_URL")

    async def connect(self):
        """
        Create asynchronous connection pool to PostgreSQL database
        """
        if self.pool is None:
            # Create connection pool with automatic connection management
            self.pool = await asyncpg.create_pool(self.database_url)
            print("Database connection pool created")

    async def close(self):
        """
        Close database connection pool gracefully
        """
        if self.pool:
            await self.pool.close()
            print("Database connection pool closed")

    async def get_all_blogs(self):
        """
        Fetch all blog records from the database and returns dictionaries containing blog data
        """
        # Acquire connection from pool and execute query
        async with self.pool.acquire() as conn:
            # Execute SQL query to select all blog fields from blogs table
            blogs = await conn.fetch("""
                SELECT id, title, user_id, description, contents, created_at
                FROM blogschema.blogs
            """)
            
            # Convert database records to Python dictionaries for easier handling
            return [dict(blog) for blog in blogs]

    async def get_blog_by_id(self, blog_id):
        """
        Retrieve a specific blog by its ID
        """
        async with self.pool.acquire() as conn:
            # Execute parameterized query to prevent SQL injection
            blog = await conn.fetchrow("""
                SELECT id, title, user_id, description, contents, created_at
                FROM blogschema.blogs
                WHERE id = $1
            """, blog_id)
            
            # Return blog as dictionary if found, None otherwise
            if blog:
                return dict(blog)
            return None

    async def get_blogs_modified_after(self, timestamp):
        """
        Useful for incremental updates and tracking changes
        """
        async with self.pool.acquire() as conn:
            # Query blogs created or updated after timestamp, ordered by creation time
            blogs = await conn.fetch("""
                SELECT id, title, user_id, description, contents, created_at
                FROM blogschema.blogs
                WHERE created_at > $1 OR updated_at > $1
                ORDER BY created_at DESC
            """, timestamp)
            return [dict(blog) for blog in blogs]

    async def get_blog_count(self):
        """
        Get total number of blogs in the database
        """
        async with self.pool.acquire() as conn:
            # Execute count query and return scalar result
            result = await conn.fetchval("SELECT COUNT(*) FROM blogschema.blogs")
            return result
