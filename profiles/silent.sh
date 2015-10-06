#!/bin/sh
DBUSSET="dbus-send --print-reply --dest='com.nokia.profiled' /com/nokia/profiled com.nokia.profiled.set_value string:silent string:\'%s\' string:\'%s\'"

dbus-send --type=method_call --dest=com.nokia.profiled /com/nokia/profiled com.nokia.profiled.set_profile string:"Silent"

gconftool-2 -s /system/tweakr/current-preset --type=string "tweakrprofile"
gconftool-2 -a /system/tweakr/tweakrprofile|sed 's/^ //'|sed 's/ = /=/'|awk -F'=' "{cmd=sprintf(\"${DBUSSET}\", \$1, \$2);system(cmd)}"

#dbus-send --type=method_call --dest=com.nokia.profiled /com/nokia/profiled com.nokia.profiled.set_profile string:"silent"
#dbus-send --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:"profile is set to silent"
