# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from datetime import date, timedelta, datetime
from .models import Racehorse, Jockey, Race, Participation

User = get_user_model()

class BaseTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.client = APIClient()

        # Authenticate client for protected actions
        self.client.login(username="testuser", password="testpass")

        # Create initial Racehorse and Jockey
        self.racehorse = Racehorse.objects.create(
            name="Lightning Bolt",
            birth_date=date(2018, 5, 20),
            breed="Thoroughbred",
            gender=Racehorse.GenderChoices.MALE,
        )
        self.jockey = Jockey.objects.create(
            name="John Doe",
            birth_date=date(1990, 3, 15),
            height_cm=175,
            weight_kg=65
        )
        self.race = Race.objects.create(
            name="Grand Derby",
            date=date.today(),
            location="Churchill Downs",
            track_configuration=Race.TrackConfiguration.LEFT_HANDED,
            track_condition="F",
            classification=Race.Classification.GRADE_1,
            season=Race.Season.SUMMER,
            track_length=1200,
            prize_money=100000,
            currency="USD",
            track_surface=Race.TrackSurface.DIRT
        )
        self.participation = Participation.objects.create(
            racehorse=self.racehorse,
            jockey=self.jockey,
            race=self.race,
            position=1,
            finish_time=timedelta(minutes=1, seconds=10),
            margin=0,
            odds=2.5
        )


class RacehorseTests(BaseTestCase):
    def test_list_racehorses(self):
        url = reverse('racehorse-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # RacehorseViewSet has pagination_class = None, so response.data is a list
        self.assertIn("Lightning Bolt", [r['name'] for r in response.data])

    def test_create_racehorse_authenticated(self):
        url = reverse('racehorse-list')
        data = {
            "name": "Thunder Storm",
            "birth_date": "2019-06-01",
            "breed": "Arabian",
            "gender": "Female",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Racehorse.objects.filter(name="Thunder Storm").exists())

    def test_update_racehorse(self):
        url = reverse('racehorse-detail', args=[self.racehorse.id])
        data = {"name": "Lightning Updated"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.racehorse.refresh_from_db()
        self.assertEqual(self.racehorse.name, "Lightning Updated")

    def test_delete_racehorse(self):
        url = reverse('racehorse-detail', args=[self.racehorse.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Racehorse.objects.filter(id=self.racehorse.id).exists())


class JockeyTests(BaseTestCase):
    def test_list_jockeys(self):
        url = reverse('jockey-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JockeyViewSet uses pagination, so response.data has 'results' key
        self.assertIn("John Doe", [j['name'] for j in response.data['results']])

    def test_create_jockey_authenticated(self):
        url = reverse('jockey-list')
        data = {"name": "Jane Rider", "birth_date": "1992-08-10", "height_cm": 165, "weight_kg": 55}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Jockey.objects.filter(name="Jane Rider").exists())


class RaceTests(BaseTestCase):
    def test_list_races(self):
        url = reverse('race-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # RaceViewSet uses pagination, so response.data has 'results' key
        self.assertIn("Grand Derby", [r['name'] for r in response.data['results']])

    def test_create_race_valid(self):
        url = reverse('race-list')
        data = {
            "name": "Summer Stakes",
            "date": str(date.today()),
            "location": "Ascot",
            "track_configuration": "R",
            "track_condition": "F",
            "classification": "G2",
            "season": "SU",
            "track_length": 1400,
            "prize_money": 50000,
            "currency": "USD",
            "track_surface": "D"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Race.objects.filter(name="Summer Stakes").exists())

    def test_create_race_invalid_condition(self):
        url = reverse('race-list')
        data = {
            "name": "Invalid Race",
            "date": str(date.today()),
            "location": "Fake Track",
            "track_configuration": "L",
            "track_condition": "FM",  # invalid for DIRT
            "classification": "G3",
            "season": "FA",
            "track_length": 1200,
            "prize_money": 10000,
            "currency": "USD",
            "track_surface": "D"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ParticipationTests(BaseTestCase):
    def test_list_participations(self):
        url = reverse('participation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ParticipationViewSet uses pagination, so response.data has 'results' key
        self.assertIn("Lightning Bolt", [p['racehorse_name'] for p in response.data['results']])

    def test_create_participation_nested(self):
        url = reverse('participation-list')
        data = {
            "racehorse": {"name": "New Horse", "birth_date": "2020-01-01", "breed": "Arabian", "gender": "Male"},
            "jockey": {"name": "New Jockey", "birth_date": "1995-01-01"},
            "race": {
                "name": "New Race",
                "date": str(date.today()),
                "location": "New Track",
                # Add required fields for Race model
                "track_configuration": "L",
                "track_condition": "F",
                "classification": "G3",
                "season": "SU",
                "track_length": 1200,
                "prize_money": 25000,
                "currency": "USD",
                "track_surface": "D"
            },
            "position": 1,
            "finish_time": "0:01:05",
            "margin": 0,
            "odds": 3.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Participation.objects.filter(racehorse__name="New Horse").exists())


class UserTests(BaseTestCase):
    def test_list_users(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # UserViewSet uses pagination, so response.data has 'results' key
        self.assertIn("testuser", [u['username'] for u in response.data['results']])

    def test_create_user(self):
        url = reverse('user-list')
        data = {"username": "newuser", "email": "new@example.com", "password": "newpass"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_update_user(self):
        url = reverse('user-detail', args=[self.user.id])
        data = {"email": "updated@example.com", "password": "newpass2"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")
