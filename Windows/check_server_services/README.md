# Check Windows services

There are many programs to monitor services.  One problem is determining
which services need to be monitored and which don't.  I approach this
problem by finding the unique services across a group of servers.

For example, all of your servers will be running services such as
Netlogon, RPC, Security Accounts Manager, etc.  These don't need to be
explicitly monitored.  Other services such as SQL, IIS or Exchange need
to be monitored.

I wrote two PowerShell scripts.  The first one looks at all of your
servers.  If a service appears on more than X number of servers, then it
is not unique.  Otherwise it is unique.  Unique services are written to
a tab-delimited file which includes Server Name, Service Name, Short Name
(a short description).

This script does have room for improvement.  It could also include a
mandatory list of services to always check for. SQL would be a good
candidate for this as it is important, but not necessarily installed on
fewer than X number of servers.

The second script is run from the Task Scheduler each morning.  It runs
through a list of servers & services (via the TSV file) and will send
an email alerting you to any services that are not running.  It will
also send an email to report that all services are OK.  For services
that are not running, it will attempt to restart them.  Included in the
script is the ability to ping servers, which is useful for servers in
a DMZ where services can't be queried via a PowerShell script.


