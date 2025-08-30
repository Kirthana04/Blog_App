from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File
from typing import List, Optional
from services.db_service import get_db_pool
from schemas.blog_schemas import BlogCreate, BlogResponse
import services.blog_service as blog_service
from services.auth_service import get_current_user
import os
import uuid
import base64

router = APIRouter(prefix="/blogs", tags=["Blogs"])

UPLOAD_DIR = "uploads/images"

def save_image(base64_str: str) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    image_data = base64.b64decode(base64_str)
    filename = f"{uuid.uuid4()}.jpg"  # or detect extension if you want
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(image_data)

    # Return path relative to static mount point
    return f"/uploads/images/{filename}"

@router.post("/create", response_model=dict)
async def create_blog(blog: BlogCreate, user=Depends(get_current_user), pool=Depends(get_db_pool)):
    image_path = None
    if blog.image:
        image_path = save_image(blog.image)

    blog_data = await blog_service.create_blog(
        pool,
        user_id=user["user_id"],
        title=blog.title,
        description=blog.description,
        image=image_path,
        tags=blog.tags,
        contents=blog.contents
    )
    return {"message": "Blog created successfully", "blog_id": blog_data["id"]}

@router.get("/", response_model=List[BlogResponse])
async def list_blogs(pool=Depends(get_db_pool)):
    return await blog_service.get_all_blogs(pool)

@router.get("/my", response_model=List[BlogResponse])
async def list_user_blogs(user=Depends(get_current_user), pool=Depends(get_db_pool)):
    return await blog_service.get_user_blogs(pool, user_id=user["user_id"])

@router.put("/delete/{blog_id}", response_model=dict)
async def delete_blog(blog_id: int, user=Depends(get_current_user), pool=Depends(get_db_pool)):
    result = await blog_service.soft_delete_blog(pool, blog_id=blog_id, user_id=user["user_id"])
    if not result["success"]:
        # Instead of raising 404, return debug info:
        return {
            "success": False,
            "message": f"Blog with id {blog_id} not found or not owned by user {user['user_id']} or already deleted."
        }
    return result

@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: int, pool=Depends(get_db_pool)):
    blog = await blog_service.get_blog_by_id(pool, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog