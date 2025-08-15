import logging
from rest_framework import viewsets, filters
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
from api.filters import ActiveRacehorseFilterBackend, RacehorseFilter, JockeyFilter, RaceFilter, ParticipationFilter
from api.tasks import send_thank_you_email

# Set up logger
logger = logging.getLogger(__name__)

class RacehorseViewSet(viewsets.ModelViewSet):
    throttle_scope = 'racehorses'
    throttle_classes = [ScopedRateThrottle]
    queryset = Racehorse.objects.order_by('pk')
    pagination_class = None
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        ActiveRacehorseFilterBackend
    ]
    filterset_class = RacehorseFilter
    search_fields = ['name']
    ordering_fields = ['name', 'birth_date', 'pk']

    def list(self, request, *args, **kwargs):
        logger.info(f"Racehorse list requested by user: {request.user}")
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

    def perform_create(self, serializer):
        user_info = f"{self.request.user} (authenticated: {self.request.user.is_authenticated})"
        logger.info(f"Creating racehorse for user: {user_info}")
        racehorse = serializer.save()
        logger.info(f"Racehorse created: {racehorse.name} (ID: {racehorse.id}) - {racehorse.breed}")

class JockeyViewSet(viewsets.ModelViewSet):
    throttle_scope = 'jockeys'
    throttle_classes = [ScopedRateThrottle]
    queryset = Jockey.objects.prefetch_related('participations').order_by('pk')
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = JockeyFilter
    search_fields = ['name']
    ordering_fields = ['name', 'birth_date']

    def list(self, request, *args, **kwargs):
        logger.info(f"Jockey list requested by user: {request.user}")
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

    def perform_create(self, serializer):
        user_info = f"{self.request.user} (authenticated: {self.request.user.is_authenticated})"
        logger.info(f"Creating jockey for user: {user_info}")
        jockey = serializer.save()
        logger.info(f"Jockey created: {jockey.name} (ID: {jockey.id})")


class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.prefetch_related('participations').order_by('pk')
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RaceFilter
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'date', 'track_length', 'prize_money']

    def list(self, request, *args, **kwargs):
        logger.info(f"Race list requested by user: {request.user}")
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

    def perform_create(self, serializer):
        user_info = f"{self.request.user} (authenticated: {self.request.user.is_authenticated})"
        logger.info(f"Creating race for user: {user_info}")
        race = serializer.save()
        logger.info(f"Race created: {race.name} (ID: {race.id}) at {race.location}")

class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.select_related('racehorse', 'race', 'jockey').order_by('pk')
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ParticipationFilter
    serializer_class = ParticipationSerializer
    
    def list(self, request, *args, **kwargs):
        logger.info(f"Participation list requested by user: {request.user}")
        # Generate a cache key per user (or 'anon' if not logged in)
        user_key = f'participation_list_user_{request.user.id if request.user.is_authenticated else "anon"}'
        decorated = cache_page(60*15, key_prefix=user_key)(super().list)
        return decorated(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        user_info = f"{self.request.user} (authenticated: {self.request.user.is_authenticated})"
        logger.info(f"Creating participation for user: {user_info}")
        participation = serializer.save()
        logger.info(f"Participation created: {participation.id} - Sending thank you email to {self.request.user.email}")
        send_thank_you_email.delay(participation.id, self.request.user.email)  # send email asynchronously
    
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

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.action == 'create' or self.action == 'update':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return UserWriteSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        logger.info(f"User list requested by user: {request.user}")
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        user_info = f"{self.request.user} (authenticated: {self.request.user.is_authenticated})"
        logger.info(f"Creating user - requested by: {user_info}")
        user = serializer.save()
        logger.info(f"User created: {user.username} (ID: {user.id}) - {user.email}")