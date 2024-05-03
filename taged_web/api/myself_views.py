from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer


@api_view(["GET"])
def get_myself_api_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
