from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_image(
    file: UploadFile,
    folder: str
):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed"
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 5MB"
        )

    filename = f"{uuid4().hex}{extension}"

    upload_dir = Path("uploads") / folder
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return f"/uploads/{folder}/{filename}"
