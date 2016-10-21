# Parse Install on CentOS 7

2016-10-21

## Initial configuration

- base system insatlled with: CentOS-7-x86_64-Minimal-1511.iso (sha1: 783eef50e1fb91c78901d0421d8114a29b998478)
- To perform a full system update, run this as root: yum update  (may need to reboot afterwards)
- edit: /etc/hostname /etc/hosts /etc/sysconfig/network
- adduser parseguy
- passwd parseguy
- usermod -aG wheel devops (so that the 'devops' user can use sudo)


## Install via Yum

- to what packages are currently installed: yum list installed *or* yum list installed | grep whatever
- yum install screen
- yum install wget
- yum install net-tools
- yum install vim-enhanced
- yum install git
- yum install policycoreutils-python   (this is for semanage, which is needed for mongodb server configuration)
- yum install telnet (optional, to verify open ports and send raw commands)

## Install via EPEL

- enables you to install packages not in the base CentOS distribution
- https://fedoraproject.org/wiki/EPEL
- yum install epel-release
- yum install smem    (to see system memory usage, you can then run smem -tw)

## Install Nginix

- https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-centos-7
- yum install nginx
- edit: /etc/nginx/nginx.conf
- within the server{} stanza add the following:

```
location /parse/ {
    proxy_pass http://127.0.0.1:1337;
}

# for the parse dashboard...
location /dashboard-for-parse/ {
	proxy_pass http://127.0.0.1:4040;
}
```

- systemctl start nginx
- firewall-cmd --permanent --zone=public --add-service=http 
- firewall-cmd --permanent --zone=public --add-service=https
- firewall-cmd --zone=public --add-port=4040/tcp **don't do this in production, this is only to directly access the dashboard; also append --allowInsecureHTTP=1 to the 'parse-dashboard' command below**
- semanage port -a -t http_port_t -p tcp 4040 **don't do this in production**
- firewall-cmd --reload
- firewall-cmd --zone=public --list-all # (to view all open ports)
- iptables -S (to view all firewall rules)
- systemctl enable nginx  (start nginix when system boots)

- To allow nginx to connect to the proxy_pass services: http://stackoverflow.com/a/31403848/452281
- setsebool httpd_can_network_connect on
- setsebool httpd_can_network_connect on -P (persist across reboots)
- getsebool -a | grep httpd | grep on$ # (to verify these changes)


## Install MongoDB

- https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/
- Create a /etc/yum.repos.d/mongodb-org-3.2.repo file so that you can install MongoDB directly, using yum
- Inside this file, create the [mongodb-org-3.2] section
- yum install mongodb-org
- semanage port -a -t mongod_port_t -p tcp 27017
- service mongod start
- systemctl enable mongod (ensure that MongoDB will start following a system reboot)
- database files stored in: /var/lib/mongodb
- log files stored in: /var/log/mongodb

## Install Node.js

- https://github.com/nodesource/distributions#rpm
- wget https://rpm.nodesource.com/setup_6.x && chmod 700 setup_6.x
- verify the contents of this file and then run:
- ./setup_6.x   # (this creates a file: /etc/yum.repos.d/nodesource-el.repo)
- yum install nodejs

## Global Install of Parse Server, Parse Dashboard

- npm install -g parse-server # (this creates many files under /usr/lib/node_modules/ and also creates /usr/bin/parse-server)

## Parse Server Basics

- See also: https://stackoverflow.com/questions/23948527/13-permission-denied-while-connecting-to-upstreamnginx
- parse-server --appId APPLICATION_ID --masterKey MASTER_KEY --databaseURI mongodb://localhost/test
- You can use any arbitrary string as your application id and master key. These will be used by your clients to authenticate with the Parse Server.

## Example Scripts

- Create start_parse_server.sh

```bash
#!/bin/bash

APPID="appid123456"
MASTERKEY="masterkey654321"
DBURI="mongodb://127.0.0.1:27017/testerdb?ssl=false"

while [ 1 ] ; do
        parse-server --verbose --appId ${APPID} --masterKey ${MASTERKEY} --databaseURI ${DBURI}
        echo "will restart parse-server in 7 seconds..."
        sleep 7
done
```

- Create write_to_local_parse_server.sh

