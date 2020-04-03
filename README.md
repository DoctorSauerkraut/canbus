# canbus
What is this project ?

canbus is a can network simulator. The program is designed to test communications over a physical or virtual CAN interface. This simulates a set of sensors interconnected inside a vehicle (or any can bus network). Basically, this tool only integrates classical CAN support (CAN 1.0 and CAN 2.0) and is based on python can library.

The program simulates a given number of sensors interconnected through a common bus. The number of nodes can be set manually.

**Setup**
	# Initialize can virtual interface
	sudo ./canup.sh

**Launch**
	python main.py (requires python 3)

**Config**
	open config.json

**Attacks and security**
	The project integrates a script (attacker.py) to simulate a DDos Attack on the network. Basically, the messages in the CAN are signed to prevent these attacks.


**Config.json file**
The config file is attached to each network interface of your network. In other words : one instance of the simulator =  one config file. Here are the details of the parameters
id : Start of the id range (or id of the current node if there is only one)

sign : Activate/Deactivate the signature of messages


nbNodes : number of nodes emulated 

totalNodes : Number total of nodes in the physical network (used for node id random computation)s

verbose : debug mode


delay : Delay of simulation (in seconds)

channel : Network interface name

Reception : Activate reception module 

Transmission : Activate transmission module