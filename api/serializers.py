from django.db import transaction
from rest_framework import serializers
from .models import Racehorse, Jockey, Race, Participation, User

class RacehorseForJockeySerializer(serializers.ModelSerializer):
    jockey_total_races = serializers.SerializerMethodField()
    jockey_total_wins = serializers.SerializerMethodField()
    jockey_win_rate = serializers.SerializerMethodField()

    class Meta:
        model = Racehorse
        fields = (
            'name',
            'jockey_total_races',
            'jockey_total_wins',
            'jockey_win_rate',
        )

    def get_jockey_total_races(self, obj):
        jockey = self.context.get("jockey")
        if not jockey:
            return 0
        return Participation.objects.filter(racehorse=obj, jockey=jockey).count()

    def get_jockey_total_wins(self, obj):
        jockey = self.context.get("jockey")
        if not jockey:
            return 0
        return Participation.objects.filter(
            racehorse=obj,
            jockey=jockey,
            position=1  # or however you define a "win"
        ).count()

    def get_jockey_win_rate(self, obj):
        total_races = self.get_jockey_total_races(obj)
        total_wins = self.get_jockey_total_wins(obj)
        return round((total_wins / total_races) * 100, 2) if total_races > 0 else 0.0

class RacehorseNestedWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racehorse
        fields = ('name', 'birth_date', 'breed', 'gender')

class JockeyNestedWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jockey
        fields = ('name', 'birth_date')

class RaceNestedWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        fields = (
            'name', 'date', 'location', 'track_configuration',
            'track_condition', 'classification', 'season', 'track_length',
            'prize_money', 'currency', 'track_surface'
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'get_full_name',
            'username',
            'email',
            'is_staff',
            'is_superuser',
            'avatar',
        )


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_staff', 'avatar')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            is_staff=validated_data.get('is_staff', False),
            avatar=validated_data.get('avatar'),
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        if 'is_staff' in validated_data:
            instance.is_staff = validated_data['is_staff']

        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']

        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class RacehorseSerializer(serializers.ModelSerializer):
    class ParticipationSerializer(serializers.ModelSerializer):
        racehorse = serializers.CharField(source='racehorse.name')
        jockey = serializers.CharField(source='jockey.name')

        class Meta:
            model = Participation
            fields = (
                'racehorse',
                'jockey',
                'position',
                'finish_time',
                'margin',
                'odds',
                'result_status'
            )
    participations = ParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Racehorse
        fields = (
            'id', 'name', 'birth_date', 'breed', 'gender', 'country', 'image',
            'is_active', 'created_at', 'updated_at',
            'total_races', 'total_wins', 'win_rate', 'age', 'participations',
            'g1_wins'
        )

class RacehorseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racehorse
        fields = (
            'name', 'birth_date', 'breed', 'gender', 'country',
            'image', 'is_active'
        )

class JockeySerializer(serializers.ModelSerializer):
    class ParticipationSerializer(serializers.ModelSerializer):
        racehorse = serializers.CharField(source='racehorse.name')
        jockey = serializers.CharField(source='jockey.name')

        class Meta:
            model = Participation
            fields = (
                'racehorse',
                'jockey',
                'position',
                'finish_time',
                'margin',
                'odds',
                'result_status'
            )
    participations = ParticipationSerializer(many=True, read_only=True)
    racehorses = serializers.SerializerMethodField()

    class Meta:
        model = Jockey
        fields = (
            'id', 'name', 'image', 'height_cm', 'weight_kg', 'birth_date',
            'total_races', 'total_wins', 'win_rate', 'age', 'racehorses', 'participations', 'g1_wins'
        )

    def get_racehorses(self, obj):
        horses = Racehorse.objects.filter(participations__jockey=obj).distinct()
        return RacehorseForJockeySerializer(
            horses,
            many=True,
            context={'jockey': obj}
        ).data

class JockeyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jockey
        fields = (
            'name', 'image', 'height_cm', 'weight_kg', 'birth_date'
        )

