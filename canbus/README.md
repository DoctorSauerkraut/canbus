# canbus
What is this project ?

canbus is a can network simulator. The program is designed to test communications over a physical or virtual CAN interface. This simulates a various of sensors interconnected inside a vehicle. Basically, this tool only integrates classical CAN support (CAN 1.0 and CAN 2.0) and is based on python can library.

The program simulates a given number of sensors interconnected through a common bus

Setup
	# Initialize can virtual interface
	sudo ./canup.sh

Launch
	python main.py

Config
	open config.json

Attacks and security
	The project integrates a script (attacker.py) to simulate a DDos Attack on the network. Basically, the messages in the CAN are signed to prevent these attacks.
