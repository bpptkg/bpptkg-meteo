# Vaisala Pasarbubar

bpptkg-meteo vaisala app.

It downloads meteorology data from Pasarbubar station web service at
`192.168.9.47` and insert it to the database. Schema table is defined in
`meteo.models.cr6.CR6` class.

You can add another schema table in bpptkg-meteo package by submitting
pull/merge request to the project repository.

You can also write another app using bpptkg-meteo package.

Prior to running this script, you must create a database and migrate the model.
See `create-schema` script in `bin/` directory.

## Usage

Just provide SQLAlchemy database engine URL to the script argument and add the
script to the system crontab by 5 minutes or so. For example:

    source /path/to/venv/bin/activate
    python /path/to/vaisala/app.py -e 'mysql://user:password@127.0.0.1/meteo'

where `/path/to/venv/` is your path to Python virtual enviroment. Add `-v`
option to run the app in debugging mode.

Do not forget to install all package requirements prior to running the script:

    pip install -r /path/to/vaisala/requirements.txt

The script will create `last` file that store the latest meteorology data
timestamp in `data/` directory. You can view runtime log in `logs/` directory.

## Configure Settings Using .env File

Vaisala app settings can also be configured from `.env` file. See `.env.example`
file for example.

Create `.env` file on the same directory with `app.py` and write your settings
there.
