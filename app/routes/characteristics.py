from fastapi import APIRouter, HTTPException

from app.models import Characteristic
from app.schemas.characteristics import CharCreateModel, CharUpdateModel
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/characteristics")


@router.get("/")
async def get_characteristics(page: int=0, limit: int = 50):
    return {"results": await Characteristic.all().limit(limit).offset(page * limit),
            "count": await Characteristic.all().count()}


@router.get("/{char_id}")
async def get_characteristic(char_id: int):
    return await Characteristic.get_or_none(id=char_id)


@router.post("/")
async def create_characteristic(data: CharCreateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    return await Characteristic.create(**data.model_dump())


@router.patch("/{char_id}")
async def update_characteristic(char_id: int, data: CharUpdateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    if (char := await Characteristic.get_or_none(id=char_id)) is None:
        raise HTTPException(status_code=404, detail="Unknown characteristic!")

    await char.update(**data.model_dump(exclude_defaults=True))
    return char


@router.delete("/{char_id}", status_code=204)
async def delete_characteristic(char_id: int, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.MANAGE_PRODUCTS):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    await Characteristic.filter(id=char_id).delete()
