from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.admin.service import AdminService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def get_admin_service() -> AdminService:
    return AdminService()


AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


@router.post("/seed")
def seed_database(service: AdminServiceDep) -> dict[str, str]:
    return service.seed_database()
