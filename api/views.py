from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings as djangoSettings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from rest_framework.exceptions import Throttled
from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *

import random
import json
import base64

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, Throttled):
        custom_response_data = {
            'message': 'The maximum number of failed login attempts has been reached. Try again in %d seconds or ask for a new password' % exc.wait
        }
        response.data = custom_response_data
    return response

# Gets the geographical zones. Only the ones available to the user are enabled
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def getGZ(request):
	# Retrieve the geographical zones available to the authenticated user
	objs = request.user.gz
	serialized = GeographicalZoneSerializer(objs, context={'request': request}, many=True)

	return JsonResponse(serialized.data, safe=False)


# Gets the areas of interest for a given zone with the user observations or adds a new one
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def aoiView(request, gz):
	gzId = int(gz)
	if request.method == 'GET':
		aois = AOI.objects.filter(geographical_zone_id=gzId).filter(owner_id=request.user.id)
		serialized = AOIReadSerializer(aois, context={'request': request}, many=True)

		return JsonResponse(serialized.data, safe=False)

	else:
		#data = JSONParser().parse(request.data)
		data = request.data
		data['geographical_zone'] = gzId
		data['owner'] = request.user.id
		serialized = AOIWriteSerializer(data=data, context={'request': request})
		if (serialized.is_valid()):
			serialized = serialized.save()
			serialized = AOIReadSerializer(serialized, context={'request': request}, many=False);
			return JsonResponse(serialized.data, safe=False)
		else:
			return Response(serialized.errors)


# Deletes an area of interest
@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def deleteAOI(request, id):
	aoiId = int(id)
	aoi = AOI.objects.filter(id=aoiId)

	if(aoi):
		if(aoi[0].owner.id == request.user.id):
			aoi.delete()
			return Response(status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_403_FORBIDDEN)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)


# Gets the user data
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def userView(request):
	serialized = UserSerializer(request.user, context={'request': request})
	return JsonResponse(serialized.data, safe=False)


from datetime import datetime

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def addObservation(request, id):
    aoiId = int(id)
    aoi = AOI.objects.filter(id=aoiId)
    user_id = request.user.id
    user = get_object_or_404(User, id=user_id)
    user_name = user.name
    user_username = user.username

    print('{timestamp} -- addObservation. User ID: {user_id}, Name: {user_name}, Username: {user_username}, aoi_id: {id_aoi}'.format(
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        user_name=user_name,
        user_username=user_username,
        id_aoi=aoiId
    ))

    if aoi:
        aoi = aoi[0]
        aoi_name = aoi.name

        if aoi.owner.id == request.user.id:
            data = JSONParser().parse(request)
            data['aoi'] = aoiId
            serialized = SurveyDataWriteSerializer(data=data, context={'request': request})

            #print(json.dumps(serialized, indent=2))

            if serialized.is_valid():
                serialized = serialized.save()
                serialized = SurveyDataSerializer(serialized, context={'request': request}, many=False)

                print(json.dumps(serialized.data, indent=2))

                print('{timestamp} -- addImage: response. User ID: {user_id}, Name: {user_name}, Username: {user_username}, aoi_id: {id_aoi}, aoi_name: {aoi_name}, data:{data}'.format(
                    timestamp=datetime.utcnow().isoformat(),
                    user_id=user_id,
                    user_name=user_name,
                    user_username=user_username,
                    id_aoi=aoiId,
                    aoi_name=aoi_name,
                    data=data
                ))
                return JsonResponse(serialized.data, safe=False)
            else:
                print('{timestamp} -- addObservation: error 400. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
                    timestamp=datetime.utcnow().isoformat(),
                    user_id=user_id,
                    user_name=user_name,
                    user_username=user_username
                ))
                print('Errors:', serialized.errors)
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            print('{timestamp} -- addObservation: error 403. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
                timestamp=datetime.utcnow().isoformat(),
                user_id=user_id,
                user_name=user_name,
                user_username=user_username
            ))

            return Response(status=status.HTTP_403_FORBIDDEN)

    else:
        print('{timestamp} -- addObservation: error 404. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            user_name=user_name,
            user_username=user_username
        ))

        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, ))
