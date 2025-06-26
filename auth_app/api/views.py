from rest_framework import generics, status
from auth_app.models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer


class UserProfileList(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class CustomLogin(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'fullname': user.username,
                'email': user.email,
                'token': token.key
            }
        else:
            data = serializer.errors

        return Response(data)


class RegesistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserProfileSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'fullname': saved_account.username,
                'email': saved_account.email,
                'token': token.key,
                'user_id': saved_account.id
            }

            headers = {
                'Status-Message': 'User wurde erfolgreich erstellt'
            }

            return Response(serializer.data, status=status.HTTP_201_CREATED,  headers=headers)
        else:
            headers = {
                'Status-Message': 'Ungültige Anfragedaten.'
            }
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST,  headers=headers)
