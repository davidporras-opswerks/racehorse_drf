from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RacehorseViewSet, JockeyViewSet, RaceViewSet, ParticipationViewSet, UserViewSet

router = DefaultRouter()
router.register(r'racehorses', RacehorseViewSet, basename='racehorse')
router.register(r'jockeys', JockeyViewSet, basename='jockey')
router.register(r'races', RaceViewSet, basename='race')
router.register(r'participations', ParticipationViewSet, basename='participation')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
