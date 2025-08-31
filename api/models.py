from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        default="avatars/default.png"  # optional default image
    )

# This is the model for the Racehorse (name, age, breed)
class Racehorse(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'Male'
        FEMALE = 'Female'
        GELDING = 'Gelding'

    name = models.CharField(max_length=100, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, default=GenderChoices.MALE)
    country = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='racehorses/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_races(self):
        return self.participations.count()

    @property
    def total_wins(self):
        return self.participations.filter(position=1).count()

    @property
    def win_rate(self):
        return (self.total_wins / self.total_races) * 100 if self.total_races > 0 else 0

    @property
    def age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )

    def __str__(self):
        return self.name

# This is the model for the Jockey (name, age)
class Jockey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='jockeys/', blank=True, null=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    racehorses = models.ManyToManyField(Racehorse, through="Participation", related_name='jockeys')

    @property
    def age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @property
    def total_races(self):
        return self.participations.count()
    
    @property
    def total_wins(self):
        return self.participations.filter(position=1).count()
    
    @property
    def win_rate(self):
        return (self.total_wins / self.total_races) * 100 if self.total_races > 0 else 0
    
    def __str__(self):
        return self.name

    
# This is the model for the Race (name, date, location, 
# track_configuration, track_condition, classification, season, track_length, track_surface)
class Race(models.Model):
    class TrackSurface(models.TextChoices):
        DIRT = 'D', 'Dirt'
        TURF = 'T', 'Turf'
        SYNTHETIC = 'S', 'Synthetic'
        OTHER = 'O', 'Other'
    
    class TrackConfiguration(models.TextChoices):
        LEFT_HANDED = 'left_handed', 'Left Handed'
        RIGHT_HANDED = 'right_handed', 'Right Handed'
        STRAIGHT = 'straight', 'Straight'

    class TrackCondition(models.TextChoices):
        FAST = 'fast', 'Fast'
        FROZEN = 'frozen', 'Frozen'
        GOOD = 'good', 'Good'
        HEAVY = 'heavy', 'Heavy'
        MUDDY = 'muddy', 'Muddy'
        SLOPPY = 'sloppy', 'Sloppy'
        SLOW = 'slow', 'Slow'
        WET_FAST = 'wet_fast', 'Wet Fast'
        FIRM = 'firm', 'Firm'
        HARD = 'hard', 'Hard'
        SOFT = 'soft', 'Soft'
        YIELDING = 'yielding', 'Yielding'
        STANDARD = 'standard', 'Standard'
        HARSH = 'harsh', 'Harsh'
    
    class Classification(models.TextChoices):
        GRADE_1 = 'G1', 'Grade 1'
        GRADE_2 = 'G2', 'Grade 2'
        GRADE_3 = 'G3', 'Grade 3'
        LISTED = 'L', 'Listed'
        HANDICAP = 'H', 'Handicap'
        MAIDEN = 'M', 'Maiden'
        OTHER = 'O', 'Other'

    class Season(models.TextChoices):
        SPRING = 'SP', 'Spring'
        SUMMER = 'SU', 'Summer'
        FALL = 'FA', 'Fall'
        WINTER = 'WI', 'Winter'

    DIRT_CONDITIONS = {'fast', 'frozen', 'good', 'heavy', 'muddy', 'sloppy', 'slow', 'wet_fast'}
    TURF_CONDITIONS = {'firm', 'good', 'hard', 'soft', 'yielding'}
    SYNTHETIC_CONDITIONS = {'standard', 'wet_fast', 'sloppy', 'frozen', 'harsh'}
    
    name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=100)
    track_configuration = models.CharField(max_length=15, choices=TrackConfiguration.choices)
    track_condition = models.CharField(max_length=15, choices=TrackCondition.choices)
    classification = models.CharField(max_length=2, choices=Classification.choices)
    season = models.CharField(max_length=2, choices=Season.choices)
    track_length = models.PositiveIntegerField(help_text="Length in meters")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    racehorses = models.ManyToManyField(Racehorse, through="Participation", related_name='races')
    jockeys = models.ManyToManyField(Jockey, through="Participation", related_name='races')
    prize_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default="USD")


    track_surface = models.CharField(max_length=2, choices=TrackSurface.choices)

    @property
    def winner(self):
        winner_participation = self.participations.filter(position=1).select_related('racehorse').first()
        return winner_participation.racehorse if winner_participation else None
    
    @property
    def total_participants(self):
        return self.participations.count()

    def __str__(self):
        return f"{self.name} on {self.date}"
    
    def clean(self):
        super().clean()
        if self.track_surface == self.TrackSurface.DIRT and self.track_condition not in self.DIRT_CONDITIONS:
            raise ValidationError({'track_condition': 'Invalid track condition for dirt surface.'})
        elif self.track_surface == self.TrackSurface.TURF and self.track_condition not in self.TURF_CONDITIONS:
            raise ValidationError({'track_condition': 'Invalid track condition for turf surface.'})
        elif self.track_surface == self.TrackSurface.SYNTHETIC and self.track_condition not in self.SYNTHETIC_CONDITIONS:
            raise ValidationError({'track_condition': 'Invalid track condition for synthetic surface.'})
    
# This is the model for the race entry (racehorse, race, jockey, position, is_winner)
class Participation(models.Model):
    racehorse = models.ForeignKey(Racehorse, related_name='participations', on_delete=models.CASCADE)
    race = models.ForeignKey(Race, related_name='participations', on_delete=models.CASCADE)
    jockey = models.ForeignKey(Jockey, related_name='participations', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.PositiveIntegerField()
    finish_time = models.DurationField(blank=True, null=True, help_text="Official finish time")
    margin = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Lengths behind the winner")
    odds = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Starting odds")

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(fields=['race', 'racehorse'], name='unique_race_racehorse'),
            models.UniqueConstraint(fields=['race', 'jockey'], name='unique_race_jockey')
        ]

    @property
    def result_status(self):
        if self.position == 1:
            return "Winner"
        elif self.position == 2:
            return "Runner-up"
        elif self.position == 3:
            return "Third place"
        else:
            return f"{self.position}th place"
        
    @property
    def is_winner(self):
        return self.position == 1

    def __str__(self):
        return f"{self.racehorse.name} in {self.race.name} - Position: {self.position} {'(Winner)' if self.is_winner else ''}"