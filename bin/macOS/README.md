## macOS Binaries

- pip3 install -U 'http://nuitka.net/gitweb/?p=Nuitka.git;a=snapshot;h=refs/heads/develop;sf=tgz'
- nuitka --standalone --python-flag=no_site pgm.py
- cd pgm.dist
- mv pgm.exe pgm
- strip pgm
- brew install upx
- upx -9 pgm
