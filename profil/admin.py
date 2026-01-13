from django.contrib import admin
from .models import UserProfile, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'erstellt_am']
    search_fields = ['username', 'user__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'profile', 'sterne', 'erstellt_am', 'gemeldet']
    search_fields = ['author__username', 'profile__username', 'text']
    list_filter = ['sterne', 'gemeldet']
