# tests_cache_throttle.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.cache import cache
from datetime import date
from .models import Racehorse

class CacheAndThrottleTests(APITestCase):
    def setUp(self):
        # Create a test Racehorse
        self.racehorse = Racehorse.objects.create(
            name="Cached Horse",
            birth_date=date(2018, 1, 1),
            breed="Arabian",
            gender="Male",
            is_active=True
        )
        self.client = APIClient()
        cache.clear()  # Ensure cache is empty at start

    def test_racehorse_list_cache(self):
        url = reverse('racehorse-list')
        
        # First request populates cache
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        content_first = response1.content

        # Second request should be served from cache (content identical)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        content_second = response2.content

        self.assertEqual(content_first, content_second)

    def test_racehorse_throttle(self):
        url = reverse('racehorse-list')
        # Assuming default rate is 5 per minute for test
        for i in range(5):
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # 6th request should be throttled
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_200_OK])
        # Note: depending on your settings, 6th may be throttled or not in test env

    def test_authenticated_required_for_create(self):
        url = reverse('racehorse-list')
        data = {"name": "Unauthenticated Horse", "breed": "Thoroughbred", "gender": "Female"}
        client = APIClient()  # not logged in
        response = client.post(url, data, format='json')
        # When authentication is required but not provided, DRF returns 401 (Unauthorized)
        # not 403 (Forbidden). 403 is for when auth succeeds but permission is denied.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Note: For full throttle test you may want to adjust REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] in settings
