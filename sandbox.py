from lib.sbem_model.sbem_inp_model 	import SbemInpModel
from glob							import glob
from os.path 						import exists
BASE_DIR 	= "C:\\repos\\ML_arbnco\data\\inp_models\\"

features = []
with open("./configs/features.txt") as featuresFile:
	for line in featuresFile:
		features.append(line.strip())
with open("./data/temp.csv", "a") as dataFile:
	header = False
	for path in glob(BASE_DIR + "*"):
		id 		= path.split("\\")[-1] 
		mPath	= path + "\\" + id + ".inp"
		ePath	= path + "\\" + id + "_epc.inp"
		model	= SbemInpModel(open(mPath).read())
		output = {"BER": False, "SER": False}
		if not exists(ePath) or not exists(mPath):
			continue
		with open(ePath) as epcFile:
			for line in epcFile:
				if line.strip().startswith("BER"):
					output["BER"] = float(line.split("=")[1].strip())
				if line.strip().startswith("SER"):
					output["SER"] = float(line.split("=")[1].strip())
				if output["BER"] and output["SER"]:
					break
		
		fSet = model.extractFeatures(features)
		if not header:
			keys = list(fSet)
			keys.append("BER")
			keys.append("SER")
			header = True
			dataFile.write(",".join(keys) + "\n")
		writeFeatures = [str(feature.value) for key, feature in fSet.items()]
		writeFeatures.append(str(output["BER"]))
		writeFeatures.append(str(output["SER"]))
		
		dataFile.write(",".join(writeFeatures) + "\n")