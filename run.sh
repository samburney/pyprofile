#!/bin/sh

export FLASK_APP=pyprofile
export FLASK_ENV=development

flask run -h 0.0.0.0
