from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AOI, GeographicalZone, Country, TreeSpecie, SurveyData, CanopyStatus, CrownDiameter, Metadata, GGZ, Photo

import csv
from django.http import HttpResponse

# Register your models here.
admin.site.register(User, UserAdmin)

admin.site.register(AOI)
admin.site.register(GeographicalZone)
admin.site.register(Country)
admin.site.register(TreeSpecie)

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class SurveyDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'canopy_status', 'aoi', 'longitude', 'latitude')    
    search_fields = ('name', 'aoi', 'canopy_status')
    list_per_page = 25
    actions = ["export_as_csv"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(SurveyData, SurveyDataAdmin)
admin.site.register(CanopyStatus)
admin.site.register(CrownDiameter)
#admin.site.register(Metadata)
admin.site.register(GGZ)
admin.site.register(Photo)

# defines content
admin.site.site_header = 'Treechecker'
admin.site.site_title = 'Treechecker'
admin.site.site_url = None
admin.site.index_title = "Data and configuration"

# empties action panel # TO DO delete action panel
from django.contrib.admin.models import LogEntry
LogEntry.objects.all().delete()