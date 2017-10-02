
# Build Python 3.6.2 on Raspberry Pi 3

```bash

# install gcc, make, etc.
sudo apt-get install build-essential

# install Python 3 Dependencies
sudo apt-get install libreadline-dev libncurses-dev liblzma-dev libssl-dev libdb-dev libgdbm-dev libbz2-dev libsqlite3-dev sqlite3


# Download and Unpack
wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz 
tar xzf Python-3.6.2.tgz
cd Python-3.6.2

# Compile and Install
./configure --prefix=${HOME}/opt --enable-optimizations
make -j 4
make install
```
