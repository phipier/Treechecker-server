from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AOI, GeographicalZone, Country, TreeSpecies, SurveyData, CanopyStatus, CrownDiameter, Metadata, GGZ, Photo
from django.utils.safestring import mark_safe
import csv
from django.http import HttpResponse

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(GeographicalZone)
admin.site.register(Country)
admin.site.register(TreeSpecies)

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
    #readonly_fields = ["thumbnail_img","thumbnail_image"]
    readonly_fields = ["picture"]
    fields = ('picture','comment','compass')
    
    def picture(self, obj):
        return mark_safe('<img src="{base64str}" height="{height}"/>'.format(
            base64str = obj.image,
            height=500            
            )
    )
    """
    def thumbnail_img(self, obj):
        return mark_safe('<img src="{url}" height="{height}"/>'.format(
            url = obj.img.url,
            height=200
            #height=obj.img.height/4,nex
            )
    )
    """

#class SurveyDataInline(admin.TabularInline):
#    model = SurveyData
#    extra=0

# @admin.register(SurveyData)
class SurveyDataAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'aoi', 'canopy_status',  'longitude', 'latitude')
    fields = ('aoi', ('name', 'comment'), ('canopy_status','tree_species','crown_diameter'), ('longitude', 'latitude'))
    search_fields = ('name', 'aoi__name', 'canopy_status__name', 'tree_species__name')
    readonly_fields = ('aoi',)
    list_filter = ('canopy_status','aoi')
    list_per_page = 50
    actions = ["export_as_csv"]
    inlines = [PhotoInline,]
    save_on_top = True

class AOIAdmin(admin.ModelAdmin):
    list_display = ('name', 'geographical_zone')  
    fields = ('name', ('x_min', 'x_max'), ('y_max', 'y_min'), 'geographical_zone', 'owner')  
    search_fields = ('name', 'geographical_zone__name')
    readonly_fields = ('x_min', 'x_max', 'y_min', 'y_max', 'geographical_zone', 'owner')
    list_per_page = 50
#    inlines = [SurveyDataInline,]

class CrownDiameterAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    fields = ('name',)  
    search_fields = ('name',)
    list_per_page = 50

"""
class PhotoAdmin(admin.ModelAdmin):

    readonly_fields = ["thumbnail_image"]

    def thumbnail_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.img.url,
            width=obj.img.width/2,
            height=obj.img.height/2,
            )
    )
"""

admin.site.register(AOI, AOIAdmin)
admin.site.register(SurveyData, SurveyDataAdmin)
admin.site.register(CanopyStatus)
admin.site.register(CrownDiameter,CrownDiameterAdmin)
#admin.site.register(Metadata)
admin.site.register(GGZ)
#admin.site.register(Photo, PhotoAdmin)


# Creating a sort function
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    for app_name, object_list in [('api', ['GeographicalZone','AOI', 'SurveyData', 'Photo','TreeSpecies', 'CanopyStatus', 'CrownDiameter', 'Country', 'GGZ', 'User'])]:
        app = app_dict[app_name]
        app['models'].sort(key=lambda x: object_list.index(x['object_name']))
        yield app

admin.AdminSite.get_app_list = get_app_list

# defines content
admin.site.site_header = 'Treechecker'
admin.site.site_title = ''
admin.site.site_url = None
admin.site.index_title = 'Welcome to Treechecker'

# empties action panel # TO DO delete action panel
from django.contrib.admin.models import LogEntry
LogEntry.objects.all().delete()