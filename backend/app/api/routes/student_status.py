from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/student-status",tags=["S4-06 Student Status"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-06 chưa được overlay.")