class ParticipationSerializer(serializers.ModelSerializer):
    racehorse_name = serializers.CharField(source='racehorse.name')
    jockey_name = serializers.CharField(source='jockey.name')
    race_name = serializers.CharField(source='race.name')
    racehorse_image = serializers.ImageField(source='racehorse.image')
    race_date = serializers.DateField(source='race.date')
    race_season = serializers.CharField(source='race.season')
    class Meta:
        model = Participation
        fields = (
            'id', 'racehorse', 'racehorse_name', 'racehorse_image', 'race', 'race_name', 'race_date', 'race_season', 'jockey', 'jockey_name', 'position',
            'finish_time', 'margin', 'odds', 'is_winner', 'result_status'
        )

# class ParticipationWriteSerializer(serializers.ModelSerializer):
#     racehorse = RacehorseNestedWriteSerializer()
#     race = RaceNestedWriteSerializer()
#     jockey = JockeyNestedWriteSerializer()

#     class Meta:
#         model = Participation
#         fields = (
#             'racehorse', 'race', 'jockey',
#             'position', 'finish_time', 'margin', 'odds'
#         )

#     def create(self, validated_data):
#         racehorse_data = validated_data.pop('racehorse')
#         race_data = validated_data.pop('race')
#         jockey_data = validated_data.pop('jockey')

#         racehorse, _ = Racehorse.objects.get_or_create(**racehorse_data)
#         race, _ = Race.objects.get_or_create(**race_data)
#         jockey, _ = Jockey.objects.get_or_create(**jockey_data)

#         return Participation.objects.create(
#             racehorse=racehorse, race=race, jockey=jockey, **validated_data
#         )

#     def update(self, instance, validated_data):
#         racehorse_data = validated_data.pop('racehorse', None)
#         race_data = validated_data.pop('race', None)
#         jockey_data = validated_data.pop('jockey', None)

#         if racehorse_data:
#             racehorse, _ = Racehorse.objects.get_or_create(**racehorse_data)
#             instance.racehorse = racehorse

#         if race_data:
#             race, _ = Race.objects.get_or_create(**race_data)
#             instance.race = race

#         if jockey_data:
#             jockey, _ = Jockey.objects.get_or_create(**jockey_data)
#             instance.jockey = jockey

#         # Update the rest of the fields (position, finish_time, etc.)
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance

class ParticipationWriteSerializer(serializers.ModelSerializer):
    racehorse = serializers.PrimaryKeyRelatedField(
        queryset=Racehorse.objects.all()
    )
    race = serializers.PrimaryKeyRelatedField(
        queryset=Race.objects.all()
    )
    jockey = serializers.PrimaryKeyRelatedField(
        queryset=Jockey.objects.all()
    )

    class Meta:
        model = Participation
        fields = (
            'racehorse', 'race', 'jockey',
            'position', 'finish_time', 'margin', 'odds'
        )



class RaceSerializer(serializers.ModelSerializer):
    class ParticipationSerializer(serializers.ModelSerializer):
        racehorse = serializers.CharField(source='racehorse.name')
        jockey = serializers.CharField(source='jockey.name')

        class Meta:
            model = Participation
            fields = (
                'racehorse',
                'jockey',
                'position',
                'finish_time',
                'margin',
                'odds',
                'result_status'
            )
    winner = serializers.CharField(source='winner.name', allow_null=True)
    total_participants = serializers.ReadOnlyField()
    participations = ParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Race
        fields = (
            'id', 'name', 'date', 'location', 'track_configuration',
            'track_condition', 'classification', 'season', 'track_length',
            'prize_money', 'currency', 'track_surface',
            'winner', 'total_participants', 'participations'
        )

class RaceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        fields = (
            'name', 'date', 'location', 'track_configuration',
            'track_condition', 'classification', 'season', 'track_length',
            'prize_money', 'currency', 'track_surface'
        )

    def validate(self, data):
        """Ensure track_condition matches the surface rules."""
        instance = Race(**data)
        instance.clean()  # Calls the model's validation logic
        return data