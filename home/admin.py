from django.contrib import admin

# Register your models here.
from home.models import Setting, ContactMessage, FAQ, Language, Currency, SettingLang


class SettingtAdmin(admin.ModelAdmin):
    list_display = ['title','company', 'update_at','status']

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name','subject', 'update_at','status']
    readonly_fields =('name','subject','email','message','ip')
    list_filter = ['status']

class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer','ordernumber','lang','status']
    list_filter = ['status','lang']

class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['name', 'code','status']
    list_filter = ['status']

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code','value','status']
    list_filter = ['status']

class SettingLangAdmin(admin.ModelAdmin):
    list_display = ['title', 'keywords','description','lang']
    list_filter = ['lang']

admin.site.register(Setting,SettingtAdmin)
admin.site.register(SettingLang,SettingLangAdmin)
admin.site.register(ContactMessage,ContactMessageAdmin)
admin.site.register(FAQ,FAQAdmin)
admin.site.register(Language,LanguagesAdmin)
admin.site.register(Currency,CurrencyAdmin)

