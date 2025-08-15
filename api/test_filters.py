# tests_filters.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from datetime import date
from .models import Racehorse, Jockey, Race

class FilterTests(APITestCase):
    def setUp(self):
        # Create test Racehorses
        self.active_horse = Racehorse.objects.create(
            name="Active Horse", birth_date=date(2018, 1, 1), breed="Arabian", gender="Male", is_active=True
        )
        self.inactive_horse = Racehorse.objects.create(
            name="Inactive Horse", birth_date=date(2019, 2, 2), breed="Thoroughbred", gender="Female", is_active=False
        )

        # Create test Jockeys
        self.jockey1 = Jockey.objects.create(name="Jockey One", birth_date=date(1990, 1, 1))
        self.jockey2 = Jockey.objects.create(name="Jockey Two", birth_date=date(1992, 2, 2))

        # Create test Races
        self.race1 = Race.objects.create(
            name="Race One",
            date=date.today(),
            location="Track A",
            track_configuration="L",
            track_condition="F",
            classification="G1",
            season="SU",
            track_length=1000,
            prize_money=50000,
            currency="USD",
            track_surface="D"
        )
        self.race2 = Race.objects.create(
            name="Race Two",
            date=date.today(),
            location="Track B",
            track_configuration="R",
            track_condition="F",
            classification="G2",
            season="FA",
            track_length=1200,
            prize_money=70000,
            currency="USD",
            track_surface="D"
        )
        self.client = APIClient()

    # Racehorse filters
    def test_racehorse_is_active_filter(self):
        url = reverse('racehorse-list')
        response = self.client.get(url + "?is_active=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r['name'] for r in response.data]
        self.assertIn("Active Horse", names)
        self.assertNotIn("Inactive Horse", names)

    def test_racehorse_search_name_icontains(self):
        url = reverse('racehorse-list')
        response = self.client.get(url + "?search=active")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r['name'] for r in response.data]
        self.assertIn("Active Horse", names)

    def test_racehorse_ordering_by_name(self):
        url = reverse('racehorse-list')
        response = self.client.get(url + "?ordering=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # RacehorseViewSet has pagination_class = None, so response.data is a list
        names = [r['name'] for r in response.data]
        # ActiveRacehorseFilterBackend filters out inactive horses, so only "Active Horse" should be returned
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], "Active Horse")

    # Jockey filters
    def test_jockey_search_name_icontains(self):
        url = reverse('jockey-list')
        response = self.client.get(url + "?search=one")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JockeyViewSet uses pagination, so response.data has 'results' key
        names = [j['name'] for j in response.data['results']]
        self.assertIn("Jockey One", names)
        self.assertNotIn("Jockey Two", names)

    # Race filters
    def test_race_filter_by_classification(self):
        url = reverse('race-list')
        response = self.client.get(url + "?classification=G1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # RaceViewSet uses pagination, so response.data has 'results' key
        names = [r['name'] for r in response.data['results']]
        self.assertIn("Race One", names)
        self.assertNotIn("Race Two", names)

    def test_race_ordering_by_track_length(self):
        url = reverse('race-list')
        response = self.client.get(url + "?ordering=-track_length")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # RaceViewSet uses pagination, so response.data has 'results' key
        lengths = [r['track_length'] for r in response.data['results']]
        self.assertEqual(lengths[0], 1200)
