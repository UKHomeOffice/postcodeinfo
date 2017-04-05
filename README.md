# postcodeinfo

[![Code Climate](https://codeclimate.com/github/ministryofjustice/postcodeinfo/badges/gpa.svg)](https://codeclimate.com/github/ministryofjustice/postcodeinfo)


REST API for UK Postcode information 
====================================
Postcode lookup RESTful API service.

Data is taken from:
* [Ordnance Survey AddressBase Basic](http://www.ordnancesurvey.co.uk/business-and-government/products/addressbase.html)
* [National Statistics Postcode List](http://geoportal.statistics.gov.uk/geoportal)
* [Dept of Communities and Local Government list of local authorities](http://opendatacommunities.org/data/dev-local-authorities/)

No data is included in this project due to copyright/licensing.

_PLEASE NOTE_ the current version only supports _mainland Great Britain_ postcodes, as Northern Ireland postcode data is published separately. We're planning to support Northern Ireland postcodes soon - if it's important to you, please
[log an issue](https://github.com/ministryofjustice/postcodeinfo/issues)

Support
-------
There is no incident response _yet_ - coming soon.

Requirements
------------
#### Developing/Contributing
 * [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
 * [boot2docker](http://boot2docker.io/) (for Mac OS X/Windows, on linux you can install docker using your favourite package manager)
 * git (`brew install git`)

#### Production
 * docker
 * [Postgresql 9.3+](http://www.postgresql.org/) with the [postgis](http://postgis.net/) plugin


Setup
-----
### Pull down the repository

```bash
$ git clone https://github.com/ministryofjustice/postcodeinfo.git
$ cd postcodeinfo
```

### Make sure you've forwarded the correct ports (only for boot2docker)

boot2docker works by starting a virtualbox VM and running docker inside it. When we forward ports using the -p or -P flag in docker, we need to do an extra step to make sure those are visible to the outside.

```bash
$ boot2docker init
$ VBoxManage modifyvm "boot2docker-vm" --natpf1 "tcp-port8000,tcp,,8000,,8000";
$ VBoxManage modifyvm "boot2docker-vm" --natpf1 "tcp-port5432,tcp,,5432,,5432";
$ boot2docker up
```
Note: this only needs running once

### Bring up the development environment
The commands below will create two docker instances, one for keeping the database (postgresql + postgis) and the other for running the django code by issuing `./manage.py runserver`
Once they're both up you can edit the code in the repository and you should be able to see your changes immediately on `http://localhost:8000`

```bash
$ $(boot2docker shellinit)
$ ./dev.sh
```
Note: If you want to execute custom commands inside the docker container you can easily do so by opening up a new shell and running the commands in the container. There's an example on how to do so in the next section (Creating a superuser)

### Create a superuser (optional)
If you need to use the django built-in admin interface you would need to create an user. We can do so by executing the createsuperuser command in the running container:

```bash
$ $(boot2docker shellinit)
$ docker exec -ti postcodeinfo ./manage.py createsuperuser
```

### Setting variables used inside the container
In the `Dockerfile` you will find the complete list of variables that are used by apps running inside the container.
Most defaults will make a dev environment ready to be used, the only exceptions being the FTP credentials.
You can easily change the value of any of the variables by prefixing the `./dev.sh` command with the var assignment. Ex:

```bash
$ OS_FTP_USERNAME="myuser" OS_FTP_PASSWORD="mypass" ./dev.sh
```

That will define the `OS_FTP_USERNAME` and `OS_FTP_PASSWORD` variables inside the dev environment as long as the container is running.
Any subsequent `docker exec` command will have those variables defined.

### Download and Import Data
In order to download and import the data we must execute the `download_and_import_all` command. We can either do that as in the "Create a superuser" section, or get a shell inside the container like so:

```bash
$ $(boot2docker shellinit)
$ docker exec -ti postcodeinfo /bin/bash
$ ./scripts/download_and_import_all.sh
$ exit
```

_This will take a long time to run - usually around 5hrs_

Keep in mind that for the download and import script to work, the correct ftp credentials need to be defined when setting the dev environment. See the `Setting variables used inside the container` section.

Note that it will keep a record of downloaded and imported files, comparing etag/last-modified timestamps and filenames to avoid re-downloading files it has already retrieved. This means that if your connection drops, you can restart, and existing files will be skipped.

Passing --force will force it to (re-)download everything, regardless of previous downloads.

Alternatively, you can download and/or import the three required datasets individually, trimming the amount of data in the import files as appropriate.

### Download / Import OS AddressBase Basic CSV files

Available from [Ordnance Survey](http://www.ordnancesurvey.co.uk/business-and-government/help-and-support/products/how-to-buy.html)

The interface is complex and tricky to navigate - instructions on how to order exactly what is needed are in [docs/ordering-addressbase.md]

OR 

Automatically download the latest version with:
```bash
$ ./manage.py download_addressbase_basic <destination_path>
```
You will need a valid FTP username and password from Ordnance Survey, and to set these values in OS_FTP_USERNAME and OS_FTP_PASSWORD environment variables. At the time of writing, the latest dataset consists of 29 x ~50MB files, so runtime will be heavily dependent on your bandwidth. However, if you just want to get something up and running and don't really need completeness, then just one datafile will be enough to get started - you don't necessarily _need_ them all.

Import AddressBase Basic files:
```bash
$ ./manage.py import_addressbase_basic <csv_path csv_path...>
```

Estimated runtime: ~ 1 minute per megabyte of downloaded data (zipped) - i.e. roughly 2.5 - 3 hrs for the full dataset

### Download / Import Local Authorities RDF .nt files

Available from The Dept for Communities and Local Government via [opendatacommunities.org](http://opendatacommunities.org/data/dev-local-authorities/), latest data dump: [http://opendatacommunities.org/data/dev-local-authorities/dump]

OR 

Automatically download the latest version with:
```bash
$ ./manage.py download_local_authorities <destination_path>
```

Import Local Authorities files:
```bash
$ ./manage.py import_local_authorities <nt_path nt_path...>
```

Estimated runtime: < 1 minute

### Download / Import NSPL Postcode/Local Authority GSS Code mapping files

Available from the [Office for National Statistics](http://www.ons.gov.uk/ons/guide-method/geography/products/postcode-directories/-nspp-/index.html) at their [Geoportal](http://geoportal.statistics.gov.uk/geoportal/catalog/main/home.page) (search for 'NSPL' to find the latest file)

OR 

Automatically download the latest version with:
```bash
$ ./manage.py download_postcode_gss_codes <destination_path>
```

Import Postcode / GSS Code files:
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

#### Postcode info - Lon/lat, Local Authority and Country lookup

```
http://127.0.0.1:8000/postcodes/sw1a1aa/
```

Example response:

```json
{
  "country": {
    "gss_code": "E92000001",
    "name": "England"
  },
  "local_authority": {
    "name": "Westminster",
    "gss_code": "E09000033"
  },
  "centre": {
    "type": "Point",
    "coordinates": [
      -0.141587558526369,
      51.50100893654096
    ]
  }
}
```

This method returns a lon/lat point for the centre of the specified postcode area only.

#### Partial postcode info - Lon/lat and Local Authority lookup

You can also perform partial postcode lookups using the partial/ endpoint:

```
http://127.0.0.1:8000/postcodes/partial/sw1a1aa/
```

Example response:

```json
{
  "local_authority": {
    "name": "Westminster",
    "gss_code": "E09000033"
  },
  "centre": {
    "type": "Point",
    "coordinates": [
      -0.141587558526369,
      51.50100893654096
    ]
  }
}
```

Note: the local authority is only a best-guess when using a partial postcode - a single postcode area may span several local authorities. In this case, the most-common local authority across all the postcodes in that area will be returned.

## API Client Libraries

There are 'official' API client libraries available for:
- Ruby [postcodeinfo-client-ruby](https://github.com/ministryofjustice/postcodeinfo-client-ruby)
- Python [postcodeinfo-client-python](https://github.com/ministryofjustice/postcodeinfo-client-python)
- PHP [postcodeinfo-client-php](https://github.com/ministryofjustice/postcodeinfo-client-php)

If you develop your own, feel free to let us know and we can link to it from here.
