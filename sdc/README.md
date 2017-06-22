sdc.py - Save Device Config
===========================

The purpose of this script is to:
-	Periodically, save the config of all devices listed in the config.ini file
-	If the currently downloaded config file is a duplicate of the previously saved config file, then it is not saved again
-	When a change is made to a config, email a "diff" between the previous config and the current config

All of the options / settings are in the config.ini file.

The program has two modes: a server mode and a client mode. When the server starts, it generates a random UDP port number (that it listens on) and a random UUID.  

These are sent in an email as the first portion of an Authentication string.  The remaining portion is a password which is a secret that only you should know.

These 3 comma-delimited items make up the full Authentication string.

```
Example:
9676,3d894414-2f07-467b-9473-3a03c4bd2ac2,SECRET_PASSWORD_HERE
(There no spaces in between fields.)
```

To run the server:

```
cd \sdc\save_device_config
if not exist sdc.sqlite3 sqlite3 sdc.sqlite3 < schema.sql
python sdc.py -c config.ini
```

Once this is running, it will send an email with the first portion of the Authentication string and then listen on the chosen UDP port number.

To run the client:

```
cd \sdc\save_device_config
python sdc.py -c config.ini -a
```

This will ask for the Authentication string, which can be pasted in.  It will not be displayed on the screen.

If the Authentication string is correct, you should then see:

```
Response: OK
```

If the password is not correct, the server will return an error and then exit.

This entire process will have to be started again.

## Development

Developed on Jun-16-2017

- Windows 10, OS X 10.6
- Python 3.6.1
- netmiko 1.4.1 (3rd party Python module)

Supported device types, see CLASS_MAPPER_BASE:

https://raw.githubusercontent.com/ktbyers/netmiko/master/netmiko/ssh_dispatcher.py

**You must update the 'device_commands' dictionary for your device types**

More on the password encryption:

https://cryptography.io/en/latest/

To create an encrypted Fernet password for the INI file:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key() # save this key to your password database/keychain
f = Fernet(key)
password = f.encrypt(b"your_device_password_goes_here")
print(password)
```
