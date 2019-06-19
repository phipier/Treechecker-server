from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AOI, GeographicalZone, Country, TreeSpecie, SurveyData, CanopyStatus, CrownDiameter, Metadata, GGZ, Photo

# Register your models here.
admin.site.register(User, UserAdmin)

admin.site.register(AOI)
admin.site.register(GeographicalZone)
admin.site.register(Country)
admin.site.register(TreeSpecie)
admin.site.register(SurveyData)
admin.site.register(CanopyStatus)
admin.site.register(CrownDiameter)
admin.site.register(Metadata)
admin.site.register(GGZ)
#admin.site.register(Photo)

admin.site.site_header = 'Treechecker'
admin.site.site_title = 'Treechecker'
admin.site.site_url = None
admin.site.index_title = "Data and configuration"

