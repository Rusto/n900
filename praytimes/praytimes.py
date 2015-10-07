# -*- coding: utf-8 -*-
#!/usr/bin/env python
# compatible with python 2.x and 3.x

import numpy
import re
import calendar
import datetime

'''
--------------------- Copyright Block ----------------------

praytimes.py: Prayer Times Calculator (ver 2.3)
Copyright (C) 2007-2011 PrayTimes.org

Python Code: Saleem Shafi, Hamid Zarrabi-Zadeh
Original js Code: Hamid Zarrabi-Zadeh

License: GNU LGPL v3.0

TERMS OF USE:
	Permission is granted to use this code, with or
	without modification, in any website or application
	provided that credit is given to the original work
	with a link back to PrayTimes.org.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY.

PLEASE DO NOT REMOVE THIS COPYRIGHT BLOCK.

--------------------- Help and Manual ----------------------

User's Manual:
http://praytimes.org/manual

Calculation Formulas:
http://praytimes.org/calculation

------------------------ User Interface -------------------------

	getTimes (date, coordinates, timeZone [, dst [, timeFormat]])

	setMethod (method)       // set calculation method
	adjust (parameters)      // adjust calculation parameters
	tune (offsets)           // tune times by given offsets

	getMethod ()             // get calculation method
	getSetting ()            // get current calculation parameters
	getOffsets ()            // get current time offsets

	#
	##
	### calculation of Hijra date

	getHijra (date)

	setBoundary (hijraTimeName) // set time when switch date 

	getBoundary ()            // get time when switch date

	###
	##
	#

------------------------- Sample Usage --------------------------

	>>> PT = PrayTimes('ISNA')
	>>> times = PT.getTimes((2011, 2, 9), (43, -80), -5)
	>>> times['sunrise']
	07:26

-----------------------------------------------------------------
'''

#----------------------- PrayTimes Class ------------------------

