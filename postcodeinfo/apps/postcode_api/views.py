import os

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response

from .models import Address, Country, LocalAuthority, PostcodeGssCode
from .serializers import AddressSerializer

from ignore_client_content_negotiation import IgnoreClientContentNegotiation


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        postcode = self.request.QUERY_PARAMS.get('postcode', '').\
            replace(' ', '').lower()

        return self.queryset.filter(postcode_index=postcode)


class PostcodeView(generics.RetrieveAPIView):

    geom_query = 'postcode_index'

    def __format_json(cls, centre, local_authority, country):
        
        if local_authority:
            local_authority = {
                'name': local_authority.name,
                'gss_code': local_authority.gss_code
            }

        if country:
            country = {
                'name': country.name,
                'gss_code': country.gss_code
            }

        data = {
            'centre': {
                'type': 'Point',
                'coordinates': centre
            },
            'local_authority': local_authority,
            'country': country
        }
        return data

    def _get_centre_point(self, postcode):
        geom = Address.objects.filter(
            **{self.geom_query: postcode}).collect(field_name='point')
        if geom:
            centre = geom.centroid.coords
            return centre

    def _get_local_authority(self, postcode):
        local_authority = LocalAuthority.objects.for_postcode(postcode)
        return local_authority

    def _get_country(self, postcode):
        country = Country.objects.for_postcode(postcode)
        return country

    def _get_administrative_districts(self, postcode):
        districts = {
            'local_authority': self._get_local_authority(postcode),
            'country': self._get_country(postcode)
        }
        return districts

    def get(self, request, *args, **kwargs):
        postcode = kwargs.get('postcode', '').replace(' ', '').lower()
        geom = self._get_centre_point(postcode)

        if geom:
            districts = self._get_administrative_districts(postcode)
            data = self.__format_json(
                geom, districts['local_authority'], districts['country'])

            return Response(data, status=status.HTTP_200_OK)

        return Response(None, status=status.HTTP_404_NOT_FOUND)


class PartialPostcodeView(PostcodeView):

    def _get_administrative_districts(self, postcode_area):

        postcode_gss_code = PostcodeGssCode.objects.most_common_in_area(
            postcode_area)
        la = None
        country = None

        if postcode_gss_code:
            la = LocalAuthority.objects.filter(
                gss_code=postcode_gss_code['local_authority_gss_code']).first()
            country = Country.objects.filter(
                gss_code=postcode_gss_code['country_gss_code']).first()

        return {
            'local_authority': la,
            'country': country
        }

    def _get_centre_point(self, postcode_area):
        return Address.objects.get_centre_point(postcode_area)


class MonitoringView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    content_negotiation_class = IgnoreClientContentNegotiation


class PingDotJsonView(MonitoringView):

    def get(self, request, *args, **kwargs):
        data = {
            'version_number': os.environ.get('APPVERSION'),
            'build_date': os.environ.get('APP_BUILD_DATE'),
            'commit_id': os.environ.get('APP_GIT_COMMIT'),
            'build_tag': os.environ.get('APP_BUILD_TAG')
        }
        return Response(data, status=status.HTTP_200_OK)


class HealthcheckDotJsonView(MonitoringView):

    def get(self, request, *args, **kwargs):
        database_ok = self.is_database_ok()
        # this should be an AND of all the checks - add more as needed
        all_ok = database_ok

        data = {
            'database': {
                'description': 'Postgres RDS instance',
                'ok': database_ok},
            'ok': all(
                [database_ok,
                 ])
        }
        overall_status = status.HTTP_200_OK
        if not all_ok:
            overall_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data, status=overall_status)

    def is_database_ok(self):
        address = Address.objects.order_by('uprn').first()
        return address is not None
