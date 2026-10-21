from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/absence-requests",tags=["S4-08 Absence Requests"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-08 chưa được overlay.")
