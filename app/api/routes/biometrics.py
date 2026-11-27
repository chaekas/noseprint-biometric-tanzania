from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.biometric.image_utils import load_rgb_image
from app.biometric.matching import best_animal_match
from app.biometric.pretrained import get_encoder
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["biometrics"])


@router.post("/biometrics/identify")
async def identify_animal(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await image.read()
    if not raw or len(raw) > settings.max_image_mb * 1024 * 1024:
        raise HTTPException(413, f"Image must be under {settings.max_image_mb} MB")
    try:
        pil_image = load_rgb_image(raw)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    query_embedding = get_encoder().encode(pil_image)
    rows = db.execute(text("""
        SELECT e.animal_id, a.animal_code, e.embedding::text
        FROM biometric_embeddings e
        JOIN animals a ON a.id=e.animal_id
        WHERE e.model_version=:model
    """), {"model": settings.model_version}).all()

    parsed_rows = []
    for animal_id, animal_code, vector in rows:
        parsed_rows.append((animal_id, animal_code, [float(v) for v in vector.strip("[]").split(",")]))

    candidate = best_animal_match(query_embedding, parsed_rows)
    if candidate is None:
        decision = "unknown"
    elif candidate["similarity"] >= settings.match_threshold:
        decision = "candidate"
    else:
        decision = "unknown"

    query_path = settings.storage_dir / "queries" / f"{uuid4().hex}.jpg"
    query_path.parent.mkdir(parents=True, exist_ok=True)
    pil_image.save(query_path, format="JPEG", quality=90)

    db.execute(text("""
        INSERT INTO identification_logs
            (query_image_path, matched_animal_id, similarity_score, decision, model_version)
        VALUES (:path, :animal_id, :score, :decision, :model)
    """), {
        "path": query_path.as_posix(),
        "animal_id": candidate["animal_id"] if candidate and decision == "candidate" else None,
        "score": candidate["similarity"] if candidate else None,
        "decision": decision,
        "model": settings.model_version,
    })
    db.commit()

    return {
        "decision": decision,
        "candidate": candidate if decision == "candidate" else None,
        "best_candidate": candidate,
        "threshold": settings.match_threshold,
        "model_version": settings.model_version,
        "warning": "Candidate match only; score is not a probability or proof of identity.",
    }
