from postcode_api.importers.psql_import_adapter import PSQLImportAdapter

class AddressBaseBasicImporter(object):

    def import_csv(self, filepaths):
        PSQLImportAdapter().import_csv('addressbase_import.sh', filepaths)

