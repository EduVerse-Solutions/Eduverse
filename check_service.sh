#!/bin/bash
if systemctl is-active --quiet eduverse; then
	echo "Service is running"
else
	echo "Service is not running, restarting..."
	systemctl start eduverse
fi
