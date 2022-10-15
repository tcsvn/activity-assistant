#!/usr/bin/with-contenv bashio

# Generate new host keys for container
ssh-keygen -A

# TODO what does this thing odo
yes '' | ssh-keygen -N '' > /dev/null

echo "Starting sshd service"
/usr/sbin/sshd -D -p 433 -e "$@"

echo "finishing..."