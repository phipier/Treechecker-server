from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class Country(models.Model):
	"""This class represents the country model."""

	name = models.CharField(max_length=100, blank=False, unique=False)
	code = models.CharField(max_length=20, blank=False, unique=True)

	class Meta:
		verbose_name = "Country"
		verbose_name_plural = "Countries"

	def __str__(self):
		"""Return a human readable representation of the country instance."""
		return "{0}, {1}".format(str(self.name), str(self.code))

class Metadata(models.Model):
	"""This class represents the metadata model."""

	key = models.CharField(max_length=100, blank=False, unique=False)
	value = models.CharField(max_length=100, blank=False, unique=False)

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{0}, {1}".format(str(self.key), str(self.value))

class User(AbstractUser):
	"""This class represents the user model."""

	name = models.CharField(max_length=255, blank=False, unique=False)
	username = models.CharField(max_length=100, blank=False, unique=False)
	email = models.EmailField(max_length=100, blank=False, unique=True)
	password = models.CharField(max_length=255, blank=False, unique=False)
	occupation = models.CharField(max_length=255, blank=True, unique=False)
	country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
	language = models.CharField(max_length=255, blank=True, unique=False)
	creation_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "User"
		verbose_name_plural = "Users"

	@property
	def gz(self):
		return GeographicalZone.objects.filter(ggz__group__user=self).all()

	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = ['name', 'username']

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(str(self.name))

	def get_full_name(self):
		return self.name

	def get_short_name(self):
		return self.username

class GeographicalZone(models.Model):
	"""This class represents the geographical zone model."""

	name = models.CharField(max_length=255, blank=False, unique=False)
	country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
	wms_url = models.TextField("WMS URLs", blank=False, null=False, unique=False)

	x_min = models.FloatField("longitude min (in decimal degrees)", blank=False, unique=False)
	x_max = models.FloatField("longitude max (in decimal degrees)", blank=False, unique=False)
	y_min = models.FloatField("latitude min (in decimal degrees)", blank=False, unique=False)
	y_max = models.FloatField("latitude max (in decimal degrees)", blank=False, unique=False)

	#proj = models.CharField(max_length=255, blank=False, unique=False)
	#image_url = models.CharField(max_length=255, blank=False, unique=False)
	#layer_name = models.CharField(max_length=255, blank=False, unique=False)

	class Meta:
		verbose_name = "Geographical Zone"
		verbose_name_plural = "Geographical Zones"

	@property
	def bbox(self):
		return [self.y_min, self.x_min, self.y_max, self.x_max]

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(str(self.name))

class GGZ(models.Model):
	"""This class represents the group-geographical zone model."""

	group = models.ForeignKey(Group, on_delete=models.CASCADE)
	geographical_zone = models.ForeignKey(GeographicalZone, on_delete=models.CASCADE)

	class Meta:
		verbose_name = "Geographical Zone / User Group"
		verbose_name_plural = "Geographical Zones / User Groups"

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{0}, {1}".format(self.group, self.geographical_zone)

class AOI(models.Model):
	"""This class represents the AOI model."""

	name = models.CharField(max_length=100, blank=False, unique=False)
	x_min = models.FloatField()
	x_max = models.FloatField()
	y_min = models.FloatField()
	y_max = models.FloatField()
	owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	geographical_zone = models.ForeignKey(GeographicalZone, on_delete=models.CASCADE)
	creation_date = models.DateTimeField(auto_now_add=True)
	is_deleted = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Area Of Interest (AOI)"
		verbose_name_plural = "Areas Of Interest (AOI)"

	@property
	def bbox(self):
		return [self.x_min, self.x_max, self.y_min, self.y_max]

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.name)

class TreeSpecie(models.Model):
	"""This class represents the Tree specie model."""

	name = models.CharField(max_length=50, blank=False, unique=True)

	class Meta:
		verbose_name = "Tree Species"
		verbose_name_plural = "Tree Species"

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.name)

class CrownDiameter(models.Model):
	"""This class represents the crown diameter model."""

	name = models.CharField(max_length=50, blank=False, unique=True)

	class Meta:
		verbose_name = "Crown Diameter"
		verbose_name_plural = "Crown Diameters"

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.name)

class CanopyStatus(models.Model):
	"""This class represents the canopy status model."""

	name = models.CharField(max_length=50, blank=False, unique=True)

	class Meta:
		verbose_name = "Canopy Status"
		verbose_name_plural = "Canopy Status"

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.name)

class SurveyData(models.Model):
	"""This class represents the survey data model."""

	name = models.CharField(max_length=255, blank=False, unique=False, null=False)
	tree_specie = models.ForeignKey(TreeSpecie, blank=True, null=True, on_delete=models.CASCADE)
	crown_diameter = models.ForeignKey(CrownDiameter, blank=True, null=True, on_delete=models.CASCADE)
	canopy_status = models.ForeignKey(CanopyStatus, null=False, on_delete=models.CASCADE)
	comment = models.TextField(blank=True, null=True, unique=False)
	owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
	aoi = models.ForeignKey(AOI, null=False, on_delete=models.CASCADE)
	longitude = models.FloatField(null=False)
	latitude = models.FloatField(null=False)
	creation_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Survey Data"
		verbose_name_plural = "Survey Data"

	@property
	def position(self):
		return {"latitude": self.latitude, "longitude":self.longitude}

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.name)

class Photo(models.Model):
	"""This class represents the photo model."""

	survey_data =  models.ForeignKey(SurveyData, null=False, on_delete=models.CASCADE)
	compass = models.FloatField(blank=True, null=True)
	comment = models.TextField(blank=True, null=True, unique=False)
	image = models.TextField(blank=False, null=False, unique=False)
	img = models.FileField("Image file", upload_to='uploads/%Y/%m/%d/',blank=True, null=True, unique=False)	

	class Meta:
		verbose_name = "Photo"
		verbose_name_plural = "Photos"

	def __str__(self):
		"""Return a human readable representation of the model instance."""
		return "{}".format(self.id)
