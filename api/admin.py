from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AOI, GeographicalZone, Country, TreeSpecie, SurveyData, CanopyStatus, CrownDiameter, Metadata, GGZ, Photo

import csv
from django.http import HttpResponse

# Register your models here.
admin.site.register(User, UserAdmin)


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

class PhotoInline(admin.TabularInline):
    model = Photo
    extra=0

#class SurveyDataInline(admin.TabularInline):
#    model = SurveyData
#    extra=0

# @admin.register(SurveyData)
class SurveyDataAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'comment', 'canopy_status', 'aoi', 'longitude', 'latitude')    
    search_fields = ('name', 'aoi', 'canopy_status')
    list_per_page = 25
    actions = ["export_as_csv"]
    inlines = [PhotoInline,]

class AOIAdmin(admin.ModelAdmin):
    list_display = ('name', 'geographical_zone', 'x_min', 'y_min', 'x_max', 'y_max')    
    search_fields = ('name', 'geographical_zone')
    list_per_page = 25
#    inlines = [SurveyDataInline,]

admin.site.register(AOI, AOIAdmin)
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