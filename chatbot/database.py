import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv("DATABASE_URL")
        
    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.database_url)
            print("Database connection pool created")
        
    async def close(self):
        if self.pool:
            await self.pool.close()
            # Removed wait_closed() as it's not needed in newer versions of asyncpg
            print("Database connection pool closed")
    
    async def get_all_blogs(self):
        """Fetch all blogs from the database"""
        async with self.pool.acquire() as conn:
            blogs = await conn.fetch("""
                SELECT id, title, user_id, description, contents, created_at
                FROM blogschema.blogs
            """)
            
            # Convert to list of dictionaries
            return [dict(blog) for blog in blogs]
    
    async def get_blog_by_id(self, blog_id):
        """Fetch a specific blog by ID"""
        async with self.pool.acquire() as conn:
            blog = await conn.fetchrow("""
                SELECT id, title, user_id, description, contents, created_at
                FROM blogschema.blogs
                WHERE id = $1
            """, blog_id)
            
            if blog:
                return dict(blog)
            return None