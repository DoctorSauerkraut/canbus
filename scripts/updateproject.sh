#!/bin/sh

scp -r -i /home/olive/.keys/id_rsa_ssh *.py pi@192.168.2.11:~/canbus/
scp -r -i /home/olive/.keys/id_rsa_ssh *.py pi@192.168.2.12:~/canbus/
scp -r -i /home/olive/.keys/id_rsa_ssh *.py pi@192.168.2.13:~/canbus/
scp -r -i /home/olive/.keys/id_rsa_ssh *.py pi@192.168.2.14:~/canbus/
scp -r -i /home/olive/.keys/id_rsa_ssh *.py pi@192.168.2.15:~/canbus/
