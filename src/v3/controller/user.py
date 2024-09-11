from fastapi import APIRouter, Request, status
from loguru import logger
from base import Response, Services
from v3.schemas.user_schema import UserSchema

router = APIRouter(tags=["User"])

services = Services()


@router.post("/")
async def create_user(user_data: UserSchema):
    try:
        if not user_data.name:
            return Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, error="Empty name"
            )

        if not user_data.password:
            return Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, error="Empty password"
            )

        user_id = services.user_service.create(user_data.name, user_data.password)
        return Response.create_response(
            status=status.HTTP_201_CREATED, message="User created", data={"id": user_id}
        )

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return Response.create_error_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, error=str(e)
        )


@router.get("/{id}")
async def get_user(id: int, request: Request):
    try:
        user_id = services.auth(request)

        if not user_id:
            return Response.create_error_response(
                status=status.HTTP_401_UNAUTHORIZED, error="Unauthorized"
            )

        user = services.user_service.get(id)
        if not user:
            return Response.create_error_response(
                status=status.HTTP_404_NOT_FOUND, error="User not found"
            )

        return Response.create_response(
            status=status.HTTP_200_OK,
            message="User loaded",
            data={"user": user.ToJson()},
        )

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return Response.create_error_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, error=str(e)
        )
