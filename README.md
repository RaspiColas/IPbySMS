# IPbySMS
Small Python script for Raspberry to send its IP address by SMS (at boot time for example)

This is configurated for using the webhook provided by French telco Free to send the SMS. In this case, file ipbysms.conf should be modified to include your Free credentials for sending the SMS (see the option "Notification par SMS" in your option configuration page on mobile.free.fr)

You just need to modify line 93 in ipbysms.py if your webhook is different.

Don't forget to add "@reboot python ipbysms.py" to your crontab ("crontab -e" to edit your crontab)

Et voilà !

More on this here: https://raspicolas.wordpress.com/?p=233
