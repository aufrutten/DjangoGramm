from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Post)
admin.site.register(models.Subscription)

admin.site.register(models.Tag)
admin.site.register(models.Comment)
admin.site.register(models.Like)
