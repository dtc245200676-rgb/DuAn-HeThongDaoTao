from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/calendar",tags=["S4-04 Calendar"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-04 chưa được overlay.")
