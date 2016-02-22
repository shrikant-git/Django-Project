from django.contrib import admin
from rango.models import Category, Page, UserProfile


class PageAdmin(admin.ModelAdmin):
    list_dsplay = ('title', 'category', 'url')

admin.site.register(Category)         # makes Category and Page available to admin interface.
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

