import os
import csv
import subprocess

from rdflib import Graph, URIRef

from postcode_api.models import LocalAuthority
from postcode_api.importers.progress_reporter import ProgressReporter


class LocalAuthoritiesImporter(object):

    def __init__(self):
        self.graph = None
        self.progress = ProgressReporter()

    def import_local_authorities(self, filename):
        self.graph = self.__load_graph(filename)
        la_count = LocalAuthority.objects.count()
        print 'Existing LocalAuthority count = ' + str(la_count)
        
        # all subject/object pairs which are related by a gssCode
        codes = self.graph.triples( (None, URIRef("http://data.ordnancesurvey.co.uk/ontology/admingeo/gssCode"), None) )
        self.progress.start(filename)

        for code_tuple in codes:
            self.__import_gss_code( code_tuple )
            self.progress.row_processed('gssCode: ' + code_tuple[0])

        self.progress.finish()
        new_count = LocalAuthority.objects.count()
        print str(new_count - la_count) + ' local authorities added'
        print 'New LocalAuthority count = ' + str(new_count)


    def __import_gss_code(self, code_tuple):
        code = str(code_tuple[2])
        local_authority = self.__find_or_create_local_authority(code)
        name = self.graph.value( subject=code_tuple[0], predicate=URIRef("http://www.w3.org/2000/01/rdf-schema#label" ) )
        self.__update_local_authority_name_if_needed(local_authority, name)


    def __update_local_authority_name_if_needed(self, local_authority, name):
        if local_authority.name != name:
            local_authority.name = name
            local_authority.save()
        

    def __find_or_create_local_authority(self, gss_code):
        try:
            a = LocalAuthority.objects.get(gss_code=gss_code)
        except LocalAuthority.DoesNotExist:
            a = LocalAuthority(gss_code=gss_code)
        return a


    def __load_graph(self, filename):
        self.graph = Graph()
        self.lines_in_file = self.progress.lines_in_file(filename)
        print 'parsing graph from file ' + filename
        self.graph.parse(filename, format="nt")
        print ' => ' + str(len(self.graph)) + ' tuples'
        return self.graph