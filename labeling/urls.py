from rest_framework.routers import DefaultRouter
from django.urls import path, include

from labeling.views import DataItemViewSet, AnnotationViewSet, ValidationViewSet, UserViewSet, LabelViewSet

router = DefaultRouter()
router.register(r'labels', LabelViewSet, basename='label')
router.register(r'data-items', DataItemViewSet, basename='dataitem')
router.register(r'annotations', AnnotationViewSet, basename='annotation')
router.register(r'validations', ValidationViewSet, basename='validation')
router.register(r'users', UserViewSet, basename='user')
urlpatterns = [
    path('', include(router.urls)),
]