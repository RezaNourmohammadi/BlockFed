// SPDX-License-Identifier: MIT

pragma solidity ^0.8.16;

contract FL{

    uint256 public inputDimension = 0;
    uint256 public outputDimension = 0;
    uint256 public numTrainers = 0;
    uint256 public numClients = 0;
    uint256 public numLevel_1_Aggregators = 0;
    uint256 public numLevel_2_Aggregators = 0;
    uint256 public numClientsRegistered = 0;
    uint256 public roundNum = 0;
    uint256 public currentRoundNum = 0;
    int256 public Precision = 0;
    int256 public learning_rate = 0;
    int256 batchSize = 0;
    uint256 public layer1Neurons = 0;
    uint256 public layer2Neurons = 0;
    uint256 public level_1_read_index;

    mapping(address => bool) clientsRegistered;
    
    address[] public Trainers;
    mapping(address => bool) public registeredTrainers;
    mapping(address => bool) public trainers_round_Update;
    mapping(uint256 => string[]) public trainersIPFS_hashPointer;

    address[] public level_1_Aggregators;
    mapping(address => bool) public Registered_level_1_Aggregators;
    mapping(address => bool) public Level_1_aggregators_round_update;
    mapping(address => bool) public Level_1_aggregators_round_read;
    mapping(uint256 => string[]) public level_1_aggregators_IPFS_hashPointer;


    address[] public level_2_Aggregators;
    mapping(address => bool) public Registered_level_2_Aggregators;
    mapping(address => bool) public Level_2_aggregators_round_update;
    mapping(address => bool) public Level_2_aggregators_round_read;
    mapping(uint256 => string[]) public level_2_aggregators_IPFS_hashPointer;
    
    modifier isTrainer(){
        require(registeredTrainers[address(msg.sender)], "you are not a trainer.");
         _;
    }

    modifier isLevel_1_Aggregator(){
        require(Registered_level_1_Aggregators[address(msg.sender)] == true, "You are not a level 1 aggregator.");
        _;
    }

    modifier isLevel_2_Aggregator(){
        require(Registered_level_2_Aggregators[address(msg.sender)] == true, "You are not a level 2 aggregator.");
        _;
    }

    

    constructor(uint256 inputDim, uint256 outputDim,
        uint256 NumOfTrainers, uint256 Num_level_1_aggs,
        uint256 Num_level_2_aggs, uint256 totalRounds, int256 precision,
        int256 learningRate, int256 BatchSize, uint256 L1Neurons, uint256 L2Neurons){
        
        inputDimension = inputDim;
        outputDimension = outputDim;
        numTrainers = NumOfTrainers;
        numLevel_1_Aggregators = Num_level_1_aggs;
        numLevel_2_Aggregators = Num_level_2_aggs;
        numClients = numTrainers + numLevel_1_Aggregators + numLevel_2_Aggregators;
        roundNum = totalRounds;
        Precision =precision;
        learning_rate = learningRate;
        batchSize = BatchSize;
        layer1Neurons = L1Neurons;
        layer2Neurons = L2Neurons;
        level_1_read_index = 0;

    }

    function register() external {

        // clientTypeFlag = 1: trainers
        // clientTypeFlag = 2: level_1_aggs
        // clientTypeFlag = 2: level_2_aggs

        require(numClientsRegistered < numClients, "registeration is done!");
        require(!clientsRegistered[address(msg.sender)], "you have already registered");
        clientsRegistered[address(msg.sender)] = true;
        numClientsRegistered = numClientsRegistered + 1;

        // if (clientTypeFlag == 1){
        //     require(Trainers.length < numTrainers, "all trainers are already registered.");
        //     Trainers.push(address(msg.sender));
        //     registeredTrainers[address(msg.sender)] = true;
        //     numClientsRegistered = numClientsRegistered + 1;
        //     clientsRegistered[address(msg.sender)] = true;
        //     trainers_round_Update[address(msg.sender)] = false;
        // }

        // if (clientTypeFlag == 2){
        //     require(level_1_Aggregators.length < numLevel_1_Aggregators, "all level 1 aggregators are already registered.");
        //     level_1_Aggregators.push(address(msg.sender));
        //     Registered_level_1_Aggregators[address(msg.sender)] = true;
        //     numClientsRegistered = numClientsRegistered + 1;
        //     clientsRegistered[address(msg.sender)] = true;
        // }

        // if (clientTypeFlag == 3){
        //     require(level_2_Aggregators.length < numLevel_2_Aggregators, "all level 2 aggregators are already registered.");
        //     level_2_Aggregators.push(address(msg.sender));
        //     Registered_level_2_Aggregators[address(msg.sender)] = true;
        //     numClientsRegistered = numClientsRegistered + 1;
        //     clientsRegistered[address(msg.sender)] = true;
        // }

    }

    function trainersUpdate(string memory IPFS_hashpointer) external {
        require(currentRoundNum <= roundNum - 1, "FL process is terminated");
        require(numClientsRegistered == numClients, "registeration is not done yet!");
        //require(registeredTrainers[address(msg.sender)], "you are not a trainer.");
        //require(!trainers_round_Update[address(msg.sender)], "you have already sent your update in this round");
        require(trainersIPFS_hashPointer[currentRoundNum].length < numTrainers, "All trainers have sent their update in this round.");
        trainersIPFS_hashPointer[currentRoundNum].push(IPFS_hashpointer);
        //trainers_round_Update[address(msg.sender)] = true;

        // if (trainersIPFS_hashPointer[currentRoundNum].length == numTrainers){
            
        // }

    }

    function level_1_AggregationUpdate(string memory IPFS_hashpointer) external {
        require(currentRoundNum <= roundNum - 1, "FL process is terminated");
        require(trainersIPFS_hashPointer[currentRoundNum].length == numTrainers, "Trainers have not completed the training process yet.");
        // require(Registered_level_1_Aggregators[address(msg.sender)] == true, "You are not a level 1 aggregator.");
        // require(Level_1_aggregators_round_update[address(msg.sender)] == false, "you have already sent your update in this round");
        require(level_1_aggregators_IPFS_hashPointer[currentRoundNum].length < numLevel_1_Aggregators, "All level 1 aggregators have sent their update in this round.");
        level_1_aggregators_IPFS_hashPointer[currentRoundNum].push(IPFS_hashpointer);
        // Level_1_aggregators_round_update[address(msg.sender)] = true;
    }

    function level_2_AggregationUpdate(string memory IPFS_hashpointer) external {
        require(currentRoundNum <= roundNum - 1, "FL process is terminated");
        require(trainersIPFS_hashPointer[currentRoundNum].length == numTrainers, "Trainers have not completed the training process yet.");
        require(level_1_aggregators_IPFS_hashPointer[currentRoundNum].length == numLevel_1_Aggregators, " level 1 aggregators have not completed the first level aggregation yet.");
        // require(Registered_level_2_Aggregators[address(msg.sender)] == true, "You are not a level 2 aggregator.");
        //require(Level_2_aggregators_round_update[address(msg.sender)] == false, "you have already sent your update in this round");
        require(level_2_aggregators_IPFS_hashPointer[currentRoundNum].length < numLevel_2_Aggregators, "All level 1 aggregators have sent their update in this round.");
        level_2_aggregators_IPFS_hashPointer[currentRoundNum].push(IPFS_hashpointer);
        //Level_2_aggregators_round_update[address(msg.sender)] = true;

        if(level_2_aggregators_IPFS_hashPointer[currentRoundNum].length == numLevel_2_Aggregators) {
            this.resetForNextRound();
        }
    }

    function trainers_read() external view returns(string[] memory){
        //require(level_2_aggregators_IPFS_hashPointer[currentRoundNum].length == numLevel_2_Aggregators, "level 2 aggregation is not done yet");
        return level_2_aggregators_IPFS_hashPointer[currentRoundNum-1];
    }


    function level_1_aggregator_read(uint256 read_index) external   returns (string[] memory) {
        require(trainersIPFS_hashPointer[currentRoundNum].length == numTrainers, "Trainers have not completed the training process yet.");
        // require(Level_1_aggregators_round_read[address(msg.sender)] == false, "you have already done.");
        //require(level_1_read_index < numTrainers, "All updates have been read in this round");
        string[] memory outputList = new string[](2);
        uint256 index = 0;
        uint256 _read_index  = read_index;
        for (uint256 i = 0; i < 2; i ++){
            outputList[index] = trainersIPFS_hashPointer[currentRoundNum][_read_index];
            index = index + 1;
            _read_index ++;
            // this.level_1_read_index_update();
        }
        //Level_1_aggregators_round_read[address(msg.sender)] = true;
        return outputList;

        //return trainersIPFS_hashPointer[currentRoundNum];
    }

    function level_2_aggregator_read() external  isLevel_2_Aggregator returns(string[] memory){
        //require(Level_2_aggregators_round_read[address(msg.sender)] == false, "you have already done.");
        // Level_2_aggregators_round_read[address(msg.sender)] = true;
        return level_1_aggregators_IPFS_hashPointer[currentRoundNum];
    }


    function level_1_read_index_update() external {
        level_1_read_index = level_1_read_index + 1;
    }

    function resetForNextRound() external {
        currentRoundNum = currentRoundNum + 1;
        level_1_read_index = 0;

        // for (uint256 i = 0; i < numTrainers; i++){
        //     trainers_round_Update[Trainers[i]] = false;
        // }

        // for (uint256 i = 0; i < numLevel_1_Aggregators; i++){
        //     Level_1_aggregators_round_update[level_1_Aggregators[i]] = false;
        //     Level_1_aggregators_round_read[level_1_Aggregators[i]] = false;
        // }

        // for (uint256 i = 0; i < numLevel_2_Aggregators; i++){
        //     Level_2_aggregators_round_update[level_2_Aggregators[i]] = false;
        //     Level_2_aggregators_round_read[level_2_Aggregators[i]] = false;
        // }
    }

    

}
