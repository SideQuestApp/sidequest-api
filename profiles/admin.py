from django.contrib import admin
from .models import User, VerifyUserEmail

admin.site.register(User)
admin.site.register(VerifyUserEmail)
