#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil

shutil.copy('conky', 'conky.conf')

praytimes = open('praytimes', 'r')
source = open('conky', 'r')
target = open('conky.conf', 'w')

inserting = 0
for line in source.readlines():	


	if "HIJRADAY" in line:
		line.replace('HIJRADAY', praytimes.readline().replace('\n', ''))


	if "${color grey}${goto 225}Top CPU" in line: inserting += 1
	if (inserting):
		if inserting == 1:
			line = '${color red}' + praytimes.readline().replace('\n', ' ') + '${color grey}' + praytimes.readline().replace('\n', ' ') + '${color red}' + praytimes.readline().replace('\n', '') + line
		elif inserting == 2:
			line = '$color' + praytimes.readline
		
		elif inserting < 13:
			line = praytimes.readline().replace('\n', '') + line
		inserting += 1
	target.write(line)

praytimes.close
source.close
target.close

#shutil.move('conky.conf', '/etc/conky/conky.conf')
