from django.contrib import admin
from .models import Racehorse, Jockey, Race, Participation, User

# Inline: show participations inside the Race admin page
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1 

# Show Racehorses in Jockey admin
class RacehorseInline(admin.TabularInline):
    model = Racehorse
    extra = 1

class RaceAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ('id', 'name', 'date')
    search_fields = ('name',)
    list_filter = ('date',)

class JockeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age')
    search_fields = ('name',)

class RacehorseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'breed')
    search_fields = ('name', 'breed')

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'racehorse', 'jockey', 'race')
    list_filter = ('race', 'jockey')

# Register models
admin.site.register(User)
admin.site.register(Race, RaceAdmin)
admin.site.register(Jockey, JockeyAdmin)
admin.site.register(Racehorse, RacehorseAdmin)
admin.site.register(Participation, ParticipationAdmin)
