from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Workout)
admin.site.register(Overload)
admin.site.register(WorkoutEntry)
