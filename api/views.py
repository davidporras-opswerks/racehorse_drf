from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import ScopedRateThrottle

from .models import Racehorse, Jockey, Race, Participation, User
from .serializers import (
    RacehorseSerializer, RacehorseWriteSerializer, 
    JockeySerializer, JockeyWriteSerializer, 
    RaceSerializer, RaceWriteSerializer,
    ParticipationSerializer, ParticipationWriteSerializer,
    UserSerializer, UserWriteSerializer
)


class RacehorseViewSet(viewsets.ModelViewSet):
    throttle_scope = 'racehorses'
    throttle_classes = [ScopedRateThrottle]
    queryset = Racehorse.objects.order_by('pk')
    serializer_class = RacehorseSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        # Generate a cache key per user (or 'anon' if not logged in)
        user_key = f'racehorse_list_user_{request.user.id if request.user.is_authenticated else "anon"}'
        decorated = cache_page(60*15, key_prefix=user_key)(super().list)
        return decorated(request, *args, **kwargs)

    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'POST', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RacehorseWriteSerializer
        return RacehorseSerializer

class JockeyViewSet(viewsets.ModelViewSet):
    throttle_scope = 'jockeys'
    throttle_classes = [ScopedRateThrottle]
    queryset = Jockey.objects.prefetch_related('participations').all()

    def list(self, request, *args, **kwargs):
        # Generate a cache key per user (or 'anon' if not logged in)
        user_key = f'jockey_list_user_{request.user.id if request.user.is_authenticated else "anon"}'
        decorated = cache_page(60*15, key_prefix=user_key)(super().list)
        return decorated(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)  # simulate delay
        return super().get_queryset()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'POST', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JockeyWriteSerializer
        return JockeySerializer


class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.prefetch_related('participations').all()

    def list(self, request, *args, **kwargs):
        # Generate a cache key per user (or 'anon' if not logged in)
        user_key = f'race_list_user_{request.user.id if request.user.is_authenticated else "anon"}'
        decorated = cache_page(60*15, key_prefix=user_key)(super().list)
        return decorated(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)  # simulate delay
        return super().get_queryset()
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'POST', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RaceWriteSerializer
        return RaceSerializer

class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.select_related('racehorse', 'race', 'jockey').all()
    
    def list(self, request, *args, **kwargs):
        # Generate a cache key per user (or 'anon' if not logged in)
        user_key = f'participation_list_user_{request.user.id if request.user.is_authenticated else "anon"}'
        decorated = cache_page(60*15, key_prefix=user_key)(super().list)
        return decorated(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)  # simulate delay
        return super().get_queryset()
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'POST', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ParticipationWriteSerializer
        return ParticipationSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('pk')
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.action == 'create' or self.action == 'update':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return UserWriteSerializer
        return super().get_serializer_class()