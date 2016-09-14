# Parse Install on CentOS 7

2016-09-13 15:48

## Initial configuration

- edit: /etc/hostname /etc/hosts /etc/sysconfig/network
- adduser parseguy
- passwd parseguy
- ...
- usermod -aG wheel devops (so that the 'devops' user can use sudo)


## Install via Yum

- yum install screen
- yum install wget
- yum install net-tools
- yum install vim-enhanced
- yum install git
- yum install policycoreutils-python   (this is for semanage, which is needed for mongodb server configuration)
- yum groupinstall 'Development Tools' (optional)
- yum install telnet (optional)

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
```

- systemctl start nginx
- firewall-cmd --permanent --zone=public --add-service=http 
- firewall-cmd --permanent --zone=public --add-service=https
- firewall-cmd --reload
- systemctl enable nginx  (start nginix when system boots)

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
- ./setup_6.x   (this creates a file: /etc/yum.repos.d/nodesource-el.repo)
- yum install nodejs

## Install Parse Server and PM2 Globally

- npm install -g parse-server pm2 (this creates 11,244 files under /usr/lib/node_modules/ and also creates /usr/bin/pm2 and /usr/bin/parse-server)
- npm install -g mongodb-runner (I believe this may *somewhat* functionaly equivalent to pm2)

## Parse Server Basics

- See also: https://stackoverflow.com/questions/23948527/13-permission-denied-while-connecting-to-upstreamnginx
- parse-server --appId APPLICATION_ID --masterKey MASTER_KEY --databaseURI mongodb://localhost/test
- You can use any arbitrary string as your application id and master key. These will be used by your clients to authenticate with the Parse Server.

## Example Scripts

- start_parse_server.sh

```bash
#!/bin/bash

APPID="appid123456"
MASTERKEY="masterkey654321"
DBURI="mongodb://127.0.0.1:27017/testerdb?ssl=false"
parse-server --verbose --appId ${APPID} --masterKey ${MASTERKEY} --databaseURI ${DBURI}
```

- write_to_local_parse_server.sh

```bash
#!/bin/bash

APPID="appid123456"
curl -X POST -H "X-Parse-Application-Id: ${APPID}" -H "Content-Type: application/json" -d '{"age":43,"name":"John","location":"Athens"}' http://localhost:1337/parse/classes/testerdb
```

- read_from_local_parse.sh

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

## iOS Examples

```objc
// ViewController.m
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    [Parse initializeWithConfiguration:[ParseClientConfiguration configurationWithBlock:^(id<ParseMutableClientConfiguration> configuration) {
        configuration.applicationId = @"WhQ2pKSeyuKIoXY9mU96XXzJHmDOFN9YKnf8WYm5";
        configuration.clientKey = @"";
        configuration.server = @"http://172.22.2.27/parse/";
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
- example from remote host through nginx
- import parse.com data
- use pm2 so that the parse-server starts up when the server is rebooted
- iOS examples
