from django.urls import path, include
from kanban_app.api.views import BoardListView, BoardDetailView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]
