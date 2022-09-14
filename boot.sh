#!/bin/bash

flask --app app init-db
exec gunicorn -b 0.0.0.0:8000 -w 5 folderbe:app