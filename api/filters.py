# api/filters.py
import django_filters
from api.models import Racehorse, Jockey, Race, Participation
from rest_framework import filters

class ActiveRacehorseFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_active=True)

class RacehorseFilter(django_filters.FilterSet):
    class Meta:
        model = Racehorse
        fields = {
            'name': ['iexact', 'icontains'],
            'breed': ['iexact', 'icontains'],
            'country': ['iexact', 'icontains'],
            'is_active': ['exact']
        }

class JockeyFilter(django_filters.FilterSet):
    class Meta:
        model = Jockey
        fields = {
            'name': ['iexact', 'icontains'],
        }

class RaceFilter(django_filters.FilterSet):
    class Meta:
        model = Race
        fields = {
            'name': ['iexact', 'icontains'],
            'location': ['iexact', 'icontains'],
            'track_surface': ['exact'],
            'classification': ['exact'],
            'season': ['exact'],
            'date': ['exact', 'lt', 'gt', 'range']
        }

class ParticipationFilter(django_filters.FilterSet):
    class Meta:
        model = Participation
        fields = {
            'racehorse__name': ['iexact', 'icontains'],
            'jockey__name': ['iexact', 'icontains'],
            'race__name': ['iexact', 'icontains'],
            'position': ['exact', 'lt', 'gt', 'range'],
        }
