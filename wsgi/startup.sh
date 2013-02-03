#!/bin/sh
cd /home/projects/openebs/wsgi
/usr/bin/uwsgi -L -s 127.0.0.1:9003 --plugins python27 -w openebs --logto /home/projects/openebs/log/openebs.log
