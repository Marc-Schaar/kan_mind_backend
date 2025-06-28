from django.urls import path, include
from kanban_app.api.views import BoardListView, BoardDetailView, TaskListView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskListView.as_view(), name='task-list'),

]
