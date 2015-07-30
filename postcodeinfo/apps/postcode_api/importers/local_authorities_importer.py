import logging

from rdflib import Graph, URIRef

from postcode_api.models import LocalAuthority
from postcode_api.importers.progress_reporter import ImporterProgress, \
    lines_in_file


log = logging.getLogger(__name__)


class LocalAuthoritiesImporter(object):

    def __init__(self):
        self.graph = None

    def import_local_authorities(self, filename):
        num_lines = lines_in_file(filename)
        self.graph = self._load_graph(filename)
        la_count = LocalAuthority.objects.count()
        log.info('Existing LocalAuthority count = ' + str(la_count))

        # all subject/object pairs which are related by a gssCode
        codes = self.graph.triples(
            (None, URIRef("http://data.ordnancesurvey.co.uk/"
                          "ontology/admingeo/gssCode"), None))

        with ImporterProgress(num_lines) as progress:
            for code_tuple in codes:
                self._import_gss_code(code_tuple)
                progress.increment('gssCode: ' + code_tuple[0])

        new_count = LocalAuthority.objects.count()
        log.info(str(new_count - la_count) + ' local authorities added')
        log.info('There are now ' + str(new_count) + ' local authorities')

    def _import_gss_code(self, code_tuple):
        code = str(code_tuple[2])
        local_authority, created = LocalAuthority.objects.get_or_create(gss_code=code)
        name = self.graph.value(subject=code_tuple[0], predicate=URIRef(
            "http://www.w3.org/2000/01/rdf-schema#label"))
        self._update_local_authority_name_if_needed(local_authority, name)

    def _update_local_authority_name_if_needed(self, local_authority, name):
        if local_authority.name != name:
            local_authority.name = name
            local_authority.save()

    def _load_graph(self, filename):
        self.graph = Graph()
        log.info('parsing graph from file ' + filename)
        self.graph.parse(filename, format="nt")
        log.info(' => ' + str(len(self.graph)) + ' tuples')
        return self.graph
