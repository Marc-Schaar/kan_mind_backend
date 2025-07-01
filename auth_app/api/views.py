from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import UserSerializer, RegistrationSerializer


class UserProfileList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomLogin(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        data = {}

        try:
            user_obj = User.objects.get(email=email)
        except:
            return Response(
                {"error": "Email ist nicht vergeben"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=user_obj.username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "fullname": user.username,
                "email": user.email,
                "token": token.key,
                "user_id": user.id,
            }
            headers = {"Status-Message": "Erfolgreiche Anmeldung."}
            return Response(data, headers=headers, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST
            )


class RegesistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                "fullname": saved_account.username,
                "email": saved_account.email,
                "token": token.key,
                "user_id": saved_account.id,
            }

            headers = {"Status-Message": "User wurde erfolgreich erstellt"}
            return Response(data, headers=headers, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Ungültige Anfragedaten."}, status=status.HTTP_400_BAD_REQUEST
            )
