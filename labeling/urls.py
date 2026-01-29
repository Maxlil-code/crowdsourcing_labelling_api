from rest_framework.routers import DefaultRouter
from django.urls import path, include

from labeling.views import DataItemViewSet, AnnotationViewSet, ValidationViewSet

router = DefaultRouter()
router.register(r'data-items', DataItemViewSet, basename='dataitem')
router.register(r'annotations', AnnotationViewSet, basename='annotation')
router.register(r'validations', ValidationViewSet, basename='validation')

urlpatterns = [
    path('', include(router.urls)),
]