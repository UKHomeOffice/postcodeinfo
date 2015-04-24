# postcodeinfo
UK Postcode to addresses, lat/long, and local authority REST API
=======
Address Finder
==============

Postcode lookup HTTP/REST service using [Ordnance Survey AddressBase Basic](http://www.ordnancesurvey.co.uk/business-and-government/products/addressbase.html) data. No data is included in this project due to copyright/licensing.

Dependencies
------------

On MacOS:

`$ brew install python postgresql geos proj gdal postgis`

Stick the kettle on, it'll be a while.

Setup
-----

### Create GIS database

```bash
$ createdb postcodeinfo
$ psql postcodeinfo
```
```SQL
> CREATE EXTENSION postgis;
```

### Create virtualenv

```bash
$ pip install virtualenv
$ git clone https://github.com/ministryofjustice/postcodeinfo.git
$ cd postcodeinfo
$ virtualenv .venv
$ source .venv/bin/activate
```

### Install requirements

```bash
$ pip install -r requirements.txt
```

### Create database schema and superuser

```bash
$ ./manage.py syncdb
```

### Import OS AddressBase Basic CSV files

Available from [http://www.ordnancesurvey.co.uk/business-and-government/help-and-support/products/how-to-buy.html](Ordnance Survey)

```bash
$ ./manage.py import_addressbase_basic <csv_path csv_path...>
```

Estimated runtime: ~ 1 minute

### Import Local Authorities RDF .nt files

Available from The Dept for Communities and Local Government via [http://opendatacommunities.org/data/dev-local-authorities/](opendatacommunities.org), latest data dump: [http://opendatacommunities.org/data/dev-local-authorities/dump]

```bash
$ ./manage.py import_local_authorities <nt_path nt_path...>
```

Estimated runtime: ~ 1 minute

### Import NSPL Postcode/Local Authority GSS Code mapping files

Available from the [http://www.ons.gov.uk/ons/guide-method/geography/products/postcode-directories/-nspp-/index.html](Office for National Statistics) at their [https://geoportal.statistics.gov.uk/geoportal/catalog/main/home.page](Geoportal) (search for 'NSPL' to find the latest file)

```bash
$ ./manage.py import_postcode_gss_codes <csv_path csv_path...>
```

Estimated runtime: ~ 2 hours

### Start dev server

```bash
$ ./manage.py runserver
```

You can now access [Django Admin](http://127.0.0.1/admin/authtoken/token/) to create a token for your superuser.

## Usage

Access the API with your token in the Authorization header:

```Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b```

Postcodes can be specified in upper or lowercase, with or without spaces.

#### Address lookup
```
http://127.0.0.1:8000/addresses/?postcode=sw1a1aa
```

You can specify which fields you want in the response with the `fields` kwarg:

```
http://127.0.0.1:8000/addresses/?postcode=sw1a1aa&fields=formatted_address,point
```

View the available fields [here](https://github.com/ministryofjustice/postcodeinfo/blob/develop/postcodeinfo/apps/postcode_api/serializers.py#L25)

Example response:

```json
[
  {
    "uprn": "10033544614",
    "organisation_name": "BUCKINGHAM PALACE",
    "department_name": "",
    "po_box_number": "",
    "building_name": "",
    "sub_building_name": "",
    "building_number": null,
    "thoroughfare_name": "",
    "dependent_thoroughfare_name": "",
    "dependent_locality": "",
    "double_dependent_locality": "",
    "post_town": "LONDON",
    "postcode": "SW1A 1AA",
    "postcode_type": "L",
    "formatted_address": "Buckingham Palace\nLondon\nSW1A 1AA",
    "point": {
      "type": "Point",
      "coordinates": [
        -0.141587558526369,
        51.50100893654096
      ]
    }
  }
]
```

#### Postcode info - Lat/lon and Local Authority lookup

```
http://127.0.0.1:8000/postcodes/sw1a1aa/
```

Example response:

```json
{
  "type": "Point",
  "local_authority": {
    "name": "Westminster",
    "gss_code": "E09000033"
  }
  "coordinates": [
    -0.141587558526369,
    51.50100893654096
  ]
}
```

This method returns a lat/lon point for the centre of the specified postcode area only.

#### Partial postcode info - Lat/lon and Local Authority lookup

You can also perform partial postcode lookups useing the partial/ endpoint:

```
http://127.0.0.1:8000/postcodes/partial/sw1a1aa/
```

Example response:

```json
{
  "type": "Point",
  "local_authority": {
    "name": "Westminster",
    "gss_code": "E09000033"
  }
  "coordinates": [
    -0.141587558526369,
    51.50100893654096
  ]
}

Note: the local authority is only a best-guess when using a partial postcode - a single postcode area may span several local authorities. In this case, the most-common local authority across all the postcodes in that area will be returned.

