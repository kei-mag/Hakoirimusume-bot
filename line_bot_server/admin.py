from django.contrib import admin

from line_bot_server.models import User

# Register your models here.

class LineBotServerAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, LineBotServerAdmin)