def observationView(request, id):
	obsId = int(id)
	if request.method == 'GET':
		objs = SurveyData.objects.filter(id=obsId).filter(owner_id=request.user.id)
		serialized = SurveyDataSerializer(objs, context={'request': request}, many=True)
		return JsonResponse(serialized.data, safe=False)

	elif(request.method == 'PUT'):
		obs = SurveyData.objects.filter(id=obsId)

		if(obs):
			if(obs[0].owner.id == request.user.id):

				data = JSONParser().parse(request)
				obj = obs[0]

				#data['tree_specie'] = getTreeSpecie(data['tree_specie'], request)
				if 'images' in data:
					imagesToKeep = data['images']
				else:
					imagesToKeep = []

				serialized = SurveyDataWriteSerializer(obj, data=data, context={'imagesToKeep': imagesToKeep})

				if(serialized.is_valid()):

					serialized.save()
					return JsonResponse(serialized.data, safe=False)

				return Response(serialized.errors)

			else:
				return Response(status=status.HTTP_403_FORBIDDEN)
		else:
			return Response(status=status.HTTP_404_NOT_FOUND)

	else:
		obs = SurveyData.objects.filter(id=obsId)

		if(obs):

			if(obs[0].owner.id == request.user.id):

				obj = obs[0]
				obj.save()
				return Response(status=status.HTTP_200_OK)

			else:
				return Response(status=status.HTTP_403_FORBIDDEN)

		else:
			return Response(status=status.HTTP_404_NOT_FOUND)



def getTreeSpecies(idOrName, request):
	'''
		Check to see if the input value is an id.
		If it isn't, we create a new TreeSpecies with the input value as name
	'''
	if(isinstance(idOrName, int )):
		obs = TreeSpecies.objects.filter(id=idOrName)
		if(obs):
			return idOrName;

	serialized = TreeSpeciesWriteSerializer(data={'name': idOrName},  context={'request': request})
	if(serialized.is_valid()):

		serialized = serialized.save()
		serialized = TreeSpeciesSerializer(serialized, context={'request': request}, many=False)
		return serialized.data['key']

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def addImage(request):

    user_id = request.user.id
    user = get_object_or_404(User, id=user_id)
    user_name = user.name
    user_username = user.username

    print('{timestamp} -- addImage. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
        timestamp=datetime.utcnow().isoformat(),
        user_id=user_id,
        user_name=user_name,
        user_username=user_username
    ))

    data = JSONParser().parse(request)
    serialized = PhotoWriteSerializer(data=data, context={'request': request})

    if serialized.is_valid():
        obs = SurveyData.objects.filter(id=data['survey_data'])
        if obs:
            if obs[0].owner.id == request.user.id:

                serialized = serialized.save()

                serialized = PhotoSerializer(serialized, context={'request': request}, many=False)

                print('{timestamp} -- addImage: response. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
                    timestamp=datetime.utcnow().isoformat(),
                    user_id=user_id,
                    user_name=user_name,
                    user_username=user_username
                ))
                return JsonResponse(serialized.data, safe=False)

            else:
                print('{timestamp} -- addImage: error 403. User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
                    timestamp=datetime.utcnow().isoformat(),
                    user_id=user_id,
                    user_name=user_name,
                    user_username=user_username
                ))

                return Response(status=status.HTTP_403_FORBIDDEN)

        else:
            print('{timestamp} -- addImage: error 503 (2). User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
                timestamp=datetime.utcnow().isoformat(),
                user_id=user_id,
                user_name=user_name,
                user_username=user_username
            ))

            return Response(status=503)

    else:

        print('{timestamp} -- addImage: error 503 (1). User ID: {user_id}, Name: {user_name}, Username: {user_username}'.format(
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            user_name=user_name,
            user_username=user_username
        ))

        print(serialized.errors)
        #return Response(serialized.errors, status=503)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def getSpecies(request):
	objs = TreeSpecies.objects.all()
	serialized = TreeSpeciesSerializer(objs, context={'request': request}, many=True)

	return JsonResponse(serialized.data, safe=False);


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def getCrowns(request):
	objs = CrownDiameter.objects.all()
	serialized = CrownDiameterSerializer(objs, context={'request': request}, many=True)

	return JsonResponse(serialized.data, safe=False);


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def getCanopies(request):
	objs = CanopyStatus.objects.all()
	serialized = CanopyStatusSerializer(objs, context={'request': request}, many=True)

	return JsonResponse(serialized.data, safe=False);


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def fileUploadView(request):
    try:
        data = JSONParser().parse(request)
        data = data['image']
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]

        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        imagePath = 'obs/' + get_random_string(length=32) + '.' + ext
        path = djangoSettings.MEDIA_ROOT + '/' + imagePath
        default_storage.save(path, data)

        return JsonResponse({"url": djangoSettings.MEDIA_URL + imagePath}, safe=False)
    except:
        return JsonResponse({"error": "Request error"}, safe=False)
