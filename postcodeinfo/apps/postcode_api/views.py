import json

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .models import Address, LocalAuthority, PostcodeGssCode
from .serializers import AddressSerializer


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        postcode = self.request.QUERY_PARAMS.get('postcode', '').\
            replace(' ', '').lower()

        return self.queryset.filter(postcode_index=postcode)


class PostcodeView(generics.RetrieveAPIView):

    @classmethod
    def __format_json(cls, geom, local_authority):
        centre = geom.centroid.geojson
        lat_long = { 'latitude': centre[1], 'longitude': centre[0] }
            
        if local_authority:
                local_authority = {
                    'name': local_authority.name,
                    'gss_code': local_authority.gss_code
                }

        data = {
                'centre': lat_long,
                'local_authority': local_authority
            }
        return data

    @classmethod
    def __get_geometry(cls, postcode):
        geom = Address.objects.filter(
            postcode_index=postcode).collect(field_name='point')
        return geom

    @classmethod
    def __get_local_authority(cls, postcode):
        local_authority = LocalAuthority.for_postcode(postcode)
        return local_authority

        
    def get(self, request, *args, **kwargs):
        postcode = kwargs.get('postcode', '').replace(' ', '').lower()

        geom = self.__get_geometry(postcode)

        if geom:
            local_authority = self.__get_local_authority(postcode)
            data = self.__format_json(geom, local_authority)

            return Response(data, status=status.HTTP_200_OK)

        return Response(None, status=status.HTTP_404_NOT_FOUND)

class PartialPostcodeView(PostcodeView):

    def __get_geometry(postcode):
        geom = Address.objects.filter(
            postcode_area=postcode).collect(field_name='point')
        return geom
