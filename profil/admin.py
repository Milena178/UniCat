from django.contrib import admin
from .models import UserProfile, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_type', 'erstellt_am']
    search_fields = ['username', 'user__username']
    list_filter = ['user_type']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['bewertender', 'bewerteter', 'sterne', 'erstellt_am', 'gemeldet']
    search_fields = ['bewertender__username', 'bewerteter__username', 'text']
    list_filter = ['sterne', 'gemeldet']
