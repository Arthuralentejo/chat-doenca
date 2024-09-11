from fastapi import APIRouter, HTTPException, Request, Depends, status
from loguru import logger
from base import Services, Response
from domain.message import Message
from v3.schemas.message_schema import MessageSchema

router = APIRouter(tags="Message")

services = Services()

@router.post("/")
async def send_message(message: MessageSchema, request: Request):
    try:
        user_id = services.auth(request)

        if not user_id:
            Response.create_error_response(
                status=status.HTTP_401_UNAUTHORIZED,
                error="Unauthorized"
            )

        if not message.text:
            Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST, 
                error="Empty text"
            )

        user = services.user_service.get(user_id)            
        msg = Message(user, message.text)

        msg.set_id(services.message_service.send(msg))
        return Response.create_response(
            status=status.HTTP_201_CREATED, 
            message='Message sent', 
            data={'id': msg.get_id()})

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        Response.create_error_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            error=str(e))


@router.get("/")
async def get_messages(last: str = None, request: Request):
    try:
        user_id = services.auth(request)

        if not user_id:
            Response.create_error_response(
                status=status.HTTP_401_UNAUTHORIZED,
                error="Unauthorized"
            )

        messages = services.message_service.get_from_last(last)
        if messages is None:
            Response.create_error_response(
                status=status.HTTP_404_NOT_FOUND,
                error="Message not found"
            )

        return Response.create_response(
            status=status.HTTP_200_OK, 
            message='Message loaded', 
            data={'data': messages.ToJson()})

    except Exception as e:
        Response.create_error_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            error=str(e))


@router.get("/{id}")
async def get_message(id: int, request: Request):
    try:
        user_id = services.auth(request)

        if not user_id:
            Response.create_error_response(
                status=status.HTTP_401_UNAUTHORIZED,
                error="Unauthorized"
            )

        if id < 0:
            Response.create_error_response(
                status=status.HTTP_400_BAD_REQUEST,
                error="Invalid message index"
            )

        message = services.message_service.get(id)
        if message is None:
            return Response.create_error_response(
                status=status.HTTP_404_NOT_FOUND,
                error="Message not found"
            )
        
        return Response.create_response(
            status=status.HTTP_200_OK,
            message= 'Message loaded', 
            data={'data': message.ToJson()})

    except Exception as e:
        logger.error(f"Error getting message: {e}")
        Response.create_error_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            error=str(e))