class PrayTimes():

	#------------------------ Constants --------------------------

	# Time Names
	timeNames = {
		'imsak'    : 'Imsak',
		'fajr'     : 'Fajr',
		'sunrise'  : 'Sunrise',
		'dhuhr'    : 'Dhuhr',
		'asr'      : 'Asr',
		'sunset'   : 'Sunset',
		'maghrib'  : 'Maghrib',
		'isha'     : 'Isha',
		'midnight' : 'Midnight'
	}

	# Calculation Methods
	methods = {
		'MWL': {
			'name': 'Muslim World League',
			'params': { 'fajr': 18, 'isha': 17 } },
		'ISNA': {
			'name': 'Islamic Society of North America (ISNA)',
			'params': { 'fajr': 15, 'isha': 15 } },
		'Egypt': {
			'name': 'Egyptian General Authority of Survey',
			'params': { 'fajr': 19.5, 'isha': 17.5 } },
		'Makkah': {
			'name': 'Umm Al-Qura University, Makkah',
			'params': { 'fajr': 18.5, 'isha': '90 min' } },  # fajr was 19 degrees before 1430 hijri
		'Karachi': {
			'name': 'University of Islamic Sciences, Karachi',
			'params': { 'fajr': 18, 'isha': 18 } },
		'Tehran': {
			'name': 'Institute of Geophysics, University of Tehran',
			'params': { 'fajr': 17.7, 'isha': 14, 'maghrib': 4.5, 'midnight': 'Jafari' } },  # isha is not explicitly specified in this method
		'Jafari': {
			'name': 'Shia Ithna-Ashari, Leva Institute, Qum',
			'params': { 'fajr': 16, 'isha': 14, 'maghrib': 4, 'midnight': 'Jafari' } },
		'Kaz': {
			'name': 'Kazakhstan',
			# from 20 march to 21 september 95 min annualy
			'params': { 'fajr': '120 min', 'isha': '-90 min' } }
	}

	# Default Parameters in Calculation Methods
	defaultParams = {
		'maghrib': '0 min', 'midnight': 'Standard'
	}

	# 1 january 2000 12:00
	epoch = 2451545.0
	# 17 november 1858 00:00
	#epoch = 2400000.5
	fractionalMonth = 29.53058796

	weekDays = ["al-Ithnayn", "ath-Thulāthāʼ", "al-Arbi‘ā’", "al-Khamīs", "al-Jumu‘ah", "as-Sabt", "al-Aḥad"]
	months = ["Muḥarram", "Ṣafar", "Rabī‘ al-Awwal", "Rabī‘ ath-Thānī", "Jumādá al-Ūlá", "Jumādá ath-Thāniyah", "Rajab", "Sha‘bān", "Ramaḍān", "Shawwāl", "Dhū al-Qa‘dah", "Dhū al-Ḥijjah"]


	#---------------------- Default Settings --------------------

	calcMethod = 'MWL'

	# do not change anything here; use adjust method instead
	settings = {
		"imsak"    : '10 min',
		"dhuhr"    : '0 min',
		"asr"      : 'Standard',
		"highLats" : 'NightMiddle'
	}

	timeFormat = '24h'
	timeSuffixes = ['am', 'pm']
	invalidTime =  '-----'

	numIterations = 1
	offset = {}

	# Hijra date change in Magrib
	hijraTimeName = 'Maghrib'

	#---------------------- Initialization -----------------------

	# !!! fixed trouble - added initMethod variable
	# he had always switched on last method in self.methods ['MWL' ]

	def __init__(self, initMethod = "MWL") :

		# set methods defaults
		for method, config in self.methods.items():
			for name, value in self.defaultParams.items():
				if not name in config['params'] or config['params'][name] is None:
					config['params'][name] = value

		# initialize settings
		self.calcMethod = initMethod if initMethod in self.methods else "MWL"
		params = self.methods[self.calcMethod]['params']
		for name, value in params.items():
			self.settings[name] = value

		# init time offsets
		for name in self.timeNames:
			self.offset[name] = 0

	#-------------------- Interface Functions --------------------

	def setMethod(self, method):
		if method in self.methods:
			self.adjust(self.methods[method].params)
			self.calcMethod = method

	def adjust(self, params):
		self.settings.update(params)

	def tune(self, timeOffsets):
		self.offsets.update(timeOffsets)

	def getMethod(self):
		return self.calcMethod

	def getSettings(self):
		return self.settings

	def getOffsets(self):
		return self.offset

	def getDefaults(self):
		return self.methods

	# return prayer times for a given date
	def getTimes(self, date, coords, timezone, dst = 0, format = None):
		self.lat = coords[0]
		self.lng = coords[1]
		self.elv = coords[2] if len(coords) > 2 else 0
		if format != None:
			self.timeFormat = format
		if type(date).__name__ == 'date':
			date = (date.year, date.month, date.day)
		self.timeZone = timezone + (1 if dst else 0)
		self.jDate = self.julian(date[0], date[1], date[2]) - self.lng / (15 * 24.0)
		return self.computeTimes()

	# convert float time to the given format (see timeFormats)
	def getFormattedTime(self, time, format, suffixes = None):
		if numpy.isnan(time):
			return self.invalidTime
		if format == 'Float':
			return time
		if suffixes == None:
			suffixes = self.timeSuffixes

		time = self.fixhour(time + 0.5 / 60)  # add 0.5 minutes to round
		hours = numpy.floor(time)

		minutes = numpy.floor((time - hours)* 60)
		suffix = suffixes[ 0 if hours < 12 else 1 ] if format == '12h' else ''
		formattedTime = "%02d:%02d" % (hours, minutes) if format == "24h" else "%d:%02d" % ((hours + 11) % 12 + 1, minutes)
		return formattedTime + suffix

	# return Hijra date for a given date
	def getHijra(self, date):
		return self.computeHijraDate(date)

	# set time when switch date 
	def setBoundary(self, hijraTimeName):
		self.hijraTimeName = hijraTimeName

	# get time when switch date
	def getBoundary(self):
		return self.hijraTimeName

	#---------------------- Calculation Functions -----------------------

	# compute mid-day time
	def midDay(self, time):
		eqt = self.sunPosition(self.jDate + time)[1]
		return self.fixhour(12 - eqt)

	# compute the time at which sun reaches a specific angle below horizon
	def sunAngleTime(self, angle, time, direction = None):
		try:
			decl = self.sunPosition(self.jDate + time)[0]
			noon = self.midDay(time)
			t = 1 / 15.0 * self.arccos((-self.sin(angle) - self.sin(decl) * self.sin(self.lat)) / (self.cos(decl) * self.cos(self.lat)))
			return noon + (-t if direction == 'ccw' else t)
		except ValueError:
			return float('nan')

	# compute asr time
	def asrTime(self, factor, time):
		decl = self.sunPosition(self.jDate + time)[0]
		angle = -self.arccot(factor + self.tan(abs(self.lat - decl)))
		return self.sunAngleTime(angle, time)

	# compute declination angle of sun and equation of time
	# Ref: http://aa.usno.navy.mil/faq/docs/SunApprox.php
	def sunPosition(self, jd):
		D = jd - 2451545.0
		g = self.fixangle(357.529 + 0.98560028 * D)
		q = self.fixangle(280.459 + 0.98564736 * D)
		L = self.fixangle(q + 1.915 * self.sin(g) + 0.020 * self.sin(2 * g))

		R = 1.00014 - 0.01671 * self.cos(g) - 0.00014 * self.cos(2 * g)
		e = 23.439 - 0.00000036 * D

		RA = self.arctan2(self.cos(e) * self.sin(L), self.cos(L)) / 15.0
		eqt = q / 15.0 - self.fixhour(RA)
		decl = self.arcsin(self.sin(e) * self.sin(L))

		return (decl, eqt)

	# convert Gregorian date to Julian day
	# Ref: Astronomical Algorithms by Jean Meeus
	def julian(self, year, month, day):
		if month <= 2:
			year -= 1
			month += 12
		A = numpy.floor(year / 100)
		B = 2 - A + numpy.floor(A / 4)
