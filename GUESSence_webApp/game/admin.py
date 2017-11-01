from django.contrib import admin
from .models import CustomUser, DemographicUser, DemUser, Game, Message, City, Profile

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(DemographicUser)
admin.site.register(DemUser)
admin.site.register(Game)
admin.site.register(Message)
admin.site.register(City)
admin.site.register(Profile)