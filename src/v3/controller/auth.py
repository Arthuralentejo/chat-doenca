from fastapi import APIRouter, HTTPException, Request, status
from loguru import logger
from base import Response, Services
from v3.schemas.auth_schema import AuthSchema

router = APIRouter(
    tags="Auth"
)


services = Services()


@router.post("/{id}")
async def login_user(id: int, auth_data: AuthSchema, request: Request):
    try:
        if not id:
            Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, error="Empty id"
            )

        if not auth_data.password:
            Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, error="Empty password"
            )

        token = services.auth_service.login(id, auth_data.password)
        return Response.create_response(201, "User login", {"token": token})

    except Exception as e:
        logger.error(f"Error to login user {id}: {e}")
        Response.create_error_response(status=500, error=str(e))


@router.delete("/{id}")
async def logout_user(id: int, request: Request):
    try:
        if not id:
            Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, error="Empty id"
            )

        if services.auth_service.logout(id):
            return Response.create_response(201, "User logout", {"result": True})
        else:
            Response.create_error_response(
                status=status.HTTP_404_NOT_FOUND, error="User not found"
            )
    except Exception as e:
        logger.error(f"Error to logout user {id}: {e}")
        Response.create_error_response(status=500, error=str(e))
