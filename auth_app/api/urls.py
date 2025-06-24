from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegesistrationView, CustomLogin
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(),
         name='userprofile-detail'),
    path('registration/', RegesistrationView.as_view(),
         name='registration-view'),
    path('login/', CustomLogin.as_view(), name='login-view'),
]
