from pathlib import Path
from uuid import uuid4
import hashlib

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.biometric.image_utils import load_rgb_image
from app.biometric.pretrained import get_encoder
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["animals"])


@router.post("/animals/register")
async def register_animal(
    animal_code: str = Form(...),
    species: str = Form("cattle"),
    breed: str | None = Form(None),
    sex: str | None = Form(None),
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    animal_code = animal_code.strip()
    if not animal_code:
        raise HTTPException(400, "animal_code is required")
    if not 3 <= len(images) <= 5:
        raise HTTPException(400, "Please upload 3 to 5 reference images for this PoC")

    root = settings.storage_dir / "original"
    root.mkdir(parents=True, exist_ok=True)
    saved_paths = []

    try:
        existing = db.execute(
            text("SELECT id FROM animals WHERE animal_code=:code"),
            {"code": animal_code},
        ).first()
        if existing:
            raise HTTPException(409, "animal_code already exists")

        result = db.execute(text("""
            INSERT INTO animals (animal_code, species, breed, sex)
            VALUES (:code, :species, :breed, :sex) RETURNING id
        """), {"code": animal_code, "species": species, "breed": breed, "sex": sex})
        animal_id = result.scalar_one()

        encoder = get_encoder()
        for upload in images:
            raw = await upload.read()
            if not raw or len(raw) > settings.max_image_mb * 1024 * 1024:
                raise HTTPException(413, f"Each image must be under {settings.max_image_mb} MB")
            image = load_rgb_image(raw)
            embedding = encoder.encode(image)
            filename = f"{uuid4().hex}.jpg"
            path = root / filename
            image.save(path, format="JPEG", quality=95)
            saved_paths.append(path)
            relative_path = path.as_posix()
            digest = hashlib.sha256(raw).hexdigest()
            image_id = db.execute(text("""
                INSERT INTO animal_images (animal_id, image_path, original_filename, sha256)
                VALUES (:animal_id, :path, :original, :digest) RETURNING id
            """), {
                "animal_id": animal_id, "path": relative_path,
                "original": upload.filename, "digest": digest,
            }).scalar_one()
            vector_text = "[" + ",".join(map(str, embedding.tolist())) + "]"
            db.execute(text("""
                INSERT INTO biometric_embeddings
                    (animal_id, image_id, embedding, model_version)
                VALUES (:animal_id, :image_id, CAST(:embedding AS vector), :model)
            """), {
                "animal_id": animal_id, "image_id": image_id,
                "embedding": vector_text, "model": settings.model_version,
            })

        db.commit()
        return {
            "animal_id": animal_id,
            "animal_code": animal_code,
            "images_registered": len(images),
            "model_version": settings.model_version,
            "message": "Animal registered. Identification performance is not yet validated.",
        }
    except HTTPException:
        db.rollback()
        for path in saved_paths:
            path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        db.rollback()
        for path in saved_paths:
            path.unlink(missing_ok=True)
        raise HTTPException(500, "Registration failed; check server logs.") from exc


@router.get("/animals")
def list_animals(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT a.id, a.animal_code, a.species, a.breed, a.sex, a.created_at,
               COUNT(i.id) AS image_count
        FROM animals a LEFT JOIN animal_images i ON i.animal_id=a.id
        GROUP BY a.id ORDER BY a.created_at DESC
    """)).mappings().all()
    return [dict(row) for row in rows]


@router.get("/animals/{animal_id}")
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("""
        SELECT a.id, a.animal_code, a.species, a.breed, a.sex, a.created_at,
               COUNT(i.id) AS image_count
        FROM animals a LEFT JOIN animal_images i ON i.animal_id=a.id
        WHERE a.id=:id GROUP BY a.id
    """), {"id": animal_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Animal not found")
    return dict(row)
