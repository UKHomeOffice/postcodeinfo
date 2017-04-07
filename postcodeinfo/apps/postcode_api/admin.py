import django

from django.contrib.gis import admin

from .models import Address


# from https://djangosnippets.org/snippets/2593/
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import InvalidPage, Paginator
from django.db import connection


class LargeTableChangeList(ChangeList):
    """
    Overrides the count method to get an estimate instead of actual count when not filtered.

    The only change is the try/catch block calculating 'full_result_count'
    """
    def __init__(self, *args, **kwargs):
        super(LargeTableChangeList, self).__init__(*args, **kwargs)
        if django.VERSION < (1, 4):
            from django.contrib.admin.views.main import MAX_SHOW_ALL_ALLOWED
            self.list_max_show_all = MAX_SHOW_ALL_ALLOWED

    def get_results(self, request):
        paginator = self.model_admin.get_paginator(request, self.queryset, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        if not self.queryset.query.where:
            full_result_count = result_count
        else:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s",
                    [self.root_queryset.query.model._meta.db_table])
                full_result_count = int(cursor.fetchone()[0])
            except:
                full_result_count = self.root_queryset.count()

        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.queryset._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator


class LargeTablePaginator(Paginator):

    """
    Overrides the count method to get an estimate instead of actual count when not filtered
    """

    def _get_count(self):
        """
        Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages.
        """
        try:
            if self._count is not None:
                return self._count
        except AttributeError:
            pass
        try:
            estimate = 0
            if not self.object_list.query.where:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT reltuples "
                        "FROM pg_class WHERE relname = %s",
                        [self.object_list.query.model._meta.db_table])
                    estimate = int(cursor.fetchone()[0])
                except:
                    pass
            if estimate < 10000:
                self._count = self.object_list.count()
            else:
                self._count = estimate
        except (AttributeError, TypeError):
            # AttributeError if object_list has no count() method.
            # TypeError if object_list.count() requires arguments
            # (i.e. is of type list).
            self._count = len(self.object_list)
        return self._count
    count = property(_get_count)
# /from https://djangosnippets.org/snippets/2593/


class AddressAdmin(admin.OSMGeoAdmin, admin.ModelAdmin):
    show_full_result_count = False
    list_display = ('uprn', 'building_number', 'building_name',
                    'thoroughfare_name', 'post_town', 'postcode_index')
    ordering = ('postcode_index','uprn')
    paginator = LargeTablePaginator

    def get_changelist(self, request, **kwargs):
        return LargeTableChangeList

    def get_queryset(self, request):
        qs = super(AddressAdmin, self).get_queryset(request)
        return qs

        
admin.site.register(Address, AddressAdmin)