#		return numpy.floor(365.25 * (year + 4716)) + numpy.floor(30.6001 * (month + 1)) + day + B - 1524.5
		return numpy.floor(365.25 * (year + 4716)) + numpy.floor(30.6001 * (month + 1)) + day + B - 1524.5

	#---------------------- Compute Prayer Times -----------------------

	# compute prayer times at given julian date
	def computePrayerTimes(self, times):
		times = self.dayPortion(times)
		params = self.settings

		imsak   = self.sunAngleTime(self.eval(params['imsak']), times['imsak'], 'ccw')
		fajr    = self.sunAngleTime(self.eval(params['fajr']), times['fajr'], 'ccw')
		sunrise = self.sunAngleTime(self.riseSetAngle(self.elv), times['sunrise'], 'ccw')
		dhuhr   = self.midDay(times['dhuhr'])
		asr     = self.asrTime(self.asrFactor(params['asr']), times['asr'])
		sunset  = self.sunAngleTime(self.riseSetAngle(self.elv), times['sunset'])
		maghrib = self.sunAngleTime(self.eval(params['maghrib']), times['maghrib'])
		isha    = self.sunAngleTime(self.eval(params['isha']), times['isha'])
		return {
			'imsak': imsak, 'fajr': fajr, 'sunrise': sunrise, 'dhuhr': dhuhr,
			'asr': asr, 'sunset': sunset, 'maghrib': maghrib, 'isha': isha
		}

	# compute prayer times
	def computeTimes(self):
		times = {
			'imsak': 5, 'fajr': 5, 'sunrise': 6, 'dhuhr': 12,
			'asr': 13, 'sunset': 18, 'maghrib': 18, 'isha': 18
		}
		# main iterations
		for i in range(self.numIterations):
			times = self.computePrayerTimes(times)
		times = self.adjustTimes(times)
		# add midnight time
		if self.settings['midnight'] == 'Jafari':
			times['midnight'] = times['sunset'] + self.timeDiff(times['sunset'], times['fajr']) / 2
		else:
			times['midnight'] = times['sunset'] + self.timeDiff(times['sunset'], times['sunrise']) / 2

		times = self.tuneTimes(times)
		return self.modifyFormats(times)

	# adjust times in a prayer time array
	def adjustTimes(self, times):
		params = self.settings
		tzAdjust = self.timeZone - self.lng / 15.0
		for t, v in times.items():
			times[t] += tzAdjust

		if params['highLats'] != 'None':
			times = self.adjustHighLats(times)

		# !!! for Kazakhstan - 'Kaz' method
		if self.isMin(params['fajr']):
			times['fajr'] = times['sunrise'] - self.eval(params['fajr']) / 60.0

		if self.isMin(params['imsak']):
			times['imsak'] = times['fajr'] - self.eval(params['imsak']) / 60.0
		# need to ask about 'min' settings
		if self.isMin(params['maghrib']):
			times['maghrib'] = times['sunset'] - self.eval(params['maghrib']) / 60.0

		if self.isMin(params['isha']):
			times['isha'] = times['maghrib'] - self.eval(params['isha']) / 60.0
		times['dhuhr'] += self.eval(params['dhuhr']) / 60.0

		return times

	# get asr shadow factor
	def asrFactor(self, asrParam):
		methods = {'Standard': 1, 'Hanafi': 2}
		return methods[asrParam] if asrParam in methods else self.eval(asrParam)

	# return sun angle for sunset/sunrise
	def riseSetAngle(self, elevation = 0):
		elevation = 0 if elevation == None else elevation
		return 0.833 + 0.0347 * numpy.sqrt(elevation) # an approximation

	# apply offsets to the times
	def tuneTimes(self, times):
		for name, value in times.items():
			times[name] += self.offset[name] / 60.0
		return times

	# convert times to given time format
	def modifyFormats(self, times):
		for name, value in times.items():
			times[name] = self.getFormattedTime(times[name], self.timeFormat)
		return times

	# adjust times for locations in higher latitudes
	def adjustHighLats(self, times):
		params = self.settings
		nightTime = self.timeDiff(times['sunset'], times['sunrise']) # sunset to sunrise
		times['imsak'] = self.adjustHLTime(times['imsak'], times['sunrise'], self.eval(params['imsak']), nightTime, 'ccw')
		times['fajr'] = self.adjustHLTime(times['fajr'], times['sunrise'], self.eval(params['fajr']), nightTime, 'ccw')
		times['isha'] = self.adjustHLTime(times['isha'], times['sunset'], self.eval(params['isha']), nightTime)
		times['maghrib'] = self.adjustHLTime(times['maghrib'], times['sunset'], self.eval(params['maghrib']), nightTime)
		return times

	# adjust a time for higher latitudes
	def adjustHLTime(self, time, base, angle, night, direction = None):
		portion = self.nightPortion(angle, night)
		diff = self.timeDiff(time, base) if direction == 'ccw' else self.timeDiff(base, time)
		if numpy.isnan(time) or diff > portion:
			time = base + (-portion if direction == 'ccw' else portion)
		return time

	# the night portion used for adjusting times in higher latitudes
	def nightPortion(self, angle, night):
		method = self.settings['highLats']
		portion = 1 / 2.0  # midnight
		if method == 'AngleBased':
			portion = 1 / 60.0 * angle
		if method == 'OneSeventh':
			portion = 1 / 7.0
		return portion * night

	# convert hours to day portions
	def dayPortion(self, times):
		for i in times:
			times[i] /= 24.0
		return times

	#---------------------- Compute Hijra Date -----------------------

	def moonPhases(self, julianDay):
		T = (julianDay - self.epoch) / 36525.0
		mE = 297.8502042 + T * 445267.1115168 - numpy.power(T, 2) * 0.0016300 + numpy.power(T, 3) / 545868.0 - numpy.power(T, 4) / 113065000
		mA = 134.9634114 + T * 477198.8676313 + numpy.power(T, 2) * 0.0089970 + numpy.power(T, 3) / 69699.0 - numpy.power(T, 4) / 863310000.0
		SmA = 357.5291092 + T * 35999.0502909 - numpy.power(T, 2) * 0.0001536 + numpy.power(T, 3) / 24490000
		D = self.fixangle(mE)
		S = self.fixangle(SmA)
		M = self.fixangle(mA)
		phaseAngle = 180 - D - 6.289 * self.sin(M) + 2.1 * self.sin(S) - 1.274 * self.sin(self.fixangle(2 * D) - M) - 0.658 * self.sin(2 * D)
		phaseAngle += -0.214 * self.sin(2 * M) 
		phaseAngle += -0.110 * self.sin(D)
		iF = (1 + self.cos(phaseAngle)) / 2 * (phaseAngle / numpy.fabs(phaseAngle))
		return iF

	def pcision(self, F):
		# calculate moon day
		### add sunset - sunrise
		### if now > sunset: day += 1
		status = True
		Dn = 0
		jDn = F
		if self.moonPhases(jDn - 1) <= 0: 
			jDn -= 1
			Dn += 1
		while status:
			Fn = self.moonPhases(jDn)
			Fn2 = self.moonPhases(jDn - 1)
			if ((Fn / numpy.fabs(Fn)) * (Fn2 / numpy.fabs(Fn2))) == 1:
				Dn += 1
				jDn -= 1
			else:
				if numpy.fabs(Fn * Fn2) < 0.2: status = False
				else:
					Dn += 1
					jDn -= 1
		return Dn

	# compute of Hijri date based on a known Gregorian date
	def computeHijraDate(self, date):
		timeTuple = date.timetuple()
		year    = date.year
		#month   = date.month
		#day     = date.day
		hours   = timeTuple[3]
		minutes = timeTuple[4]
		seconds = timeTuple[5]

		deltaDays = self.jDate - self.julian(year, 1, 1)
		fractionalYear = (year + deltaDays / (365 + calendar.isleap(year)) - 621.578082192) / 0.97022298
		fractionalYear += numpy.floor(numpy.fabs(fractionalYear) / 3000) * 30 / 10631
		fractionalDay = fractionalYear - numpy.floor(fractionalYear)

		hijraYear = fractionalYear - fractionalDay

		if ((fractionalDay * 10631 / 30) - numpy.floor(fractionalDay * 10631 / 30) < 0.5):
		    fractionalDay = numpy.floor(fractionalDay * 10631 / 30) + 1
		else: fractionalDay = numpy.floor(fractionalDay * 10631 / 30) + 2

		gregorianYear = hijraYear * 0.970224044 + 621.574981435
		gregorianFractionalDay = gregorianYear - numpy.floor(gregorianYear)
		gregorianYear -= gregorianFractionalDay
		gregorianDay = numpy.floor((365 + calendar.isleap(gregorianYear)) * gregorianFractionalDay) + 1
		gregorianYear += gregorianDay / (365 + calendar.isleap(gregorianYear))
		hijraFractionalYear = (gregorianYear - 621.574981435) / 0.970224044
		hijraFractionalDay = hijraFractionalYear - numpy.floor(hijraFractionalYear)
		hijraDay = hijraFractionalDay * 10631 / 30 + 1;
		hijraMonth = 1
		hijraFractionalDay = 1
		while hijraFractionalDay < fractionalDay:
		    hijraDay += 1
		    hijraFractionalDay += 1
		    if hijraDay >= self.fractionalMonth:
		        hijraDay = hijraDay - self.fractionalMonth
		        hijraMonth += 1
		hijraDay = numpy.floor(hijraDay) + 1
		if hijraMonth == 13:
		    hijraMonth = 1
		    hijraYear += 1
		partDay = (hours + minutes / 60 + seconds / 3600) / 24
		precise = self.pcision(self.jDate + partDay)
		if hijraDay != precise:
		    if (hijraDay == 1) and (precise > 28):
		        hijraMonth -= 1
		        if hijraMonth == 0: 
		            hijraMonth = 12
		            hijraYear -= 1
		    elif (hijraDay > 28) and (precise < 3):
		        hijraMonth += 1
		        if hijraMonth == 13:
		            hijraMonth = 1
		            hijraYear += 1
		hijraDay = precise
		if hijraYear < 1: hijraYear -= 1

		return str(hijraDay) + "\n" + self.months[hijraMonth - 1] + "\n" + str(int(hijraYear)) + "\n" + self.weekDays[timeTuple[6]]

	#---------------------- Misc Functions -----------------------

	# compute the difference between two times
	def timeDiff(self, time1, time2):
		return self.fixhour(time2 - time1)

	# convert given string into a number
	def eval(self, st):
		val = re.split('[^0-9.+-]', str(st), 1)[0]
		return float(val) if val else 0

	# detect if input contains 'min'
	def isMin(self, arg):
		return isinstance(arg, str) and arg.find('min') > -1

	#----------------- Degree-Based Math Functions -------------------

	def sin(self, d): return numpy.sin(numpy.radians(d))
	def cos(self, d): return numpy.cos(numpy.radians(d))
	def tan(self, d): return numpy.tan(numpy.radians(d))

	def arcsin(self, x): return numpy.degrees(numpy.arcsin(x))
	def arccos(self, x): return numpy.degrees(numpy.arccos(x))
	def arctan(self, x): return numpy.degrees(numpy.arctan(x))

	def arccot(self, x): return numpy.degrees(numpy.arctan(1.0/x))
	def arctan2(self, y, x): return numpy.degrees(numpy.arctan2(y, x))

	def fixangle(self, angle): return self.fix(angle, 360.0)
	def fixhour(self, hour): return self.fix(hour, 24.0)

	def fix(self, a, mode):
		if numpy.isnan(a):
			return a
		a = a - mode * (numpy.floor(a / mode))
		return a + mode if a < 0 else a

