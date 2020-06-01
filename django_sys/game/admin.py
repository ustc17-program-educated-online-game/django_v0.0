from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.HistoryInfo)
admin.site.register(models.PlayerInfo)
admin.site.register(models.Map)