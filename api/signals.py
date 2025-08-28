from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.models import Racehorse, Jockey, Race, Participation
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Racehorse)
def invalidate_racehorse_cache(sender, instance, **kwargs):
    """
        Invalidate racehorse list caches when a racehorse is created, updated, or deleted
    """
    print("Clearing racehorse cache")

    # Clear racehorse list caches
    cache.clear()

@receiver([post_save, post_delete], sender=Jockey)
def invalidate_jockey_cache(sender, instance, **kwargs):
    """
        Invalidate jockey list caches when a jockey is created, updated, or deleted
    """
    print("Clearing jockey cache")

    # Clear jockey list caches
    cache.delete_pattern('*jockey_list*')

@receiver([post_save, post_delete], sender=Race)
def invalidate_race_cache(sender, instance, **kwargs):
    """
        Invalidate race list caches when a race is created, updated, or deleted
    """
    print("Clearing race cache")

    # Clear race list caches
    cache.delete_pattern('*race_list*')

@receiver([post_save, post_delete], sender=Participation)
def invalidate_participation_cache(sender, instance, **kwargs):
    """
        Invalidate participation list caches when a participation is created, updated, or deleted
    """
    print("Clearing participation cache")

    # Clear participation list caches
    cache.delete_pattern('*participation_list*')

