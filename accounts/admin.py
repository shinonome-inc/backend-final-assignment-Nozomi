from django.contrib import admin

from .models import Friends, User

admin.site.register(User)
admin.site.register(Friends)
