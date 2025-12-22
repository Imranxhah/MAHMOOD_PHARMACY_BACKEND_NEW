from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('prescriptions/upload/', PrescriptionViewSet.as_view({'post': 'create'}), name='prescription-upload'),
    path('', include(router.urls)),
]
