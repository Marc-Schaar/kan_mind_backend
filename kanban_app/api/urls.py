from django.urls import path
from kanban_app.api.views import BoardListView, BoardDetailView, TaskListView, TaskDetailView, TaskAssignedToMeView, TaskReviewingView, CommentOfTasksList, CommentOfTasksListDetail, EmailCheckView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/',
         CommentOfTasksList.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:pk>/',
         CommentOfTasksListDetail.as_view(), name='task-comments-detail'),
    path('tasks/assigned-to-me/', TaskAssignedToMeView.as_view(),
         name='task-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewingView.as_view(), name='task-reviewing'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
