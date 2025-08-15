from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Racehorse, Jockey, Race, Participation
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Populate the database with sample Umamusume racehorses, jockeys, and races"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database population...")

        # --- 1. Create Racehorses ---
        horses_data = [
            {"name": "Special Week", "birth_date": date(1995, 5, 2), "breed": "Thoroughbred", "gender": Racehorse.GenderChoices.MALE, "country": "Japan"},
            {"name": "Silence Suzuka", "birth_date": date(1994, 5, 1), "breed": "Thoroughbred", "gender": Racehorse.GenderChoices.MALE, "country": "Japan"},
            {"name": "Tokai Teio", "birth_date": date(1988, 4, 20), "breed": "Thoroughbred", "gender": Racehorse.GenderChoices.MALE, "country": "Japan"},
            {"name": "Mejiro McQueen", "birth_date": date(1987, 4, 3), "breed": "Thoroughbred", "gender": Racehorse.GenderChoices.MALE, "country": "Japan"},
            {"name": "Oguri Cap", "birth_date": date(1985, 3, 27), "breed": "Thoroughbred", "gender": Racehorse.GenderChoices.MALE, "country": "Japan"},
        ]
        horses = []
        for horse_data in horses_data:
            horse, _ = Racehorse.objects.get_or_create(**horse_data)
            horses.append(horse)
        self.stdout.write(f"Created {len(horses)} racehorses.")

        # --- 2. Create Jockeys ---
        jockey_names = ["Yutaka Take", "Katsumi Ando", "Hironobu Tanabe", "Mirco Demuro", "Christophe Lemaire"]
        jockeys = []
        for name in jockey_names:
            jockey, _ = Jockey.objects.get_or_create(name=name)
            jockeys.append(jockey)
        self.stdout.write(f"Created {len(jockeys)} jockeys.")

        # --- 3. Create Races ---
        races_data = [
            {
                "name": "Japan Cup",
                "date": date.today() - timedelta(days=30),
                "location": "Tokyo Racecourse",
                "track_configuration": Race.TrackConfiguration.LEFT_HANDED,
                "track_condition": Race.TrackCondition.FIRM,  # short code 'FM'
                "classification": Race.Classification.GRADE_1,
                "season": Race.Season.FALL,
                "track_length": 2400,
                "track_surface": Race.TrackSurface.TURF,
                "prize_money": 5000000,
                "currency": "JPY",
            },
            {
                "name": "Takarazuka Kinen",
                "date": date.today() - timedelta(days=60),
                "location": "Hanshin Racecourse",
                "track_configuration": Race.TrackConfiguration.RIGHT_HANDED,
                "track_condition": Race.TrackCondition.GOOD,  # short code 'G'
                "classification": Race.Classification.GRADE_1,
                "season": Race.Season.SUMMER,
                "track_length": 2200,
                "track_surface": Race.TrackSurface.TURF,
                "prize_money": 3500000,
                "currency": "JPY",
            },
        ]
        races = []
        for race_data in races_data:
            race, _ = Race.objects.get_or_create(**race_data)
            races.append(race)
        self.stdout.write(f"Created {len(races)} races.")

        # --- 4. Create Participations ---
        for race in races:
            # Pick unique horses and unique jockeys for this race
            participants = random.sample(horses, 3)
            selected_jockeys = random.sample(jockeys, 3)

            positions = list(range(1, len(participants) + 1))
            random.shuffle(positions)

            for i, horse in enumerate(participants):
                Participation.objects.get_or_create(
                    racehorse=horse,
                    race=race,
                    jockey=selected_jockeys[i],
                    position=positions[i]
                )

        self.stdout.write("Created race participations.")
        self.stdout.write(self.style.SUCCESS("Database population complete!"))


