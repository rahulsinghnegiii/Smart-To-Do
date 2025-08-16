from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, ContextEntryViewSet, AIAnalysisView

# Create router and register viewsets
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'context', ContextEntryViewSet, basename='contextentry')
router.register(r'ai', AIAnalysisView, basename='ai')

urlpatterns = [
    path('api/', include(router.urls)),
]