```bash
#!/bin/bash

APPID="appid123456"
curl -X POST -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" -d '{"age":43,"name":"John","location":"Athens"}' http://localhost:1337/parse/classes/testerdb
```

- Create read_from_local_parse.sh

```bash
#!/bin/bash

APPID="appid123456"
curl -X GET -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" http://localhost:1337/parse/classes/testerdb
```

- as the parseguy user:

```
[parseguy@staging1 ~]$ ./start_parse_server.sh
appId: appid123456
masterKey: ***REDACTED***
port: 1337
databaseURI: mongodb://127.0.0.1:27017/testerdb?ssl=false
mountPath: /parse
maxUploadSize: 20mb
verbose: true
serverURL: http://localhost:1337/parse

[3262] parse-server running on http://localhost:1337/parse

```

```
[parseguy@staging1 ~]$ ./write_to_local_parse_server.sh
{"objectId":"zMeGUR5NMr","createdAt":"2016-09-14T00:29:45.249Z"}
[parseguy@staging1 ~]$ ./read_from_local_parse_server.sh
{"results":[{"objectId":"zMeGUR5NMr","age":43,"name":"John","location":"Athens","createdAt":"2016-09-14T00:29:45.249Z","updatedAt":"2016-09-14T00:29:45.249Z"}]}
```

- verify you can access the parse server from a remote host,
- Create read_from_remote_parse.sh

```bash
#!/bin/bash

SERVER=192.168.1.27
APPID=appid123456
curl -X GET -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" http://${SERVER}/parse/classes/testerdb
```

- The above command should return something like:

```json
{"results":[{"objectId":"zMeGUR5NMr","age":43,"name":"John","location":"Athens","createdAt":"2016-09-14T00:29:45.249Z","updatedAt":"2016-09-14T00:29:45.249Z"}]}
```

- verify you can remotely submit new data to the server, 
- Create readwrite_remote_parse.sh

```bash
#!/bin/bash

SERVER=192.168.1.27
APPID=appid123456

echo; echo "initial read..."
curl -X GET -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" http://${SERVER}/parse/classes/testerdb
echo; echo "submit new entry..."
curl -X POST -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" -d '{"age":19,"name":"Bobby","location":"Boise"}' http://${SERVER}/parse/classes/testerdb
echo; echo "verify write..."
curl -X GET -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" http://${SERVER}/parse/classes/testerdb
```


## Parse Dashboard

- https://github.com/ParsePlatform/parse-dashboard
- npm install -g parse-dashboard
- Create: /home/parseguy/parse-dboard-cfg.json,  Note: the *serverURL* will be used by the browser and therefore should use an IP address that is externally accessible

```json
{
  "apps": [{
    "serverURL": "http://192.168.1.27/parse",
    "appId": "appid123456",
    "masterKey": "masterkey654321",
    "appName": "TesterDB",
    "iconName": ""
  }],
  "iconsFolder": "icons",
  "users": [
    {
       "user":"tom",
       "pass":"change me (see below)"
    },
    {
       "user":"jerry",
       "pass":"change me (see below)"
    }
  ],
  "useEncryptedPasswords": true
}
```

- to use encrypted passwords in the parse-dboard-cfg.json file:
- yum install python-pip
- yum install python-devel
- yum install libffi-devel
- yum groupinstall 'Development Tools' # needed to build bcrypt module
- pip install bcrypt
- generate passwords with this Python script and insert into the JSON file above
- Create gen_bcrypt_hash.py:

```python
#!/usr/bin/env python2.7

import getpass
import bcrypt

a = getpass.getpass(" Enter password: ")
b = getpass.getpass("Verify password: ")

if a != b:
        print("Passwords do no match!")
else:
        rounds = 15
        print( bcrypt.hashpw(a, bcrypt.gensalt(rounds)) )
```

- Create start_dashboard.sh:

