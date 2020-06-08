from django.contrib import admin

# Register your models here.
from user.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_name','language','address', 'phone','city','country','image_tag']

admin.site.register(UserProfile,UserProfileAdmin)