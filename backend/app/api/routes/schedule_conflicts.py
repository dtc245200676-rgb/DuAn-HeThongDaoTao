from fastapi import APIRouter, HTTPException
router=APIRouter(prefix="/api/s4/conflicts",tags=["S4-02 Conflicts"])
@router.get("/placeholder")
def placeholder():
    raise HTTPException(501,"S4-02 chưa được overlay.")
