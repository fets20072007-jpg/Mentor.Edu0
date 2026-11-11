from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.database.models import User
from app.security.auth import get_current_user
router = APIRouter(prefix="/uploads", tags=["Uploads"])
ROOT = Path(__file__).resolve().parents[4] / "uploads"
ROOT.mkdir(parents=True, exist_ok=True)
@router.post("/file")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    data = await file.read()
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(413, "Arquivo excede 12 MB.")
    suffix = Path(file.filename or "arquivo").suffix.lower()[:12]
    name = f"{current_user.id}_{uuid4().hex}{suffix}"
    (ROOT / name).write_bytes(data)
    return {"arquivo": f"/uploads/{name}", "nome_original": file.filename, "tipo": file.content_type}
