#!/bin/bash
exec gunicorn -c assets/gunicorn-conf.py 'launcher:app'
