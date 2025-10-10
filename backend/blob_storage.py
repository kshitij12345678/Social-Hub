import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import aiofiles

class BlobStorage:
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.posts_path = self.base_path / "posts"
        self.profiles_path = self.base_path / "profiles"
        
        # Create directories if they don't exist
        self.posts_path.mkdir(parents=True, exist_ok=True)
        self.profiles_path.mkdir(parents=True, exist_ok=True)
    
    async def save_post_media(self, file: UploadFile, user_id: int) -> str:
        """Save uploaded post media (image/video) and return file path"""
        # Generate unique filename
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = self.posts_path / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Return relative path for database storage
        return f"/uploads/posts/{unique_filename}"
    
    async def save_profile_picture(self, file: UploadFile, user_id: int) -> str:
        """Save uploaded profile picture and return file path"""
        # Generate unique filename
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"profile_{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = self.profiles_path / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Return relative path for database storage
        return f"/uploads/profiles/{unique_filename}"
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            # Convert relative path to absolute path
            if file_path.startswith("/uploads/"):
                full_path = self.base_path / file_path[9:]  # Remove "/uploads/" prefix
            else:
                full_path = Path(file_path)
            
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """Extract file extension from filename"""
        if not filename:
            return ""
        return Path(filename).suffix.lower()
    
    def get_file_type(self, filename: str) -> str:
        """Determine if file is image or video"""
        extension = self._get_file_extension(filename)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
        
        if extension in image_extensions:
            return 'image'
        elif extension in video_extensions:
            return 'video'
        else:
            return 'unknown'
    
    def is_valid_media_file(self, filename: str) -> bool:
        """Check if file is a valid media file"""
        return self.get_file_type(filename) in ['image', 'video']

# Global storage instance
blob_storage = BlobStorage()