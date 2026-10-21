from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/schedule-changes",tags=["S4-03 Session Changes"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-03 chưa được overlay.")
