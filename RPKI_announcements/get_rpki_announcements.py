#!/usr/bin/env python

import urllib
import datetime

now = datetime.datetime.now()
f = urllib.URLopener()
f.retrieve("http://localcert.ripe.net:8088/export.csv", now.strftime("%Y-%m-%d_%H:%M") + "_RPKI_announcements.csv")