from django.contrib import admin
from .models import Project, Task, Tag

# aca tenemos los 3 modelos registrados, estos los vamos a poder gestionar desde el panel de /admin despues
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Tag)