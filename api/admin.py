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

from django.db.models.fields.related import ForeignKey
import json
import datetime

class ExportStreamMixin:
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

    export_as_csv.short_description = "Export selected as CSV"


    def export_as_geojson(self, request, queryset):
        meta = self.model._meta
        fields = meta.fields

        features = []
        for obj in queryset:
            properties = {}
            for field in fields:
                if isinstance(field, ForeignKey):
                    related_obj = getattr(obj, field.name)
                    properties[field.name] = str(related_obj)
                else:
                    properties[field.name] = getattr(obj, field.name)

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.longitude, obj.latitude]
                },
                "properties": properties
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "crs": {
                "type": "EPSG",
                "properties": {
                    "code": 4326
                }
            }
        }

        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename={}.geojson'.format(meta)
        response.write(self.json_serializable(geojson))
        return response

    export_as_geojson.short_description = "Export Selected as GeoJSON"

    def json_serializable(self, obj):
        def converter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return json.dumps(obj, default=converter, indent=4)


from django.http import FileResponse
from django.db.models import ForeignKey
import geopandas as gpd
from shapely.geometry import Point
import uuid
import tempfile
import os
from shapely.wkt import dumps

class ExportMixinPandas:
    EPSG_code = 4326
    def create_geodataframe(self, queryset):
        data = []
        fields = self.model._meta.fields
        exclude_fields = ['creation_date', 'update_date']  # exclude these fields
        for obj in queryset:
            row = {}
            for field in fields:
                if isinstance(field, ForeignKey):
                    related_obj = getattr(obj, field.name)
                    row[field.name] = str(related_obj)
                elif field.name not in exclude_fields:  # exclude fields here
                    row[field.name] = getattr(obj, field.name)
            row['geometry'] = Point(obj.longitude, obj.latitude)
            data.append(row)

        gdf = gpd.GeoDataFrame(data, geometry='geometry')
        gdf.set_crs(epsg=self.EPSG_code, inplace=True)

        return gdf

    from shapely.wkt import dumps

    def generate_response(self, gdf, driver, content_type, extension):
        filename_path = f"/tmp/{uuid.uuid4().hex}.{extension}"
        try:
            if extension == "csv":
                # Convert the geometry column to WKT format with SRID for CSV
                #epsg_code = self.EPSG_code
                #gdf['geometry'] = gdf['geometry'].apply(lambda x: f"SRID={epsg_code};{x.wkt}")
                gdf.to_csv(filename_path, index=False)
            else:
                gdf.to_file(filename_path, driver=driver)

            response = FileResponse(open(filename_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="surveydata.{extension}"'
        except Exception as e:
            print(f"Error occurred: {e}")
            raise
        finally:
            if os.path.exists(filename_path):
                os.remove(filename_path)
            elif os.path.isdir(filename_path):
                shutil.rmtree(filename_path)
        return response

    def export_as_csv_pandas(self, request, queryset):
        gdf = self.create_geodataframe(queryset)
        return self.generate_response(gdf, "", 'text/csv', 'csv')

    export_as_csv_pandas.short_description = "Export selected data as a CSV file"

    def export_as_geopackage_pandas(self, request, queryset):
        gdf = self.create_geodataframe(queryset)
        return self.generate_response(gdf, "GPKG", 'application/geopackage', 'gpkg')

    export_as_geopackage_pandas.short_description = "Export selected data as a GeoPackage file"

    def export_as_geojson_pandas(self, request, queryset):
        gdf = self.create_geodataframe(queryset)
        return self.generate_response(gdf, "GeoJSON", 'application/json', 'geojson')

    export_as_geojson_pandas.short_description = "Export selected data as a GeoJSON file"

    def export_as_shapefile_pandas(self, request, queryset):
        gdf = self.create_geodataframe(queryset)
        return self.generate_response(gdf, "ESRI Shapefile", 'application/zip', 'zip')

    export_as_shapefile_pandas.short_description = "Export selected data as a shapefile"


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
class SurveyDataAdmin(admin.ModelAdmin, ExportMixinPandas):
    list_display = ('name', 'aoi', 'canopy_status',  'longitude', 'latitude')
    fields = ('aoi', ('name', 'comment'), ('canopy_status','tree_species','crown_diameter'), ('longitude', 'latitude'))
    search_fields = ('name', 'aoi__name', 'canopy_status__name', 'tree_species__name')
    readonly_fields = ('aoi',)
    list_filter = ('canopy_status','aoi')
    list_per_page = 50
    actions = ["export_as_geojson_pandas", "export_as_geopackage_pandas", "export_as_csv_pandas"]
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

#admin.AdminSite.get_app_list = get_app_list

# defines content
admin.site.site_header = 'Treechecker'
admin.site.site_title = ''
admin.site.site_url = None
admin.site.index_title = 'Welcome to Treechecker'

# empties action panel # TO DO delete action panel
#from django.contrib.admin.models import LogEntry
#LogEntry.objects.all().delete()
