from django.contrib import admin

from labeling.models import Label, DataItem, Annotation, Validation, User

# Register your models here.
admin.site.register(User)
admin.site.register(Label)
admin.site.register(DataItem)
admin.site.register(Annotation)
admin.site.register(Validation)