#---------------------- prayTimes Object -----------------------

prayTimes = PrayTimes('Kaz')
prayTimes.adjust({"imsak": '30 min'})
prayTimes.adjust({"asr": 'Hanafi'})

#-------------------------- Test Code --------------------------

# sample code to run in standalone mode only
if __name__ == "__main__":
	date = datetime.date.today()
	#print('Prayer Times for ' + date.strftime("%e %b %Y, %A") + ' in Karaganda/Kazakhstan')
	if ((date.month == 3) and (date.day >= 20)) or ((date.month > 3) and (date.month < 9)) or ((date.month == 9) and (date.day <= 21)): prayTimes.adjust({"isha": '-95 min'})
	else: prayTimes.adjust({"isha": '-90 min'})
	times = prayTimes.getTimes(date.today(), (49.89362, 73.18815), 6);
	print prayTimes.getHijra(date)
	#print '=' * 20

	#
	##
	### added to determine the time of Fajr on fazilet
	prayTimesMWL = PrayTimes('MWL')
	prayTimesMWL.adjust({"imsak": '10 min'})
	prayTimesMWL.adjust({"asr": 'Hanafi'})
	if ((date.month == 3) and (date.day >= 20)) or ((date.month > 3) and (date.month < 9)) or ((date.month == 9) and (date.day <= 21)): prayTimesMWL.adjust({"isha": '-95 min'})
	else: prayTimesMWL.adjust({"isha": '-90 min'})
	timesMWL = prayTimesMWL.getTimes(date.today(), (49.89362, 73.18815), 6);
	for i in ['Imsak', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
		if timesMWL[i.lower()] <> times[i.lower()]: times[i.lower()] = timesMWL[i.lower()] + "/" + times[i.lower()]
		#if i == prayTimes.hijraTimeName: times[i.lower()] = times[i.lower()] + " *"
	###
	##
	#

	for i in ['Imsak', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha', 'Midnight']:
		#print(i+ ': '+ times[i.lower()])
		print(times[i.lower()])
