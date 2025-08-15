from django.db import transaction
from rest_framework import serializers
from .models import Racehorse, Jockey, Race, Participation, User

class RacehorseForJockeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Racehorse
        fields = (
            'name', 'total_wins', 'win_rate'
        )

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
        fields = ('name', 'date', 'location')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('password', 'user_permissions')
        fields = (
            'id',
            'get_full_name',
            'username',
            'email',
            'is_staff',
            'is_superuser',
        )

class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_staff')  # include is_staff if needed

    def create(self, validated_data):
        # Use create_user so password is hashed and other defaults are set
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False)
        )
        return user

    def update(self, instance, validated_data):
        # Update fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)

        # If password provided, hash it
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class RacehorseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racehorse
        fields = (
            'id', 'name', 'birth_date', 'breed', 'gender', 'country', 'image',
            'is_active', 'created_at', 'updated_at',
            'total_races', 'total_wins', 'win_rate', 'age'
        )

class RacehorseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racehorse
        fields = (
            'name', 'birth_date', 'breed', 'gender', 'country',
            'image', 'is_active'
        )

class JockeySerializer(serializers.ModelSerializer):
    racehorses = serializers.SerializerMethodField()

    class Meta:
        model = Jockey
        fields = (
            'id', 'name', 'image', 'height_cm', 'weight_kg', 'birth_date',
            'total_races', 'total_wins', 'win_rate', 'age', 'racehorses'
        )

    def get_racehorses(self, obj):
        # Get unique racehorses this jockey has ridden
        racehorses_qs = Racehorse.objects.filter(
            participations__jockey=obj
        ).distinct()
        return RacehorseForJockeySerializer(racehorses_qs, many=True).data

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
    class Meta:
        model = Participation
        fields = (
            'id', 'racehorse_name', 'race_name', 'jockey_name', 'position',
            'finish_time', 'margin', 'odds', 'is_winner', 'result_status'
        )

class ParticipationWriteSerializer(serializers.ModelSerializer):
    racehorse = RacehorseNestedWriteSerializer()
    race = RaceNestedWriteSerializer()
    jockey = JockeyNestedWriteSerializer()

    class Meta:
        model = Participation
        fields = (
            'racehorse', 'race', 'jockey',
            'position', 'finish_time', 'margin', 'odds'
        )

    def create(self, validated_data):
        racehorse_data = validated_data.pop('racehorse')
        race_data = validated_data.pop('race')
        jockey_data = validated_data.pop('jockey')

        racehorse, _ = Racehorse.objects.get_or_create(**racehorse_data)
        race, _ = Race.objects.get_or_create(**race_data)
        jockey, _ = Jockey.objects.get_or_create(**jockey_data)

        return Participation.objects.create(
            racehorse=racehorse, race=race, jockey=jockey, **validated_data
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