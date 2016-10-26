""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Plugin for Withing device

Implements
==========

class WITHING, withingException

@author: tikismoke
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""
from __future__ import unicode_literals

import traceback
import subprocess
try:
    import requests
    from requests_oauthlib import OAuth1
    import withings
    from withings import WithingsAuth, WithingsApi

except RuntimeError:
    self._log.debug(u"Error importing withing!")

import sys
import os
import pickle
import locale
import time

class withingException(Exception):
    """
    WITHING exception
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class WITHINGclass:
    """
    Get informations about withing
    """
    # -------------------------------------------------------------------------------------------------
    def __init__(self, log, api_id, api_secret, period, dataPath):
        try:
            """
            Create a withing instance, allowing to use withing api
            """
            self._log = log
            self.api_id = api_id
            self.api_secret = api_secret
            self.period = period
	    self._sensors = []

	    self._dataPath = dataPath 

            if not os.path.exists(self._dataPath) :
                self._log.info(u"Directory data not exist, trying create : %s" , self._dataPath)
                try :
                    os.mkdir(self._dataPath)
                    self._log.info(u"Withings data directory created : %s"  %self._dataPath)
                except Exception as e:
                    self._log.error(e.message)
                    raise withingException ("Withings data directory not exist : %s" % self._dataPath)
	    if not os.access(self._dataPath, os.W_OK) :
                self._log.error("User %s haven't write access on data directory : %s"  %(user,  self._dataPath))
    	        raise withingException ("User %s haven't write access on data directory : %s"  %(user,  self._dataPath))

            self.withing_config_file = os.path.join(os.path.dirname(__file__), '../data/withings.json')
	    self.auth = WithingsAuth(self.api_id, self.api_secret)
#	    self.open_token(self.auth)

            try:
    	        with open(self.withing_config_file, 'r') as withing_token_file:
                    self._log.debug(u"Opening File")
                    self.creds = pickle.load(withing_token_file)
                    self._log.debug(u"Getting user")
		    self.client = WithingsApi(self.creds)
		    self.user = self.client.get_user()
                    if self.user == None :
                        self.auth = WithingsAuth(self.api_key, self.api_secret)
		        self.authorize_url = self.auth.get_authorize_url()
		        print("Go to %s allow the app and copy your oauth_verifier" %self.authorize_url)
		        self.oauth_verifier = raw_input('Please enter your oauth_verifier: ')
		        self.creds = auth.get_credentials(self.oauth_verifier)
		        self.client = WithingsApi(creds)
		        self.user = self.client.get_user()
                        if user == None :
                            self._log.error(u"Error getting user, from code")
                            self._log.error(error)
                            sys.exit("refreshing token failed from refresh_token")
                            #TODO stop plugin
                        else :
                            self._log.warning(u"Token succesfully refresh with token_refresh from file")
                with open(self.withing_config_file, 'w') as withing_token_file:
                    pickle.dump(self.creds, withing_token_file)

            except ValueError:
                self._log.error(u"error reading Withing.")
                return
        except ValueError:
            self._log.error(u"error reading Withing.")


    def open_token(self, auth):
            try:
    	        with open(withing_config_file, 'r') as withing_token_file:
                    self._log.debug(u"Opening File")
                    self.creds = pickle.load(withing_token_file)
                    self._log.debug(u"Getting user")
		    self.client = WithingsApi(self.creds)
		    self.user = self.client.get_user()
                    if user == None :
                        self.auth = WithingsAuth(self.api_key, self.api_secret)
		        self.authorize_url = self.auth.get_authorize_url()
		        print("Go to %s allow the app and copy your oauth_verifier" %self.authorize_url)
		        self.oauth_verifier = raw_input('Please enter your oauth_verifier: ')
		        self.creds = auth.get_credentials(self.oauth_verifier)
		        self.client = WithingsApi(creds)
		        self.user = self.client.get_user()
                        if user == None :
                            self._log.error(u"Error getting user, from code")
                            self._log.error(error)
                            sys.exit("refreshing token failed from refresh_token")
                            #TODO stop plugin
                        else :
                            self._log.warning(u"Token succesfully refresh with token_refresh from file")
                with open(withing_config_file, 'w') as withing_token_file:
                    pickle.dump(self.creds, withing_token_file)

            except:
                self._log.error(u"Error with file saved or no file saved")
                self._log.error(u"Go to Advanced page to generate a new token file")
                #TODO stop plugin

    # -------------------------------------------------------------------------------------------------
    def add_sensor(self, device_id, device_name, device_type, user_id):
        """
        Add a sensor to sensors list.
        """
        self._sensors.append({'device_id': device_id, 'device_name': device_name, 'device_type': device_type,
                              'user_id': user_id})


    # -------------------------------------------------------------------------------------------------
    def readWithingApi(self, userid):
        """
        read the withing api for user information
        """
        try:
            user = self.client.get_user()
            self._log.debug(user)
            return user
        except AttributeError:
            self._log.error(u"### USERid '%s', ERROR while reading client value." % userid)
            return "failed"

    # -------------------------------------------------------------------------------------------------
    def readWithingMeasureApi(self, userid):
        """
        read the withing measure api information
        """
        try:
            measures = self.client.get_measures()
            return measures[0].data
        except AttributeError:
            self._log.error(u"### USERid '%s', ERROR while reading measure value." % userid)
            return "failed"


    # -------------------------------------------------------------------------------------------------
    def loop_read_sensor(self, send, send_sensor, stop):
        """
        """
        while not stop.isSet():
	    for sensor in self._sensors:
		self._log.debug(sensor)
                if sensor['device_type'] == "withing.user":
                    val = self.readWithingApi(sensor['user_id'])
		    self._log.debug(val)
                    if val != "failed":
			self._log.debug(val)
			self._log.debug(sensor)
                        send(sensor['device_id'], {'firstname': val['users'][0]['firstname'], 'lastname': val['users'][0]['lastname'], 'id': val['users'][0]['id']})
                elif sensor['device_type'] == "withing.measure":
                    val = self.readWithingMeasureApi(sensor['user_id'])
		    self._log.debug(val)
                    if val != "failed":
			timestamp = val['date']
			for measure in val['measures']:
                            sensor_name = u''
			    self._log.debug(measure)
                            if measure['type'] == 1:
                                sensor_name = "weight"
                            elif measure['type'] == 4:
                                sensor_name = "height"
                            elif measure['type'] == 5:
                                sensor_name = "fat_free_mass"
                            elif measure['type'] == 6:
                                sensor_name = "fat_ratio"
                            elif measure['type'] == 8:
                                sensor_name = "fat_free_mass"
                            elif measure['type'] == 9:
                                sensor_name = "diastolic_blood_pressure"
                            elif measure['type'] == 10:
                                sensor_name = "systolic_blood_pressure"
                            elif measure['type'] == 11:
                                sensor_name = "heart_pulse"
                            if sensor_name != u'':
                                #timestamp = calendar.timegm(sensors.date.timetuple())
				#timestamp=time.time()
				self._log.debug("Sending value to binary")
				value=float(measure['value'])/pow(10, abs(measure['unit']))
			        send_sensor(sensor['device_id'], sensor_name, value, timestamp)

                self._log.debug(u"=> '{0}' : wait for {1} seconds".format(sensor['device_name'], self.period))
    	    stop.wait(self.period)