```bash
#!/bin/bash

export DASH=/home/parseguy/parse-dboard-cfg.json
export DEBUG="express:*" # (optional)

# (--allowInsecureHTTP=1 is only for initial install and testing)
# NOTE: mountPath needs to be the same as nginx.conf location 
while [ 1 ] ; do
        while [ 1 ] ; do
                echo "`date`: waiting for parse server to start..."
                PARSE=`netstat -a -n | egrep -c ":1337.*LISTEN"`
                if [ "${PARSE}" == "1" ] ; then
                        break
                fi
                sleep 2
        done

        echo "`date`: starting dashboard..."
        sleep 2


        parse-dashboard --config ${DASH} --port 4040 --mountPath /ag-parse-dashboard
        echo "will restart parse-dashboard in 10 seconds..."
        sleep 10
done
```

- As the parseguy user, run ./start_parse_server.sh
- Then run ./start_dashboard.sh


## Run Parse and the Dashboard at system boot

- Create /home/parseguy/screen_boot.rc

```bash
startup_message off
defscrollback 10000

screen -t ParseServer /home/parseguy/start_parse_server.sh
screen -t ParseDashboard /home/parseguy/start_dashboard.sh
screen -t ParseBash /bin/bash
```

- run crontab -e and add the following line:
- @reboot /bin/screen -d -m -c /home/parseguy/screen_boot.rc


## Install SSL Certificate for Nginix

- yum install certbot
- certbot certonly
- follow https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04
- (making adjustments for CentOS instead of Ubuntu)
- For the root crontab file, use: 
- 45 2 * * * /bin/certbot renew --quiet
- 50 2 * * * /sbin/service nginx restart



## Install SSL Certificate for MongoDB

- Adapted from this guide, "MongoDB 3.2.x SSL with Letsencrypt": https://gist.github.com/leommoore/1e773a7d230ca4bbe1c2
- Do not install the LetsEncrypt software with this method
- Instead, start at the "download IdenTrust DST" section
- install_mongo_ssl.sh
```bash
#!/bin/bash

# adapted from: https://gist.github.com/leommoore/1e773a7d230ca4bbe1c2

SOURCE=/etc/letsencrypt/live/parse.example.com
DEST=/etc/ssl/mongodb

if [ ! -e ${DEST} ] ; then
    mkdir -m 700 ${DEST}
    chown mongod:mongod ${DEST}
else
    rm -f ${DEST}/ca.* ${DEST}/mongodb.pem
fi

cat ${SOURCE}/privkey.pem ${SOURCE}/fullchain.pem > ${DEST}/mongodb.pem

if [ ! -e ${DEST}/ca.crt ] ; then
    # from: https://www.identrust.com/certificates/trustid/root-download-x3.html
    echo "-----BEGIN CERTIFICATE-----" > ${DEST}/ca.crt
    echo "MIIDSjCCAjKgAwIBAgIQRK+wgNajJ7qJMDmGLvhAazANBgkqhkiG9w0BAQUFADA/" >> ${DEST}/ca.crt
    echo "MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT" >> ${DEST}/ca.crt
    echo "DkRTVCBSb290IENBIFgzMB4XDTAwMDkzMDIxMTIxOVoXDTIxMDkzMDE0MDExNVow" >> ${DEST}/ca.crt
    echo "PzEkMCIGA1UEChMbRGlnaXRhbCBTaWduYXR1cmUgVHJ1c3QgQ28uMRcwFQYDVQQD" >> ${DEST}/ca.crt
    echo "Ew5EU1QgUm9vdCBDQSBYMzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB" >> ${DEST}/ca.crt
    echo "AN+v6ZdQCINXtMxiZfaQguzH0yxrMMpb7NnDfcdAwRgUi+DoM3ZJKuM/IUmTrE4O" >> ${DEST}/ca.crt
    echo "rz5Iy2Xu/NMhD2XSKtkyj4zl93ewEnu1lcCJo6m67XMuegwGMoOifooUMM0RoOEq" >> ${DEST}/ca.crt
    echo "OLl5CjH9UL2AZd+3UWODyOKIYepLYYHsUmu5ouJLGiifSKOeDNoJjj4XLh7dIN9b" >> ${DEST}/ca.crt
    echo "xiqKqy69cK3FCxolkHRyxXtqqzTWMIn/5WgTe1QLyNau7Fqckh49ZLOMxt+/yUFw" >> ${DEST}/ca.crt
    echo "7BZy1SbsOFU5Q9D8/RhcQPGX69Wam40dutolucbY38EVAjqr2m7xPi71XAicPNaD" >> ${DEST}/ca.crt
    echo "aeQQmxkqtilX4+U9m5/wAl0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNV" >> ${DEST}/ca.crt
    echo "HQ8BAf8EBAMCAQYwHQYDVR0OBBYEFMSnsaR7LHH62+FLkHX/xBVghYkQMA0GCSqG" >> ${DEST}/ca.crt
    echo "SIb3DQEBBQUAA4IBAQCjGiybFwBcqR7uKGY3Or+Dxz9LwwmglSBd49lZRNI+DT69" >> ${DEST}/ca.crt
    echo "ikugdB/OEIKcdBodfpga3csTS7MgROSR6cz8faXbauX+5v3gTt23ADq1cEmv8uXr" >> ${DEST}/ca.crt
    echo "AvHRAosZy5Q6XkjEGB5YGV8eAlrwDPGxrancWYaLbumR9YbK+rlmM6pZW87ipxZz" >> ${DEST}/ca.crt
    echo "R8srzJmwN0jP41ZL9c8PDHIyh8bwRLtTcm1D9SZImlJnt1ir/md2cXjbDaJWFBM5" >> ${DEST}/ca.crt
    echo "JDGFoqgCWjBH4d1QB7wCCZAA62RjYJsWvIjJEubSfZGL+T0yjWW06XyxV3bqxbYo" >> ${DEST}/ca.crt
    echo "Ob8VZRzI9neWagqNdwvYkQsEjgfbKbYK7p2CNTUQ" >> ${DEST}/ca.crt
    echo "-----END CERTIFICATE-----" >> ${DEST}/ca.crt

    cat ${SOURCE}/chain.pem >> ${DEST}/ca.crt
fi

openssl x509 -in ${DEST}/ca.crt -out ${DEST}/ca.pem -outform PEM
openssl verify -verbose -CAfile ${DEST}/ca.crt ${DEST}/mongodb.pem

chown mongod:mongod ${DEST}/ca.* ${DEST}/mongodb.pem
chmod 600 ${DEST}/ca.* ${DEST}/mongodb.pem

echo
ls -la ${DEST}
```

