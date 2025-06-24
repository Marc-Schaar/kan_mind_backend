from django.urls import path, include
from kanban_app.api.views import BoardViewset
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'boards', BoardViewset)

urlpatterns = [
    path('', include(router.urls)),]
