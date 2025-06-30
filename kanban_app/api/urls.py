from django.urls import path
from kanban_app.api.views import BoardListView, BoardDetailView, TaskListView, TaskDetailView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

]
