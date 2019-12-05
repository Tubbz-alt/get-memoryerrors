"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__Version__    = "20191205.3"


import getpass
import sys
import os
import argparse

sys.path.append(os.getcwd()+'/bin')

from common      import timeFunctions
from common      import urlFunctions
from ucsmRoutine import ucsFunctions


defaultAdminName  = 'admin'
defaultServerName = 'Put your UCS Manager IP here'

green = '\033[32m'

#Argument Handling
helpmsg = '''
This tool connects to UCS and pulls memory information. 
All memory modules in a domain are listed (if visible to UCSM).
Memory statistics are only provided if errors are found.
'''

argsParse = argparse.ArgumentParser(description=helpmsg)
argsParse.add_argument('--server',   action='store',        dest='serverName', default=defaultServerName, required=False,  help='Cluster IP for UCS Manager')
argsParse.add_argument('--user',     action='store',        dest='adminName',  default=defaultAdminName,  required=False,  help='User name to access UCS Manager')
argsParse.add_argument('-d',        action='store',         dest='directory',  default='./reports',       required=False,  help='Directory reports are written into (optional)')
argsParse.add_argument('--verbose',  action='store_true',   dest='verbose',    default=False,             required=False,  help='Enables verbose messaging for debug purposes (optional)' )
args = argsParse.parse_args()

if (args.verbose):
    print('{0}Server:      {1}\033[0m'.format(green, args.serverName))
    print('{0}User:        {1}\033[0m'.format(green, args.adminName))
    print('{0}directory:   {1}\033[0m'.format(green, args.directory))
    print('{0}verbose:     {1}\033[0m'.format(green, args.verbose))

#Create objects for class handling
timeFunctions   = timeFunctions()
ucsF 	        = ucsFunctions(args) # We pass args to init to ensure we can identify verbose
URL             = urlFunctions()

fileTime = timeFunctions.getCurrentTime()
#File Name
path = '{0}/{1}-MemoryErrors.log'.format(args.directory, fileTime)
if (args.verbose):
    print("{0}File Path:   {1}\033[0m".format(green, path))

# URL used for access to UCS. UCS uses a single URL for everything until RedFish matures.
url = 'https://{0}/nuova'.format(args.serverName)
if (args.verbose):
    print("{0}URL:         {1}\033[0m".format(green,url))

# This line is used for authentication. We don't reprint it in verbose to protect the password. 
data = '<aaaLogin inName="{0}" inPassword="{1}" />'.format(args.adminName, getpass.getpass())

# Get a cookie. We use this for all further communcations with the server. 
authCookie =  URL.getCookie(url, data)
if (args.verbose):
    print("{0}Cookie:      {1}\033[0m".format(green, authCookie))

systemType = URL.getTopInfo(url, authCookie)
if systemType == 'stand-alone':
    print("Stand-Alone Support not yet implemented in this version")
    #We can only get inventory on stand alone servers.
elif systemType == 'cluster':
    #Get all rack units
    if (args.verbose):
        print('{0}System Type: Cluster\033[0m'.format(green))
    for Line in ucsF.getUnit(authCookie, url, "computeRackUnit"):
        print("\n\n{0}Unit:        {1}\033[0m".format(green, Line))
        ucsF.writeCompute(Line, path)
        ucsF.getMemory (authCookie, url, Line['dn'], path)
    #Get all blade servers
    for Line in ucsF.getUnit(authCookie, url, "computeBlade"):
        print("\n\n{0}Unit:        {1}\033[0m".format(green, Line))
        ucsF.writeCompute(Line, path)
        ucsF.getMemory (authCookie, url, Line['dn'], path)
#Clean up cookie when script exits normally.
if authCookie:
    print ("Invalidating authCookie")
    URL.getData(url, '<aaaLogout inCookie="{0}"></aaaLogout>'.format(authCookie))
