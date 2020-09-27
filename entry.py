### Includes ###
##-Native
from sys 				import argv
#Command line runnererererer...
from os 				import system
##-Project
from lib.environment 	import Environment
##
# Arg preprocesses
##
if "fresh" in argv:
	system("cls")
### Get stuck in! ###
##
# Create a new 
##
environment = Environment.BuildEnvironment()
environment.printSummary()

if "debug" not in argv:
	environment.cleanup()

	
