from postcode_api.importers.psql_import_adapter import PSQLImportAdapter

class PostcodeGssCodeImporter(object):

    def import_postcode_gss_codes(self, filepaths):
        PSQLImportAdapter().import_csv('postcode_gss_code_import.sh', filepaths)
