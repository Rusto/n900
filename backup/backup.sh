#!/bin/sh

name=`date +"%F_%H-%M"`
#path=/media/mmc1/MyBackup/`date +"%F_%H-%M"`
path=/media/mmc1/MyBackup
fullpath="$path"/"$name"

run-standalone.sh dbus-send --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:"making backup..."

mkdir -p "$fullpath"/etc
#mkdir -p "$fullpath"/home/user/.bookmarks
mkdir -p "$fullpath"/home/user/.calendar
mkdir    "$fullpath"/home/user/.config
mkdir    "$fullpath"/home/user/.osso-abook
#mkdir    "$fullpath"/home/user/.osso-abook-backup
mkdir    "$fullpath"/home/user/MyDocs
mkdir -p "$fullpath"/opt/fapman-cache
mkdir -p "$fullpath"/var/lib/hildon-application-manager

cp -r /etc/conky					    "$fullpath"/etc
cp -r /etc/mce						    "$fullpath"/etc
cp -r /etc/systemui					    "$fullpath"/etc
#cp    /home/user/.bookmarks/MyBookmarks.xml*                "$fullpath"/home/user/.bookmarks
cp    /home/user/.calendar/calendardb                       "$fullpath"/home/user/.calendar
cp -r /home/user/.config				    "$fullpath"/home/user
#cp -r /home/user/.osso-abook/db                             "$fullpath"/home/user/.osso-abook
cp -r /home/user/.osso-abook				    "$fullpath"/home/user
#cp -r /home/user/.osso-abook-backup/db                      "$fullpath"/home/user/.osso-abook-backup
cp -r /home/user/.rtcom-eventlogger                         "$fullpath"/home/user
cp    /home/user/mybackup.sh				    "$fullpath"
cp    /home/user/silent.sh				    "$fullpath"
cp -r /home/user/MyDocs/.documents                          "$fullpath"/home/user/MyDocs
cp -r /opt/fapman-cache					    "$fullpath"/opt
cp    /var/lib/hildon-application-manager/catalogues*       "$fullpath"/var/lib/hildon-application-manager
cp    /var/lib/hildon-application-manager/packages.backup   "$fullpath"/var/lib/hildon-application-manager

ls /usr/share/applications/hildon -al >> "$fullpath"/usr-share-app-hildon.txt

echo "osso-addressbook-backup -e "$fullpath"/osso-addressbook-backup" | su - user

run-standalone.sh dbus-send --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:"arhiving..."

tar -jcvf "$path"/"$name".tar.bz2 "$fullpath"

run-standalone.sh dbus-send --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:"backup created"
