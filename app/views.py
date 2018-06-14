from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication])
def url1(request):
    return Response({'message': 'OK'}, 200)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def url2(request):
    return Response({'message': 'OK'}, 200)
