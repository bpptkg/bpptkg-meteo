# Vaisala Babadan

## Overview

Vaisala Babadan downloads meteorology data from Babadan weather device at telnet
server `192.168.62.77` port 2020 and insert it to the database at minute
interval. Schema table is defined in `meteo.models.bbd.Babadan` class.

Prior to running this script, you must create a database and migrate the model.
See `create-schema` script in the `bin/` directory.

## Deploying

Clone the project from GitLab repository:

    git clone https://github.com/bpptkg/bpptkg-meteo.git

Change directory to vaisala-bbd:

    cd /path/to/bpptkg-meteo/examples/vaisala-bbd

Create virtual environment folder and activate the environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Install all package requirements:

    pip install -r requirements.txt

Then configure your environment variables. Create `.env` file on the top project
directory and write your settings there. See `.env.example` file for example.

Copy Supervisor configuration file from `supervisor/vaisala-bbd.conf` to
`/etc/supervisor/conf.d/vaisala-bbd.conf`. Then, edit the conf file according to
your needs, particularly the path to the deployed vaisala-bbd directory.

    cp supervisor/vaisala-bbd.conf /etc/supervisor/conf.d/
    vim /etc/supervisor/conf.d/vaisala-bbd.conf

Reread and update Supervisor configuration:

    sudo supervisorctl reread
    sudo supervisorctl update
