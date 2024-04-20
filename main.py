from utils.flutils import *
from DataPreparation import clients_data_creation
import numpy as np
from utils.utils import read_yaml
from clients.Clients import FLClients
from GeneDataPreparation import geneDataPreparation
from clients.blockchainConnection import FLBlockchainConnection
import json


config_file = read_yaml("/home/iman/projects/kara/Projects/blockFed_Mycode_v2/Config.yaml")

print("-------Initialization--------")

numClients = config_file["DEFAULT"]["NumberOfClients"]
numTrainers = config_file["DEFAULT"]["numTrainers"]
mainDataPath = config_file["DEFAULT"]["MainDataPath"]
totalRounds = config_file["DEFAULT"]["Rounds"]
clientsDataPoints,  global_testData = clients_data_creation(mainDataPath, numClients)
connection = FLBlockchainConnection(config_file)
connection.connect()

print("")
print("--------creating clients------------")
print("")

role_list = dict()
role_list["trainers"] = []
role_list["level_1_aggregators"] = []
role_list["level_2_aggregators"] = []


globalAcc = []
clientsNameList = []
clients = []
Trainers = []
level_1_aggregators = []
level_2_aggregators = []
for i in range(numClients):
    clientName = 'client_' + str(i)
    clientsNameList.append(clientName)
    clients.append(FLClients(i+1, clientName, connection, config_file, clientsDataPoints[i], global_testData))
    
    # if i < 4:
    #     role = 1
    #     Trainers.append(FLClients(i+1, clientName, connection, config_file, role))
    #     # clients.append(FLClients(i+1, clientName, connection, config_file, role, clientsDataPoints[i], clientsDataTarget[i]))
    #     clients.append(Trainers[-1])
    # if (i == 4) | (i == 5):
    #     role = 2
    #     level_1_aggregators.append(FLClients(i+1, clientName, connection, config_file, role))
    #     # clients.append(FLClients(i+1, clientName, connection, config_file, role, [], []))
    #     clients.append(level_1_aggregators[-1])
    # if (i == 6):
    #     role  = 3
    #     level_2_aggregators.append(FLClients(i+1, clientName, connection, config_file, role))
    #     # clients.append(FLClients(i+1, clientName, connection, config_file, role, [], []))
    #     clients.append(level_2_aggregators[-1])
    

    

        
    
print("")
print("--------registering clients------------")
print("")

for Client in clients:
    Client.register()
    print()


## role definition via smart contract
accuracy_scores = []
clients_index = []
for i in range(len(clients)):
    # clients[i].train()
    # acc, loss = clients[i].test(-1)
    acc = 100
    accuracy_scores.append(acc)
    clients_index.append(clients[i].clientName)
list1, list2 = zip(*sorted(zip(accuracy_scores, clients_index), reverse=True))

for client in clients: 
    if (list2.index(client.clientName) <= 3):
        client.role = 1
        Trainers.append(client)
    if (list2.index(client.clientName) == 4) | (list2.index(client.clientName) == 5):
        client.role = 2
        level_1_aggregators.append(client)
    if (list2.index(client.clientName) == 6):
        client.role = 3
        level_2_aggregators.append(client)
##
print("---------------Federated Learning------------")

roundNum = 0

while roundNum < totalRounds:
    
    trainers_list=[]
    
    level_1_aggregators_list = []
    
    level_2_aggregators_list = []
    
    for trainerClient in Trainers: 
        
        weights = trainerClient.getWeights()
        
        trainerClient.update(weights, roundNum)
        
        trainers_list.append(trainerClient.clientName)
        
      
            
            
        # if roundNum > 0:
            
        #     globalweights = trainerClient.loadGlobalWeights(roundNum)
        #     trainerClient.setWeights(globalweights)
        #     trainerClient.train()
        #     newWeights = trainerClient.getWeights()
        #     trainerClient.update(newWeights, roundNum)
        #     acc, loss = trainerClient.test(roundNum)
        #     trainerClient.testAccuracy.append(acc)
        #     print()
            
            ## weights = trainerClient.getWeights()
            ## trainerClient.update(weights, roundNum)
            
    read_index = 0
    for aggregator in level_1_aggregators:
        aggregatedWeights = aggregator.level_1_aggregation(read_index, roundNum)
        aggregator.update(aggregatedWeights, roundNum)
        level_1_aggregators_list.append(aggregator.clientName)
        read_index = read_index + 2
        
    for aggregator in level_2_aggregators:
        aggregatedWeights = aggregator.level_2_aggregation(roundNum)
        aggregator.update(aggregatedWeights, roundNum)
        level_2_aggregators_list.append(aggregator.clientName)
    
    role_list["trainers"].append(trainers_list)
    role_list["level_1_aggregators"].append(level_1_aggregators_list)
    role_list["level_2_aggregators"].append(level_2_aggregators_list)    
    
    roundNum = aggregator.getroundNum()  
            
        
    accuracy_scores = []
    clients_index = []
    Trainers = []
    level_1_aggregators = []
    level_2_aggregators = []
    
    # global model accuracy check flag
    check_flag = False
    for i in range(len(clients)):
        globalweights = clients[i].loadGlobalWeights(roundNum)
        clients[i].setWeights(globalweights)
        if (check_flag == False): ## storing the global model's accuracy
            global_model_acc, loss = clients[i].test(roundNum)
            globalAcc.append(global_model_acc)
            check_flag = True
        clients[i].train()
        acc, loss = clients[i].test(roundNum)
        accuracy_scores.append(acc)
        clients_index.append(clients[i].clientName)
        clients[i].testAccuracy.append(acc)
    list1, list2 = zip(*sorted(zip(accuracy_scores, clients_index), reverse=True))

    for client in clients: 
        if (list2.index(client.clientName) <= 3):
            client.role = 1
            Trainers.append(client)
        if (list2.index(client.clientName) == 4) | (list2.index(client.clientName) == 5):
            client.role = 2
            level_1_aggregators.append(client)
        if (list2.index(client.clientName) == 6):
            client.role = 3
            level_2_aggregators.append(client)
    
    print()
        
outputPath = config_file["DEFAULT"]["outputPath"] 
if os.path.exists(outputPath) == False:
    os.mkdir(outputPath)
            
outputFile = outputPath + 'result.json'   

result_dictionary = dict()
result_dictionary["global_acc"] = globalAcc
    
json_object = json.dumps(result_dictionary, indent=4)
with open(outputFile, "w") as outfile:
    outfile.write(json_object)    
       
       
for client in clients:
    outputFile = outputPath + client.clientName + '.json'
    client_result_dict = dict()
    client_result_dict["Accuracy"] = client.testAccuracy
    json_object = json.dumps(client_result_dict, indent=4)
    with open(outputFile, "w") as outfile:
        outfile.write(json_object)
        
outputFile = outputPath + 'role_list.json'
json_object = json.dumps(role_list, indent=4)
with open(outputFile, "w") as outfile:
    outfile.write(json_object)