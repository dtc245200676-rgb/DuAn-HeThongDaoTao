import io,os,uuid
from pathlib import Path
from fastapi import APIRouter,Depends,File,HTTPException,UploadFile
from PIL import Image,ImageOps
from sqlalchemy.orm import Session
from app.api.deps import AuthContext,get_current_context
from app.api.routes.profile_common import serialize_profile
from app.db.database import get_db
router=APIRouter(prefix="/api/profile",tags=["S2-03 Avatar"])
MAX_AVATAR_BYTES=2*1024*1024;ALLOWED_TYPES={"image/jpeg","image/png"};UPLOAD_DIR=Path(os.getenv("AVATAR_UPLOAD_DIR","uploads/avatars"))
@router.post("/avatar")
async def upload_avatar(file:UploadFile=File(...),context:AuthContext=Depends(get_current_context),db:Session=Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES: raise HTTPException(422,"Ảnh đại diện chỉ chấp nhận JPG hoặc PNG.")
    raw=await file.read(MAX_AVATAR_BYTES+1)
    if len(raw)>MAX_AVATAR_BYTES: raise HTTPException(422,"Dung lượng ảnh đại diện không được vượt quá 2MB.")
    try: image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc: raise HTTPException(422,"Tệp ảnh không hợp lệ.") from exc
    square=ImageOps.fit(image,(512,512),method=Image.Resampling.LANCZOS);thumb=ImageOps.fit(image,(128,128),method=Image.Resampling.LANCZOS);UPLOAD_DIR.mkdir(parents=True,exist_ok=True);stem=f"user-{context.user.id}-{uuid.uuid4().hex}";avatar=UPLOAD_DIR/f"{stem}.jpg";thumbfile=UPLOAD_DIR/f"{stem}-thumb.jpg";square.save(avatar,"JPEG",quality=88,optimize=True);thumb.save(thumbfile,"JPEG",quality=85,optimize=True)
    context.user.avatar_path=avatar.as_posix();context.user.avatar_thumbnail_path=thumbfile.as_posix();db.commit();db.refresh(context.user);return serialize_profile(context.user)
