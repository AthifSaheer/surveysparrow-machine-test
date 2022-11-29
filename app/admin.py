from django.contrib import admin
from . import models

@admin.register(models.URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ("url", "interval", "user", "active")