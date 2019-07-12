
#!/usr/bin/env bash

echo -e "++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e "+++     Connecting to prod app server...     +++"
echo -e "++++++++++++++++++++++++++++++++++++++++++++++++"

sshpass -p cWfP6h ssh -i ./atu.id_rsa atu@dmz-ratewf01.na.amfbowl.net
