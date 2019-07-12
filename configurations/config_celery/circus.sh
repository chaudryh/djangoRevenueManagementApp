sudo su apache
source /home/apache/.pyenv/versions/bbu/bin/activate
cd /home/apache/bbu/config/circus
circusd --daemon circus.ini
