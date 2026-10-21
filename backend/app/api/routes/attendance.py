from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/attendance",tags=["S4-07 Attendance"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-07 chưa được overlay.")
