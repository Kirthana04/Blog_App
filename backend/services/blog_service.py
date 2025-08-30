import asyncpg
from schemas.blog_schemas import BlogCreate
from routes.blog_router import BlogResponse

def _row_to_dict(row):
    if not row:
        return None
    row_dict = dict(row)
    # IMAGE is now a string path, no base64 encoding needed
    return row_dict

async def create_blog(
    conn: asyncpg.Connection,
    user_id: int,
    title: str,
    description: str = None,
    image: str = None,
    tags: list = None,
    contents: str = None,
):
    query = """
        INSERT INTO blogschema.blogs (user_id, title, description, image, tags, contents)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, user_id, title, description, image, tags, contents, deleted_flag, created_at
    """
    row = await conn.fetchrow(
        query,
        user_id,
        title,
        description,
        image,
        tags,
        contents
    )
    return _row_to_dict(row)

async def get_all_blogs(conn: asyncpg.Connection):
    query = """
        SELECT id, user_id, title, description, image, tags, contents, deleted_flag, created_at
        FROM blogschema.blogs
        WHERE deleted_flag = FALSE
        ORDER BY created_at DESC
    """
    rows = await conn.fetch(query)
    return [_row_to_dict(row) for row in rows]

async def get_user_blogs(conn: asyncpg.Connection, user_id: int):
    query = """
        SELECT id, user_id, title, description, image, tags, contents, deleted_flag, created_at
        FROM blogschema.blogs
        WHERE user_id = $1 AND deleted_flag = FALSE
        ORDER BY created_at DESC
    """
    rows = await conn.fetch(query, user_id)
    return [_row_to_dict(row) for row in rows]

async def get_blog_by_id(conn: asyncpg.Connection, blog_id: int):
    query = """
        SELECT id, user_id, title, description, image, tags, contents, deleted_flag, created_at
        FROM blogschema.blogs
        WHERE id = $1 AND deleted_flag = FALSE
    """
    row = await conn.fetchrow(query, blog_id)
    return _row_to_dict(row)

async def soft_delete_blog(pool: asyncpg.Pool, blog_id: int, user_id: int):
    async with pool.acquire() as conn:
        query = """
            UPDATE blogschema.blogs
            SET deleted_flag = TRUE
            WHERE id = $1 AND user_id = $2 AND deleted_flag = FALSE
            RETURNING id
        """
        row = await conn.fetchrow(query, blog_id, user_id)
        return {"success": row is not None}


async def restore_blog(conn: asyncpg.Connection, blog_id: int, user_id: int):
    query = """
        UPDATE blogschema.blogs
        SET deleted_flag = FALSE
        WHERE id = $1 AND user_id = $2 AND deleted_flag = TRUE
        RETURNING id
    """
    row = await conn.fetchrow(query, blog_id, user_id)
    return {"success": row is not None}


async def get_blog_by_id(pool, blog_id: int) -> BlogResponse | None:
    async with pool.acquire() as conn:
        query = """
            SELECT id, user_id, title, description, image, tags, contents
            FROM blogschema.blogs
            WHERE id = $1 AND deleted_flag = FALSE
        """
        row = await conn.fetchrow(query, blog_id)
        if not row:
            return None
        
        # Assuming your tags are stored as an array or JSON in the DB
        return BlogResponse(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            image=row["image"],
            tags=row["tags"],  # adjust if stored as JSON string (parse if needed)
            contents=row["contents"],
        )
