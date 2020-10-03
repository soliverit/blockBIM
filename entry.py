### Includes ###
##-Native
from sys 					import argv
#Command line runnererererer...
from os 					import system
##-Project
from lib.sbem_environment 	import SBEMEnvironment
##
# Arg preprocesses
##
if "fresh" in argv:
	system("cls")
### Get stuck in! ###
print("\t################################################")
print("\t# Saleh-ML (v0.9)                              #")
print("\t#                                              #")
print("\t#   Decentralised SBEM retrofit analysis based #")
print("\t#   on the PhD thesis of Saleh Seyedzadeh as   #")
print("\t#   described in:                              #")
print("\t#                                              #")
print("\t#   S. Seyedzadeh, F. Rahimian, S. Oliver,     #")
print("\t#   N Dawood, S. Rodriguez (2020). : Machine   #")
print("\t#   learning modelling for predicting          #") 
print("\t#   non-domestic buildings energy performance: #")
print("\t#   a model to supportdeep energy retrofit     #")
print("\t#   decision-making Applied Energy             #") 
print("\t################################################")
print("")
##
# Create a new 
##
environment = SBEMEnvironment.BuildEnvironment(withRegressor=True)
if "silent" in argv:
	environment.silent = True
environment.printSummary()

environment.run()

	
