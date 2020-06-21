from django.contrib import admin

# Register your models here.
from user.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_name','address', 'phone','city','country','language','currency','image_tag']

admin.site.register(UserProfile,UserProfileAdmin)