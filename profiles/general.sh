#!/bin/sh
dbus-send --type=method_call --dest=com.nokia.profiled /com/nokia/profiled com.nokia.profiled.set_profile string:"general"
dbus-send --type=method_call --dest=org.freedesktop.Notifications /org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:"profile is set to general"
