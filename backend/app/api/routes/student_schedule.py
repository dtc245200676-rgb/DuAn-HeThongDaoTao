from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/student-schedule",tags=["S4-05 Student Schedule"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-05 chưa được overlay.")
