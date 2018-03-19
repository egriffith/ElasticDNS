# ElasticDNS

ElasticDNS is a simple python3 script which uses Boto3 and checkip.amazonaws.com to keep a configured Route53 Resource Record Set up to date with a given machine's current public IP. 

Please note that while I do provide an RPM file it does not handle dependencies on your behalf, it is only meant to make upgrades / installation / removal as simple as possible. There are 2 dependencies that this script has that need to be provided in some way by the user. The first dependency is the python3 version of the "requests" library (sometimes called python3-requests or python34-requests in your package manager). The second dependency is on the python3 version of boto3. These dependencies are not provided because this package is intended to work across CentOS 7, Amazon Linux and Fedora, and the naming of those packages (and their availability) varies across all three operating systems. 

Under CentOS, for example, the python3 version of boto3 is not packaged at all, meanwhile the python3 version of requests is called "python34-requests." Meanwhile under Amazon Linux, boto3 and python3-requests are available in the repositories. 

Assuming you have pip3 available, you should be able to install both dependencies with "pip3 install requests boto3" regardless of your OS, alternatively you can run "pip3 install -r requirements.txt"

If any user out there has an idea of how to keep logical dependencies for one package across all three OSs, please get in touch!

This application consists of the following files

/etc/elasticdns/elasticdns.conf
/etc/cron.d/elasticdns
/usr/bin/elasticdns
/usr/lib/systemd/system/elasticdns.service
/usr/lib/systemd/system/elasticdns.timer
/var/log/elasticdns/elasticdns.ip


If you install the script by hand file by file, the systemd files should instead be placed under

/etc/systemd/system/ 

rather than

/usr/lib/systemd/system/

Regardless, once the files in place, the configuration file (/etc/elasticdns/elasticdns.conf) needs to be configured. Please see the configuration file for a full break down of the various fields. Every field is mandatory except for "Profile=" and "Comment=". 

A cron file is provided in case your distribution of choice does not use systemd. Should that be the case, you will need to edit the cron file and uncomment the line in order for it to run.

If your distribution does use systemd, then you may enable the script to automatically execute by running the command

systemctl enable elasticdns.timer --now

as root. This will run the script and check your current IP every five minutes.

This script is meant to be run as a permanent user, by default this user is root. Regardless of the user that this script is running as, you must have valid aws credentials defined in the .aws/credentials or .aws/config file of that executing user's home directory. Should these credentials not be present,boto3 will also attempt to use environment variables or an IAM Instance Profile role for credentials. For a full breakdown of the order various credentials will be tried in, please see the boto3 documentation on credentials. 