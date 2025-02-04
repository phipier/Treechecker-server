# Treechecker server
1. [Introduction](#introduction)

2. [Installation on PythonAnywhere](#installation1) 
    1. [Steps](#steps)
    2. [Considerations](#considerations)

2. [Installation on your hosting server](#installation2)
    1. [Requirements](#requirements)
    2. [Instructions](#instructions)    
   
4. [Database structure](#dbStructure)
5. [REST API](#restAPI)
    1. [Notes](#notes)
    2. [API calls](#apiCalls)
        1. [Authentication methods](#authenticationMethods)
            1. [Get token](#getToken)
            2. [Refresh token](#refreshTokens)
        2. [AOI methods](#aoiMethods)
            1. [Create AOI](#createAOI)
            2. [Delete AOI](#deleteAOI)
        3. [GZ methods](#gzMethods)
            1. [Get GZs](#getGZs)
            2. [Get GZ Info](#getGZInfo)
        4. [Observation methods](#observationMethods)
            1. [Add observation](#addObservation)
            2. [Get observation](#getObservation)
            3. [Update observation](#updateObservation)
            4. [Delete observation](#deleteObservation)
        5. [Other methods](#otherMethods)
            1. [Get User Data](#getUserData)
            2. [Upload Image](#uploadImage)
            3. [Add Image](#addImage)
            4. [Get Tree species](#getTreeSpecies)
            5. [Get Crown diameters](#getCrownDiameters)
            6. [Get Canopy statuses](#getCanopyStatuses)

# Introduction <a name="introduction"></a>
This document describes the server backend infrastructure of the Treechecker project.

# Installation on PythonAnywhere <a name="installation1"></a>
## Steps <a name="steps"></a>

In this section, you will learn how to install a Treechecker server using PythonAnywhere, a free hosting service. A free account will allow you a 1 GB database. You are free to upgrade your account anytime at a later date.		
Source : https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/

* Create a PythonAnywhere account	

Go to https://www.pythonanywhere.com and create an account  
NB: bear in mind that the default URL address will be "your-username.pythonanywhere.com" (for a free account, it will not be possible to change it afterwards)

* Clone the Treechecker official repository

Go to the Dashboard and open a bash console. Clone the treechecker-server repository
$ cd
$ git clone https://github.com/phipier/Treechecker-server.git 

Alternatively:
$ git clone https://webgate.ec.europa.eu/CITnet/stash/scm/fiseapps/treechecker-server.git	

* Create a Python virtual environment
```
$ cd ~/treechecker-server  
$ mkvirtualenv --python=/usr/bin/python3.6 trckvirtualenv  
$ workon trckvirtualenv  
$ pip install -r requirements-paw.txt   
```
* Create a database  

Go to Databases and create a MySQL database named "<your-username>$db" (only type "db" and the rest will be added automatically).
	
* Set up project environment variables  
	
Create and edit a new file named env.py in folder ~/treechecker-server:  
```
$ cd ~/treechecker-server  
$ vi env.py  
```

Do the necessary replacements in the following values and then copy and paste it inside file env.py:  
```
	SECRET_KEY_val="<secret-key-of-your-choice>"  
	DATABASES = {  
		'default': {  
		'HOST': "<your-username>.mysql.pythonanywhere-services.com",
		'NAME': "<your-username>$db",
		'USER': "<your-username>",
		'PASSWORD': "<your-db-password>",
		'PORT': '',
		'ENGINE': "django.db.backends.mysql",
		'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
	}
```

exemple:
```
SECRET_KEY_val="mykey"  
DATABASES = {  
	'default': {  
	'HOST': "Treechecker.mysql.pythonanywhere-services.com",
	'NAME': "Treechecker$db",
	'USER': "Treechecker",
	'PASSWORD': "y4Edj72gEJkh6S2",
	'PORT': '',
	'ENGINE': "django.db.backends.mysql",
	'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
        }
}
```

* Create a web app
	
Go back to Dashboard and click on "open web tab". "Add a new web app", and then make sure you choose "Manual Configuration", and then choose "Python 3.6", and then "Next"   
- For "source code", use “/home/<your-username>/treechecker-server“ (The field "Working directory" should then be automatically set to : “/home/<your-username>/”  and field "WSGI configuration" to : “file:/var/www/<your-username>_pythonanywhere_com_wsgi.py”. If not, please set them to those values)   
- Click on the "WSGI configuration" file name (<your-username>_pythonanywhere_com_wsgi.py) to edit it and replace the old content with the following content :  
	
```
#####################################################
import os
import sys

# add your project path (check path and spelling, it is case sensitive)
path = '/home/<your-username>/treechecker-server'
if path not in sys.path:
sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'canhemon.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
#####################################################
```

- For "virtual environment": /home/<your-username>/.virtualenvs/trckvirtualenv
- For "static files": /static/ and /home/<your-username>/treechecker-server/static/
- For "security": enable HTTPS	
	
* Initialise database model	
```
$ cd ~/treechecker-server
$ workon trckvirtualenv
$ python manage.py makemigrations
$ python manage.py migrate		
```

* Create an admin user	
```
$ python manage.py createsuperuser
```
* Test server

You may navigate to the following URL : your-username.pythonanywhere.com/settings and log in using username and password of super user.		
* Configure Treechecker-server	

Add Groups  
Add Group "user" and add basic rights (add AOI ...)  
Add Users  
Add User + add group "user"  
Add Region  
Fill field "WMS URLs"  
JSON format split into two parts :  
	BASE_WMS : A list of Background layers (only visible on map at AOI creation time)  
	VIEWER_WMS : A list of WMS layers that will be displaid on the interactive map when creating an area of interest (AOI) from the app.  
	DL_WMS : A list of WMS whose tiles will be downloaded when creating an area of interest (AOI). The tiles will be visible offline on the interactive map when adding an observation from the app. 
	
For example:

```
{
"BASE_WMS":[
	{
		"name":"OSM",
		"layerName":"OSM",
		"url":"https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
		"attribution":"Map data © <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors",
		"maxZoom":"22",
		"maxNativeZoom":"19"
	}
],
"VIEWER_WMS":[
	{
		"name":"Lombardia",
		"url":"https://www.cartografia.servizirl.it/viewer31/proxy/proxy.jsp?https://www.cartografia.servizirl.it/arcgis2/services/BaseMap/ortofoto2007UTM/ImageServer/WMSServer?",
		"layers":"0",
		"format":"image/png",
		"transparent":"true",
		"version":"1.1.0",
		"height":256,
		"width":256,
		"crs":"EPSG:4326",
		"maxZoom":"22",
		"maxNativeZoom":"19"
	}
],
"DL_WMS":[
	{
		"name":"Lombardia",
		"url":"https://www.cartografia.servizirl.it/viewer31/proxy/proxy.jsp?https://www.cartografia.servizirl.it/arcgis2/services/BaseMap/ortofoto2007UTM/ImageServer/WMSServer?",
		"layers":"0",
		"format":"image/png",
		"transparent":"true",
		"version":"1.1.0",
		"height":256,
		"width":256,
		"crs":"EPSG:4326",
		"maxZoom":"22",
		"maxNativeZoom":"19"
	}
]
}		
```

## Considerations <a name="considerations"></a>  

In order for the API to properly work you should at least provide data to the following tables: *(You can follow the links to check in more detail what each table stores)*
* [GeographicalZone](#geographicalZone)
* [GGZ](#ggz)
* [CrownDiameter](#crownDiameter)
* [CanopyStatus](#canopyStatus)

# Installation on your hosting server <a name="installation2"></a>
## Requirements <a name="requirements"></a>

The project has been developed using:
* Apache HTTP Server 2.4.2
* Python 3.6
* Python3-pip 8.1.1
* PostgreSql 9.4.14
* Django 1.11.2

## Instructions <a name="instructions"></a>
	
* Clone the treechecker-server repository in your projects folder  
```
$ git clone https://github.com/phipier/Treechecker-server.git
```

* Create a Python virtual environment  
```
$ cd ~/treechecker-server
$ python3 -m venv trckvirtualenv
$ source trckvirtualenv/bin/activate
$ pip install -r requirements.txt
```

* Create a database  

Go to Databases and create a database named "<your-databasename>"  
	
* Set up project environment variables  
```
$ cd ~/treechecker-server
```
create and edit a file named env.py in the main folder:  
```
$ vi env.py
```

Copy and paste the following into env.py and do the necessary replacements:  
```
SECRET_KEY_val="<secret-key-of-your-choice>"
DATABASES = {
'default': {
'HOST': "<your-hostaddress>",
'NAME': "<your-databasename>",
'USER': "<your-username>",
'PASSWORD': "<your-db-password>",
'PORT': '5432',
'ENGINE': "django.db.backends.postgresql",
'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
}
```

Open the file *<Project folder>\canhemon\settings.py* and edit the following lines:  

Set *DEBUG* to **False** to disable the Django warnings. *Note: leave it set to True while installing*  
Set *ALLOWED_HOSTS* to an array with the domain which points to the server. **Please consider using a HTTPS enabled server for better security**  
Modify the *TIME_ZONE* setting to the timezone you want Django to be configured in.  
Set the *STATIC_ROOT* to the directory where the uploaded images and the support files will be stored. *Note: Whatever you put inside this directory will be visible from outside* 

* Create the database structure running the following commands
```bash
    cd TreecheckerApp/web/
    python manage.py makemigrations
    python manage.py migrate
```

* Create a Django superuser
```bash
    python manage.py createsuperuser
```

* Collect the static files
```bash
    python manage.py collectstatic
```

* Configure Apache with WSGI  

file at projectfolder/canhemon/wsgi.py	

```
# WSGI config for canhemon project.
# It exposes the WSGI callable as a module-level variable named ``application``.
# For more information on this file, see
# https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/

import os, sys, site
import mod_wsgi

ROOT_DIR = '/var/www/<treechecker.com>/site/TreeCheckerApp/web/'
APP_DIR = '/var/www/<treechecker.com>/site/TreeCheckerApp/web/canhemon'
VE_DIR = '/var/www/<treechecker.com>/site/venv/lib/python3.6/site-packages'

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, APP_DIR)

sys.path.insert(1,VE_DIR)
site.addsitedir(VE_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canhemon.settings")

import signal
import time

application = get_wsgi_application()
```

* Apache configuration file /etc/httpd/conf.d/treecheckerprojectname.conf
  
```
<VirtualHost *:80>
ServerName <treechecker.com>
#ServerAlias <treeck.com>
DocumentRoot /var/www/<treechecker.com>/site/TreeCheckerApp/web/canhemon
Alias /static/ /var/www/<treechecker.com>/site/TreeCheckerApp/web/static/

# APACHE VIRTUAL HOST CUSTOM LOG DEFINITION
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t \"%r\" %>s %b" common
ErrorLog /var/www/<treechecker.com>/logs/error.log
CustomLog /var/www/<treechecker.com>/logs/access.log combined
# END APACHE VIRTUAL HOST CUSTOM LOG DEFINITION

# <Location /admin>
# Deny from all
# Allow from 139.191.16.20
# </Location>

#HTTP Strict Transport Security (HSTS)(max-age=expireTime', where expireTime is the time in seconds)
Header always set Strict-Transport-Security "max-age=31536000; includeSubdomains;"

# APACHE VIRTUAL HOST DOCUMENTROOT DEFINITION
<Directory /var/www/<treechecker.com>/site/TreeCheckerApp/web/canhemon>
AllowOverride None
Require all granted
Options -Indexes +FollowSymLinks
</Directory>
# END APACHE VIRTUAL HOST DOCUMENTROOT DEFINITION

<Directory /var/www/<treechecker.com>/site/TreeCheckerApp/web/static>
Require all granted
</Directory>

RewriteEngine on
RewriteCond %{REQUEST_METHOD} ^(TRACE|TRACK)
RewriteRule .* - [F]

WSGIDaemonProcess treecheckerwsgi display-name=treecheckerDjango user=trck processes=2 threads=15 deadlock-timeout=30
WSGIScriptAlias / /var/www/<treechecker.com>/site/TreeCheckerApp/web/canhemon/wsgi.py
WSGIPassAuthorization On
WSGIProcessGroup treecheckerwsgi
</VirtualHost>
```

# Database structure <a name="dbStructure"></a>
This is the database schema diagram:
![schema](docs/dbSchema.jpeg)

## Country
Stores countries information to be used by the users and geographical zones tables.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(100) | No | No | Country name as shown on the user profile screen |
| code | VARCHAR(20)  | No | Yes | Country code as specified by the ISO 3166 spec |

## Metadata
A key - value store. Not currently used but required per the project definition.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| key | VARCHAR(100) | No | No | Country name as shown on the user profile screen |
| value | VARCHAR(20)  | No | No | Country code as specified by the ISO 3166 spec |

## User
Stores users information.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(255) | No | No | Full name |
| email | VARCHAR(100) | No | Yes | Email. **Used to log in in the app** |
| password | VARCHAR(255) | No | No | Encripted password |
| occupation | VARCHAR(255) | No | No | User ocuppation |
| country_id | INTEGER FOREIGN KEY  | No | No | User country as a reference to the country table |
| language | VARCHAR(255) | No | No | User language as defined by the ISO 639-1 spec |
| creation_date | DATETIME | No | No | When this user was created |
| update_date | DATETIME | No | No | When this user was last updated |

## Geographical zone
Stores information related to a geographical zone.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(255) | No | No | Geographical zone name |
| country_id | INTEGER FOREIGN KEY | No | No | Geographical zone country as a reference to the country table |
| layer_name | VARCHAR(255) | No | No | Layer name as defined by the WMS service pointed by the wms_url attribute |
| wms_url | VARCHAR(255) | No | No | WMS URL used by this geographical zone |
| proj | VARCHAR(255)  | No | No | Coordinate Reference System as defined by the WMS service pointed by the wms_url attribute |
| image_url | VARCHAR(255) | No | No | Relative URL of the image used by the app on the geographical zones list |
| x_min | FLOAT | No | No | Minimum X of this geographical zone bounding box |
| x_max | FLOAT | No | No | Maximum X of this geographical zone bounding box |
| y_min | FLOAT | No | No | Minimum Y of this geographical zone bounding box |
| y_max | FLOAT | No | No | Maximum Y of this geographical zone bounding box |

## GGZ
Relates a user group as defined by the authorization middleware with their available geographical zones.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| group_id | INTEGER FOREIGN KEY | No | No | Group as a reference to the group table defined by Django |
| geographical_zone_id | INTEGER FOREIGN KEY | No | No | Geographical zone as a reference to the Geographical zone table |

## AOI
Stores information related to an area of interest defined by an user.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(100) | No | No | AOI name |
| x_min | FLOAT | No | No | Minimum X of this AOI bounding box |
| x_max | FLOAT | No | No | Maximum X of this AOI bounding box |
| y_min | FLOAT | No | No | Minimum Y of this AOI bounding box |
| y_max | FLOAT | No | No | Maximum Y of this AOI bounding box |
| owner_id | INTEGER FOREIGN KEY | No | No | AOI creator as a reference to the user table |
| geographical_zone_id | INTEGER FOREIGN KEY | No | No | Geographical zone as a reference to the Geographical zone table |
| creation_date | DATETIME | No | No | When this AOI was created |
| is_deleted | BOOLEAN | No | No | Is this AOI deleted? |

## Tree specie
Stores information related to the tree species.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(50) | No | No | Specie name |

## Crown diameter
Stores information related to the tree crown diameter.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(50) | No | No | Specie name |

## Canopy status
Stores information related to the tree canopy status.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(50) | No | No | Specie name |

## Survey data
Stores information related to an area of interest defined by an user.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| name | VARCHAR(255) | No | No | Survey data name |
| tree_specie_id | INTEGER FOREIGN KEY | No | No | Tree specie as a reference to the tree specie table |
| crown_diameter_id | INTEGER FOREIGN KEY | No | No | Crown diameter as a reference to the crown diameter table |
| canopy_status_id | INTEGER FOREIGN KEY | No | No | Canopy status as a reference to the canopy status table |
| comment | TEXT | No | No | Comment added to the survey data |
| owner_id | INTEGER FOREIGN KEY | No | No | Survey data creator as a reference to the user table |
| aoi_id | INTEGER FOREIGN KEY | No | No | AOI where the survey data was taken as a reference to the AOI table |
| geographical_zone_id | INTEGER FOREIGN KEY | No | No | Geographical zone where the survey data was taken as a reference to the Geographical zone table |
| longitude | FLOAT | No | No | WGS84 longitude where the survey data was taken |
| latitude | FLOAT | No | No | WGS84 latitude where the survey data was taken |
| compass | FLOAT | No | No | Heading the device was pointed at when the survey data was taken |
| creation_date | DATETIME | No | No | When this survey data was created |
| update_date | DATETIME | No | No | When this survey data was last updated |
| is_deleted | BOOLEAN | No | No | Is this survey data deleted? |

## Photo
Stores information related to an area of interest defined by an user.

| Column name        | Type     | Can be null?  | Unique? | Description |
| :------------- |:-------------:| :-----:| :---: | :----|
| id | INTEGER SERIAL | No | Yes | Row identifier |
| survey_data_id | INTEGER FOREIGN KEY | No | No | Survey data this image belongs to as a reference to the survey data table |
| longitude | FLOAT | No | No | WGS84 longitude where the photo was taken |
| latitude | FLOAT | No | No | WGS84 latitude where the photo was taken |
| compass | FLOAT | No | No | Heading the device was pointed at when the image was taken |
| url | VARCHAR(255) | No | No | Relative URL of the image on the server |

# Rest API <a name="restAPI"></a>

## Notes <a name="notes"></a>
To authenticate the api calls an *Authorization: JWT <token>* header should be sent with each request.

Each request expects an *application/json* content type

## API calls <a name="apiCalls"></a>
### Authentication methods <a name="authenticationMethods"></a>
#### Get token <a name="getToken"></a>

|  |  |
| :------------- | :----|
| **URL** | /api-token-auth/ |
| **Method** | POST |
| **Requires authentication:** | false |
| **Params:** | ` { "email": "email@domain.com", "password": "password123" } ` |
| **Response:** | ` { "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InRlc3QiLCJleHAiOjE1MDU3MTk0MTUsIm9yaWdfaWF0IjoxNTA1NzE1ODE1LCJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.ko-4TFy8pp2F8yaODdRO0F_sy94JJvf5-YDm-CRvcLg" } ` |


#### Refresh token <a name="refreshTokens"></a>

|  |  |
| :------------- | :----|
| **URL** | /api-token-refresh/ |
| **Method** | POST |
| **Requires authentication:** | false |
| **Params:** | ` { "token": "OLD_TOKEN" } ` |
| **Response:** | ` { "token": "NEW_TOKEN" } ` |

### AOI methods <a name="aoiMethods"></a>
#### Create AOI <a name="createAOI"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/gzs/**_idGZ_**/aois/ |
| **Method** | POST |
| **Requires authentication:** | true |
| **Params:** | ` { "name": "Test from postman", "x_min": 1.8025, "x_max": 1.9056, "y_min": 45.26, "y_max": 58.24 } ` |
| **Response:** | ` { "key": 4, "name": "Test from postman", "obs": [], "bbox": [ 45.26, 1.8025, 58.24, 1.9056 ] } ` |


#### Delete AOI <a name="deleteAOI"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/aois/**_idAOI_**/ |
| **Method** | DELETE |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** |  |

### GZ methods <a name="gzMethods"></a>
#### Get GZs <a name="getGZs"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/gzs/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 1, "name": "Berga", "image_url": "/gz/1.jpeg", "is_enabled": true  }, ... ] ` |

#### Get GZ Info <a name="getGZInfo"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/gzs/**_idGZ_**/aois/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 1, "name": "El vall", "obs": [ { "key": 1, "name": "Tree1", "tree_specie": { "key": 1, "name": "specie1" }, "crown_diameter": { "key": 1, "name": "0.1" }, "canopy_status": { "key": 2, "name": "status2" }, "comment": "Comentari 1", "position": { "longitude": 1.849544, "latitude": 42.104026 }, "images": [ { "key": 4, "url": "/static/obs/4.png" }, { "key": 3, "url": "/static/obs/3.png" } ] } ], "bbox": [ 42.103886, 1.847184, 42.104607, 1.856271 ] } ] ` |

### Observation methods <a name="observationMethods"></a>
#### Add Observation <a name="addObservation"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/aois/**_idAOI_**/observations/ |
| **Method** | POST |
| **Requires authentication:** | true |
| **Params:** | ` { "name": "obsTest", "tree_specie": 2, "crown_diameter": 2, "canopy_status": 5, "comment": "This is a test from postman", "latitude": 1.72789, "longitude": 45.123456, "compass": 30.45 } ` |
| **Response:** | ` { "key": 5, "name": "obsTest", "tree_specie": { "key": 2, "name": "specie2" }, "crown_diameter": { "key": 2, "name": "0.2" }, "canopy_status": { "key": 5, "name": "status5" }, "comment": "This is a test from Postman", "position": { "longitude": 45.123456, "latitude": 1.72789 }, "images": [ ] } ` |

#### Get Observation <a name="getObservation"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/observations/**_idObs_**/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 2, "name": "Tree2", "tree_specie": { "key": 1, "name": "specie1" }, "crown_diameter": { "key": 7, "name": "0.7" }, "canopy_status" : { "key": 3, "name": "status3" }, "comment": "Comentari 2", "position": { "longitude": 1.83455, "latitude": 42.005069 }, "images": [ ] } ] ` |

#### Update Observation <a name="updateObservation"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/observations/**_idObs_**/ |
| **Method** | PUT |
| **Requires authentication:** | true |
| **Params:** | ` { "name": "obsTest2", "tree_specie": 3, "crown_diameter": 5, "canopy_status": 3, "comment": "_This is a test from Postman_", "longitude": 40.123456, "latitude": 2.72789, "compass": 12 } ` |
| **Response:** | ` { "name": "obsTest2", "tree_specie": 3, "crown_diameter": 5, "canopy_status": 3, "comment": "_This is a test from Postman_", "aoi": 1, "gz": 1, "longitude": 40.123456, "latitude": 2.72789, "compass": 12 } ` |

#### Delete Observation <a name="deleteObservation"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/observations/**_idObs_**/ |
| **Method** | DELETE |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** |  |

### Others <a name="otherMethods"></a>
#### Get User data <a name="getUserData"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/users/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` { "key": 1, "name": "Usuari de test", "username": "test", "email": "test@test.com", "occupation": "Developer", "country": { "key": 1, "country_code": "cat" }, "language": "ca" } ` |

#### Upload image <a name="uploadImage"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/upload/ |
| **Method** | POST |
| **Requires authentication:** | true |
| **Params:** | ` { "image": "base64_image" } ` |
| **Response:** | ` { "url": "/static/obs/66.jpg" } ` |

#### Add image <a name="addImage"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/images/ |
| **Method** | POST |
| **Requires authentication:** | true |
| **Params:** | ` { "survey_data": 2, "latitude": 1.2859, "longitude": 45.38, "compass": 1.2345, "url": "url" } ` |
| **Response:** | ` { "key": 7, "url": "url" } ` |

#### Get tree species <a name="getTreeSpecies"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/species/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 1, "name": "specie1" }, ... ] ` |

#### Get crown diameters <a name="getCrownDiameters"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/crowns/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 1, "name": "0.1" }, ... ] ` |

#### Get canopy statuses <a name="getCanopyStatuses"></a>

|  |  |
| :------------- | :----|
| **URL** | /api/canopies/ |
| **Method** | GET |
| **Requires authentication:** | true |
| **Params:** |  |
| **Response:** | ` [ { "key": 1, "name": "status1" }, ... ] ` |
