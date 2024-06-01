from django.contrib import admin
from .models import User, VerifyUserEmail, WouldYouRatherQA

admin.site.register(User)
admin.site.register(VerifyUserEmail)
admin.site.register(WouldYouRatherQA)
