"""Phase 2 Image Storage Service.

Handles saving uploaded images to local disk for development.
Architecture is designed for easy replacement with S3, GCS, or Azure Blob in later phases.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile, HTTPException, status


# Supported MIME types for uploaded incident images
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}

# Allowed file extensions (secondary check)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Max image size: 10 MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024


class StorageService:
    """
    Local file-system image storage for Phase 2.

    Future phases may replace this implementation with a cloud provider
    (S3, GCS, Azure Blob) by swapping the `save_image` method.
    The interface contract — accepts `UploadFile`, returns `str` (URL/path) — must remain.
    """

    def __init__(self, upload_dir: str):
        """
        Args:
            upload_dir: Absolute path to the root upload directory.
        """
        self.upload_dir = Path(upload_dir)
        self.incidents_dir = self.upload_dir / "incidents"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create upload directories if they do not exist."""
        self.incidents_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file: UploadFile) -> Tuple[str, str]:
        """
        Validate and persist an uploaded image file.

        Args:
            file: The uploaded file from FastAPI's multipart parser.

        Returns:
            Tuple of (stored_filename, relative_url_path).

        Raises:
            HTTPException 400 if validation fails.
            HTTPException 500 if the file cannot be written.
        """
        await self._validate_image(file)

        # Generate a unique filename to prevent collisions and path traversal
        original_ext = Path(file.filename or "image.jpg").suffix.lower()
        if original_ext not in ALLOWED_EXTENSIONS:
            original_ext = ".jpg"

        unique_name = f"{uuid.uuid4().hex}{original_ext}"
        dest_path = self.incidents_dir / unique_name

        try:
            # Reset file pointer after validation read
            await file.seek(0)
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except OSError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded image. Please try again.",
            ) from exc

        # Return the relative URL path served via StaticFiles
        relative_url = f"/uploads/incidents/{unique_name}"
        return unique_name, relative_url

    async def _validate_image(self, file: UploadFile) -> None:
        """
        Validate image MIME type and file size.

        Raises:
            HTTPException 400 if the file is missing, too large, or unsupported.
        """
        if file is None or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is required.",
            )

        # MIME type check
        content_type = (file.content_type or "").lower()
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{content_type}'. Supported: JPEG, PNG.",
            )

        # Size check: read up to MAX + 1 bytes to detect oversized files
        content = await file.read(MAX_IMAGE_SIZE_BYTES + 1)
        if len(content) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image file too large. Maximum allowed size is {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB.",
            )

        # File must not be empty
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is empty.",
            )

        # Seek back to start for the actual save operation
        await file.seek(0)
