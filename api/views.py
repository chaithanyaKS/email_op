from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(["GET"])
def ping(request: Request) -> Response:
    return Response({"detail": "Service is up and running"})
