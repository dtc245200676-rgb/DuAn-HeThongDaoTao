from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/holidays",tags=["S4-01 Holidays"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-01B chưa được overlay.")
