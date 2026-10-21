from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/timetable",tags=["S4-01 Timetable"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-01 chưa được overlay.")
