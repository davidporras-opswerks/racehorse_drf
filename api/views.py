from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Racehorse, Jockey, Race, Participation
from .serializers import (
        RacehorseSerializer, RacehorseWriteSerializer, JockeySerializer, 
        JockeyWriteSerializer, RaceSerializer, RaceWriteSerializer,
        ParticipationSerializer, ParticipationWriteSerializer
    )

from rest_framework.throttling import ScopedRateThrottle

class RacehorseViewSet(viewsets.ModelViewSet):
    throttle_scope = 'racehorses'
    throttle_classes = [ScopedRateThrottle]
    queryset = Racehorse.objects.order_by('pk')
    serializer_class = RacehorseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @method_decorator(cache_page(60 * 15, key_prefix='racehorse_list'))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RacehorseWriteSerializer
        return RacehorseSerializer
    
class JockeyViewSet(viewsets.ModelViewSet):
    throttle_scope = 'jockeys'
    throttle_classes = [ScopedRateThrottle]
    queryset = Jockey.objects.prefetch_related('participations').all()
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 15, key_prefix='jockey_list'))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JockeyWriteSerializer
        return JockeySerializer
    
class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.prefetch_related('participations').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RaceWriteSerializer
        return RaceSerializer

class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.select_related('racehorse', 'race', 'jockey').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ParticipationWriteSerializer
        return ParticipationSerializer
