#!/bin/sh

# Set up virtual can interface

modprobe vcan
ip link add dev vcan0 type vcan
ip link set up vcan0

