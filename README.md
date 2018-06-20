# Document topics annotation interface

A Django project for collecting topic term annotations on TREC documents. Users are asked to read documents and, after reading each document, select the terms that they feel best represent the main topic(s) of the document.

## Data

Data for the interface is sampled using [this code](https://github.com/gtsherman/document-expansion/blob/master/src/main/kotlin/org/retrievable/documentExpansion/main/CollectUserStudyData.kt), which provides a comma-delimited list of document and available topic terms:

```
docno1,term1,term2,...
docno2,term3,term4,term5,...
```

This data can be run through [this script](https://github.com/gtsherman/document-expansion-experiments/blob/master/user-study/get_document_text.py) (which will need adapting to any specific system) to collect the full text of each document and perform minor but important formatting. The result will be a JSON-formatted file.

Full text of documents can be loaded into the interface with the `insertdocs` command:

```
$ python manage.py insertdocs /path/to/json_file
```

Next, insert the CSV of topic term options with the `insertterms` command:

```
$ python manage.py insertterms /path/to/csv_file
```

If you need to start over, the `cleardata` command will wipe out both documents and terms from the database. When recording is complete, the `dumprecorded` command will produce a CSV of the topic terms selected by each user for each document.

## Running

Before running, you must first create and activate the project's virtualenv:

```
$ virtualenv env
$ source env/bin/activate
```

Install the requirements:

```
$ pip install -r requirements.txt
```

### Development

For a quick test run, use Django's built-in server:

```
$ python manage.py runserver
```

Then navigate to http://localhost:8000 in your browser.

### Production

#### nginx

Install nginx using your system's package manager (e.g. `apt-get install nginx`) or manually.

Create a file (say, `topicterms`) in `/etc/nginx/sites-available`:

```
server {
  listen 80;
  server_name [host name or IP];
  
  location /static/ {
    root /path/to/static/dir;
  }
  
  location / {
    proxy_pass http://unix:/path/to/gunicorn.socket;
  }
}
```

#### gunicorn

Simply activate the virtualenv and install gunicorn:

```
$ source env/bin/activate
$ pip install gunicorn
```

Next, create a user who will be responsible for running gunicorn. In Ubuntu, this looks like:

```
$ sudo adduser gunicorn
$ [fill out the info]
$ sudo adduser gunicorn www-data
```

We also need to create a space to contain the gunicorn socket:

```
$ mkdir /path/to/run
$ sudo chown [user]:www-data /path/to/run
```

#### supervisord

Although systemd or another distro-specific solution could work, supervisord is a bit more cross-platform and, for me, a bit easier to understand.

First, install using your system's package manager or manually. Then create a file (say, `gunicorn.conf`) in `/etc/supervisor/conf.d`:

```
[program:gunicorn]
directory=/path/to/project
command=/path/to/env/bin/gunicorn --workers 3 --bind unix:/path/to/gunicorn.socket interface.wsgi
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gunicorn.log
user=gunicorn
```

Finally, reload supervisor:

```
$ sudo supervisorctl reread
$ sudo supervisorctl update
```

#### SSL

Optionally (but advisedly), use [certbot](https://certbot.eff.org/) to add encryption to the site to protect user logins and data.
