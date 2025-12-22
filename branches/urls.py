from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, NearestBranchView

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('branches/nearest/', NearestBranchView.as_view(), name='nearest-branch'),
    path('', include(router.urls)),
]
