from web3 import Web3
import json 

class FLBlockchainConnection:
    
    def __init__(self, config) -> None:
        self.config = config
        self.FLcontractAddress = config["DEFAULT"]["FLContractAddress"]
        self.FLcontractABI = None
        self.FLcontractDeployed = None
    
    def is_connected(self):
        return self.web3Connection.isConnected()

    def get_precision(self, accountNR):
        return self.FLcontractDeployed.functions.Precision().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})
    
    def connect(self):
        self.web3Connection=Web3(Web3.HTTPProvider(self.config["DEFAULT"]["EtheriumRPCServer"],request_kwargs={'timeout': 60*10}))
        with open(self.config["DEFAULT"]["FLContractABIPAth"]) as f:
            ##self.FLcontractABI=json.load(f)["abi"]
            self.FLcontractABI = json.load(f)
        self.FLcontractDeployed = self.web3Connection.eth.contract(address=self.FLcontractAddress,abi=self.FLcontractABI)
    
    def __await_Trainsaction(self,thxHash):
        self.web3Connection.eth.wait_for_transaction_receipt(thxHash)
    
    
    
    def register(self,accountNR, device_name):
        if (self.is_connected() == False):
            print(device_name + " is not connected")
        if self.is_connected():
             try:
                 thxHash= self.FLcontractDeployed.functions.register().transact({"from": self.web3Connection.eth.accounts[accountNR]})
                 self.__await_Trainsaction(thxHash)
                 
                 print(" ")
                 print("registration of " + device_name + " successfully done")
                 print(" ")
             except:
                 
                 print(" ")
                 print("registeration of " + device_name + " failed")
                 print(" ")
                
    
    def get_RoundNumber(self, accountNR ):
        return self.FLcontractDeployed.functions.currentRoundNum().call(
            {"from": self.web3Connection.eth.accounts[accountNR]})
        
    def level_1_aggregator_read(self, accountNumber, clientName, read_index, roundNum):
        hashList = []
        try:
            UploadedModelsHash= self.FLcontractDeployed.functions.level_1_aggregator_read(read_index).call(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            
            for h in UploadedModelsHash:
                hashList.append('Qm'+h)
            
            
            print(" ")
            print(f"Round: {roundNum}, level 1 aggregator:  {clientName}: reading successfull")
            print(" ")
            
        except:
            
            print(" ")
            print(f"Round: {roundNum}, level 1 aggregator:  {clientName}: reading Failed")
            print(" ")
       
        return hashList
        
    
    def level_2_aggregator_read(self, accountNumber, clientName, roundNum):
        hashList = []
        try:
            UploadedModelsHash= self.FLcontractDeployed.functions.level_2_aggregator_read().call(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            
            for h in UploadedModelsHash:
                hashList.append('Qm'+h)
            
            
            print(" ")
            print(f"Round: {roundNum}, level 2 aggregator:  {clientName}: reading successfull")
            print(" ")
            
        except:
            
            print(" ")
            print(f"Round: {roundNum}, level 2 aggregator:  {clientName}: reading Failed")
            print(" ")
        
        return hashList
    
    def TrainerUpdate(self, ipfsHash, accountNumber, clientName, roundNum):
        try:
            thxHash = self.FLcontractDeployed.functions.trainersUpdate(ipfsHash).transact(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            self.__await_Trainsaction(thxHash)
            
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE SUCCESSFUL")
            print(" ")
        
        except:
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE Failed")
            print(" ")
    
    def level_1_aggregatorUpdate(self, ipfsHash, accountNumber, clientName, roundNum):
        try:
            thxHash = self.FLcontractDeployed.functions.level_1_AggregationUpdate(ipfsHash).transact(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            self.__await_Trainsaction(thxHash)
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE SUCCESSFUL")
            print(" ")
        
        except:
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE Failed")
            print(" ")
    
    
    
    def level_2_aggregatorUpdate(self, ipfsHash, accountNumber, clientName, roundNum):
        try:
            thxHash = self.FLcontractDeployed.functions.level_2_AggregationUpdate(ipfsHash).transact(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            self.__await_Trainsaction(thxHash)
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE SUCCESSFUL")
            print(" ")
        
        except:
            print(" ")
            print(f"Round: {roundNum}, {clientName}: UPDATE Failed")
            print(" ")        
    
    def loadGlobalModel(self, accountNumber, roundNum, clientName): 
        try:
            globalModel_IPFShash= self.FLcontractDeployed.functions.trainers_read().call(
                {"from": self.web3Connection.eth.accounts[accountNumber]})
            
            globalModel_IPFShash[0] = 'Qm' + globalModel_IPFShash[0]
            
            print(" ")
            print(f"Round: {roundNum}, {clientName}: Downloaded the global model successfully")
            print(" ")
        
        except:
            print(" ")
            print(f"Round: {roundNum}, {clientName}: failed to download the global model")
            print(" ")  
        
        return globalModel_IPFShash