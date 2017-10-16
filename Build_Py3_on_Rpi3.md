
# Build Python 3.6.3 on Raspberry Pi 3

```bash

# install gcc, make, etc.
sudo apt-get install build-essential


# install Python 3 dependencies
sudo apt-get install libreadline-dev libncurses-dev liblzma-dev libssl-dev libgnutls-openssl27 libdb-dev libgdbm-dev libbz2-dev libsqlite3-dev sqlite3


# Download source and unpack
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz 
tar xzf Python-3.6.3.tgz
cd Python-3.6.3


# Compile and install
./configure --prefix=${HOME}/opt --enable-optimizations
make -j 4
make install

# To ensure that you are always running this version,
# add this line to your .bash_profile
export PATH=${HOME}/opt/bin:${PATH}

```
