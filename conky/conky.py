#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil

#shutil.copy('conky', 'conky.conf')

praytimes = open('praytimes', 'r')
source = open('conky', 'r')
target = open('conky.conf', 'w')

for line in source.readlines():	

	targetline = line
	if "HIJRADAY" in line:
		targetline = line.replace('HIJRADAY', praytimes.readline().replace('\n', ''))
		targetline = targetline.replace('HIJRAMONTH', praytimes.readline().replace('\n', ''))
		targetline = targetline.replace('HIJRAYEAR', praytimes.readline().replace('\n', ''))
	if "HIJRAWEEKDAY" in line:
		targetline = line.replace('HIJRAWEEKDAY', praytimes.readline().replace('\n', ''))
	if "IMSAKTIME" in line:
		targetline = line.replace('IMSAKTIME', praytimes.readline().replace('\n', ''))
	if "FAJRTIME" in line:
		targetline = line.replace('FAJRTIME', praytimes.readline().replace('\n', ''))
	if "SUNRICETIME" in line:
		targetline = line.replace('SUNRICETIME', praytimes.readline().replace('\n', ''))
	if "DHUHRTIME" in line:
		targetline = line.replace('DHUHRTIME', praytimes.readline().replace('\n', ''))
	if "ASRTIME" in line:
		targetline = line.replace('ASRTIME', praytimes.readline().replace('\n', ''))
	if "MAGRIBTIME" in line:
		targetline = line.replace('MAGRIBTIME', praytimes.readline().replace('\n', ''))
	if "ISHATIME" in line:
		targetline = line.replace('ISHATIME', praytimes.readline().replace('\n', ''))
	if "MIDNIGHTTIME" in line:
		targetline = line.replace('MIDNIGHTTIME', praytimes.readline().replace('\n', ''))
	target.write(targetline)

praytimes.close
source.close
target.close

#shutil.move('conky.conf', '/etc/conky/conky.conf')