- service mongod restart
- On a remote server, copy ca.pem and mongodb.pem to ${HOME}/mongodb
- From that system, connect with:
- mongo --ssl -sslCAFile ${HOME}/mongodb/ca.pem --sslPEMKeyFile ${HOME}/mongodb/mongodb.pem parse.example.com:27017/testerdb


## Export your data from parse.com

- https://www.parse.com/login
- Use the "new" parse dashboard
- click on your app (on the right side)
- click on app settings -> general (on the left side)
- export data (an email will be sent to you with a download link)
- or you can also use "Clone this app", but this will not clone any data, just the schema
- Example mongodb://parse.example.com:27017/testerdb?ssl=true


## iOS Examples

```objc
/*
Podfile:

target 'parse-objc' do
    pod 'Parse'
end
*/

// ViewController.m

#import "ViewController.h"
#import "Parse.h"

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    [Parse initializeWithConfiguration:[ParseClientConfiguration configurationWithBlock:^(id<ParseMutableClientConfiguration> configuration) {
        configuration.applicationId = @"appid123456";
        configuration.clientKey = @"";
        configuration.server = @"http://192.168.1.27/parse/";
    }]];
    
    PFQuery *query = [PFQuery queryWithClassName:@"testerdb"];
    // to return a sungle entity...
    //[query whereKey:@"name" equalTo:@"John"];
    [query findObjectsInBackgroundWithBlock:^(NSArray *objects, NSError *error) {
        if (!error) {
            // The find succeeded.
            NSLog(@"Successfully retrieved %ld contacts.", objects.count);
            NSLog(@"========================================================");
            // Do something with the found objects
            for (PFObject *object in objects) {
                NSLog(@"object: %@", object.objectId);
                NSLog(@"web   : %@", object[@"contactWeb"]);
                NSLog(@"phone : %@", object[@"contactPhone"]);
                NSLog(@"---------------------------");
            }
        } else {
            // Log details of the failure
            NSLog(@"Error: %@ %@", error, [error userInfo]);
        }
    }];
    
}

```



## Todo

- https encryption
- import parse.com data
