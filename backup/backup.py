#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil

try:
  shutil.copy("*", "/media/mmc1/mybackup/*")
except:
  print "io error"
finally:
  print "backup completed"
