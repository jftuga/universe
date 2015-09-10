
I needed to copy about 80 GB (two VMs) to my test ESXi server, which
runs under VMWare Workstation 8. Unfortunately, this was going to
take a long time using the "Browse Datastores" -> "Upload file"
method. I noticed that my VMNet1 adapter was only running at 100
Mbps but wasn't sure if this was the problem or not. This method
was out -- too slow.

Veeam FastSCP failed with a "Retrieving the COM class factory for
component". After googling this error message, it looks like this
was due to trying to run it, a 32-bit app, on a 64-bit version of
Windows 7.  

Next I tried pscp.exe, but it could only muster 5 MB/s -- still way
to slow.

My VMs just happened to also be compressed with WinRar (to transport
from work to home on a USB stick), so I downloaded the command-line
RAR Linux binary, but this is not compatible with ESXi. However,
the [p7zip for Posix/Linux](http://www.7-zip.org/) was compatible
and it can also uncompress RAR files. I like using RAR because of
the -rr option, which appends a recovery record onto the end of the
archive. I feel this is good piece of mind when using a USB stick.

My final solution was to transfer the highly compressed RAR files
via pscp and then uncompress with the 7zip 9.20.1 Linux binary.
86.3 GB compressed down to 6 GB. It took about 20 minutes to transfer
the RAR files and another 40 minutes to uncompress. The system I
am using is a Core 2 Duo 3.33 GHz.

This sure does beat the 4 plus hours the original method was going
to take! :-) I still think this time could be improved and will
post if I find a faster method.

Jan 2012

