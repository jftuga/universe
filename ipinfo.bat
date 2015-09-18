@echo off

rem ipinfo.bat
rem -John Taylor
rem Sep-18-2015

rem Use the ipinfo.io IP lookup API for IP geolocation
rem See also: http://ipinfo.io/
rem See also: https://news.ycombinator.com/item?id=10237247

set IP=%1

@echo.
curl.exe ipinfo.io/%IP%

rem $ curl ipinfo.io
rem   {
rem     "ip": "208.54.39.206",
rem     "hostname": "mce2736d0.tmodns.net",
rem     "city": "Los Angeles",
rem     "region": "California",
rem     "country": "US",
rem     "loc": "34.0522,-118.2437",
rem     "org": "AS21928 T-Mobile USA, Inc.",
rem     "postal": "90013",
rem     "phone": 213
rem   }
  
rem Or just your IP
rem   $ curl ipinfo.io/ip
rem   208.54.39.206
  
rem Or any other field (eg. city)
rem   $ curl ipinfo.io/city
rem   Los Angeles
  
rem Or lookup another IP
rem   $ curl ipinfo.io/8.8.8.8
rem {
rem     "ip": "8.8.8.8",
rem     "hostname": "google-public-dns-a.google.com",
rem     "city": "Mountain View",
rem     "region": "California",
rem     "country": "US",
rem     "loc": "37.3860,-122.0838",
rem     "org": "AS15169 Google Inc.",
rem     "postal": "94040",
rem     "phone": 650
rem }

rem Or a specific field for that IP:
rem   $ curl ipinfo.io/8.8.8.8/org
rem   AS15169 Google Inc.
