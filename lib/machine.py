from sklearn.ensemble		import GradientBoostingRegressor
from time					import sleep
from threading				import Thread
from sys					import stdout
class Machine():
	def __init__(self, trainData, testData, target,parameters={}):
		self.target			= target
		self.trainingData	= trainData
		self.testData		= testData
		self.parameters		= parameters
		##
		# Do targets		
		##
		self.trainingTargets= self.trainingData[self.target]
		self.testTargets	= self.testData[self.target]
		#Drop targets
		self.trainingData	= self.trainingData.drop([self.target], axis=1)
		self.testData		= self.testData.drop([self.target], axis=1)
		##
		# Declare placeholders
		##
		self.model			= False
	##
	# Train the model
	##
	def train(self):
		self.printSummary()
		##
		# Do model
		##
		self.model = GradientBoostingRegressor()
		for k, v in self.parameters.items():
			setattr(self.model, k, v)
			
		self.model.fit(self.trainingData, self.trainingTargets)
		##
		# That'a wrap!
		##
		print("\n\t########################")
	##
	# Do a prediction
	##
	def predict(self,inputs):
		return self.model.predict([[feature.value for key, feature in inputs.items()]])[0]
	##
	# Print summary
	##
	def printSummary(self):
		print("\n\t### Gradient Boosting Regressor ###")
		print("\tTarget:\t\t%s\n\tTrain size:\t%s\n\tTest size:\t%s" %(self.target,len(self.trainingData), len(self.testData)))
		print("\tParams:")
		for key, value in self.parameters.items():
			print("\t\t%s:%s" %(key, value))
		
		
		