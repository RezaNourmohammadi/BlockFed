from clients.learningModel import *
import os
import json
from utils.Data2IPFS import writeipfs, readFromIPFS
import numpy as np
from DataPreparation import clients_data_creation

class FLClients:
    def __init__(self, accountNumber, clientName, connection, configFile, localTrainData, testData) -> None:
        self.accountNum = accountNumber
        self.clientName = clientName
        self.learningModel = FLlearningModel(configFile["DEFAULT"]["Epochs"], 
                                             configFile["DEFAULT"]["InputDimension"], 
                                             configFile["DEFAULT"]["numClasses"], 
                                             configFile["DEFAULT"]["LearningRate"] )
        self.blockchainConnection = connection
        self.config = configFile
        self.precision = self.getPrecision()
        self.role = None ## 1 = trainer, 2 = level 1 aggregator, 3 = level 2 aggregator
        # self.localDataPoints = localDataPoints
        # self.localDataTargets = localDataTargets
        self.testData = testData
        # self.testTargets = None
        self.trainData = localTrainData
        self.testAccuracy = []
        
        
    
    def getroundNum(self):
        return self.blockchainConnection.get_RoundNumber(self.accountNum)
        
    # def connect(self):
    #     self.blockchainConnection.connect(self.config)
    
    def register(self):
        self.blockchainConnection.register(self.accountNum, self.clientName)
        
    def train(self):
        self.learningModel.train_model(self.trainData)
    
    def test(self, numRound):
        accuracy = []
        for(X_test, Y_test) in self.testData:
            acc, loss = self.learningModel.test_model(X_test, Y_test, numRound, self.clientName)
            accuracy.append(np.array(acc))
        return np.mean(accuracy), loss
        
    def loadGlobalWeights(self, roundNum):
        IPFS_Hash = self.blockchainConnection.loadGlobalModel(self.accountNum, roundNum, self.clientName)
        IPFSClientID = self.config["DEFAULT"]["IPFSclientID"]
        path = self.config["DEFAULT"]["IPFSDataPath"] + self.clientName + '/'
        modelData = readFromIPFS(IPFS_Hash[0], IPFSClientID, path)
        outputPath = path + '/' + IPFS_Hash[0]
        f = open(outputPath)
        model = json.load(f)
        globalWeights = []
        for key in model.keys():
            globalWeights.append(np.array(model[key]))
        return globalWeights
    
    def getWeights(self):
        return self.learningModel.get_weights()
    
    def setWeights(self, newWeights):
        # scaled_weights = []
        # for i in range(len(newWeights)):
        #     w = []   
        #     for weights in newWeights[i]:
        #         w.append(weights/self.precision)
        #     scaled_weights.append(w)
        # scaled_weights = self.learningModel.scale_model_weights_2(newWeights, self.precision)
            
        self.learningModel.set_weights(newWeights)
        

    
    def level_1_aggregation(self, read_index, roundNum):
        hashList = self.blockchainConnection.level_1_aggregator_read(self.accountNum, self.clientName, read_index, roundNum)
        IPFSClientID = self.config["DEFAULT"]["IPFSclientID"]
        counter = 0
        aggregatedWeights = []
        for IPFS_Hash in hashList:
            path = self.config["DEFAULT"]["IPFSDataPath"] + self.clientName + '/'
            modelData = readFromIPFS(IPFS_Hash, IPFSClientID, path)
            outputPath = path + '/' + IPFS_Hash
            f = open(outputPath)
            data = json.load(f)
            if counter == 0:
                keys = data.keys()
                weight_dict = dict()
                for key in keys:
                    # weight_dict[key] = []
                    weight_dict[key] = (np.array(data[key]))
                counter += 1
            else:
                for key in keys:
                    weight_dict[key] += (np.array(data[key]))
                counter += 1
                
        for key in weight_dict.keys():
            aggregatedWeights.append(weight_dict[key]/counter)
            
        return aggregatedWeights
    
    
    def level_2_aggregation(self, roundNum):
        hashList = self.blockchainConnection.level_2_aggregator_read(self.accountNum, self.clientName, roundNum)
        IPFSClientID = self.config["DEFAULT"]["IPFSclientID"]
        counter = 0
        aggregatedWeights = []
        for IPFS_Hash in hashList:
            path = self.config["DEFAULT"]["IPFSDataPath"] + self.clientName + '/'
            modelData = readFromIPFS(IPFS_Hash, IPFSClientID, path)
            outputPath = path + '/' + IPFS_Hash
            f = open(outputPath)
            data = json.load(f)
            if counter == 0:
                keys = data.keys()
                weight_dict = dict()
                for key in keys:
                    # weight_dict[key] = []
                    weight_dict[key] = (np.array(data[key]))
                counter += 1
            else:
                for key in keys:
                    weight_dict[key] += (np.array(data[key]))
                counter += 1
                
        for key in weight_dict.keys():
            aggregatedWeights.append(weight_dict[key]/counter)
            
        return aggregatedWeights
    
    def update(self, newWeights, roundNum):
        
        
        IPFSDatapath = self.config["DEFAULT"]["IPFSDataPath"] + self.clientName
        if os.path.exists(IPFSDatapath) == False:
            os.mkdir(IPFSDatapath)
            
        IPFSdata = IPFSDatapath + '/' + self.clientName + '.json'
        
        IPFSFileHash = "0x00000000000000000000000000000000"
        
        data_dictionary = dict()
        for i in range(len(newWeights)):
            key = f"weights_{i}"
            data_dictionary[key] = (newWeights[i]).tolist()
            
        json_object = json.dumps(data_dictionary, indent=4)
        with open(IPFSdata, "w") as outfile:
            outfile.write(json_object)

        IPFSFileHash = writeipfs(IPFSdata, self.config["DEFAULT"]["IPFSclientID"])
        if self.role == 1: 
            self.blockchainConnection.TrainerUpdate(IPFSFileHash[2:], self.accountNum, self.clientName, roundNum)
        elif self.role == 2: 
            self.blockchainConnection.level_1_aggregatorUpdate(IPFSFileHash[2:], self.accountNum, self.clientName, roundNum)
        elif self.role == 3: 
            self.blockchainConnection.level_2_aggregatorUpdate(IPFSFileHash[2:], self.accountNum, self.clientName, roundNum)
        
        return IPFSFileHash
    
    def getPrecision(self):
        return self.blockchainConnection.get_precision(self.accountNum)
    
    
        