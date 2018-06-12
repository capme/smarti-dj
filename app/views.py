from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def url1(request):
    return Response({'message': 'OK'}, 200)


@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def url2(request):
    return Response({'message': 'OK'}, 200)
