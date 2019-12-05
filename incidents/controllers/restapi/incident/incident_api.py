"""
rcbfp Module
---
incidents - Incident Master Model 0.0.1
This is the Master model for Incident
---
Author: Mark Gersaniva
Email: mark.gersaniva@springvalley.tech
"""

from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied

# Master
from incidents.models.incident.incident_models import Incident as Master

# Master Serializer
from incidents.controllers.restapi.incident.serializers.incident_serializers import IncidentPublicSerializer as MasterPublicSerializer
from incidents.controllers.restapi.incident.serializers.incident_serializers import IncidentPrivateSerializer as MasterPrivateSerializer

"""
Endpoints:
- Public
    - List
    - Detail
- Private
    - Create
    - Update
    - Delete
"""

###############################################################################
# Public
###############################################################################


class ApiPublicIncidentListDetail(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = MasterPublicSerializer
    model = Master

    def get_queryset(self, request, *args, **kwargs):
        """
        Filter if a `incident` value is passed in the URL
        """
        filters = {}
        if 'incident' in kwargs.GET:
            filters['incident'] = kwargs.GET.get('incident')

        return self.model.objects.filter(**filters)


###############################################################################
# Private
###############################################################################


class ApiPrivateIncidentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MasterPrivateSerializer
    model = Master

    def get_queryset(self, request, *args, **kwargs):
        """
        Filter if a `incident` value is passed in the URL
        """
        filters = {}
        if 'incident' in kwargs.GET:
            filters['incident'] = kwargs.GET.get('incident')

        return self.model.objects.filter(**filters)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            data['created_by'] = request.user
            try:
                self.model.objects.create(**data)
            except IntegrityError as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
            except KeyError as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)        
        instance = self.get_object() # override
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if instance.created_by != request.user:
            raise PermissionDenied()

        if serializer.is_valid():
            data = serializer.validated_data
            data['last_updated_by'] = request.user
            data.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object() # override

        if instance.created_by != request.user:
            raise PermissionDenied()
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
