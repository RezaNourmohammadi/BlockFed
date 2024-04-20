from utils.flutils import *
import numpy as np
from GeneDataPreparation import geneDataPreparation

def clients_data_creation(mainDataPath, num_clients):
    # data_list, label_list = load(mainDataPath)
    data_list, label_list = geneDataPreparation()
    data_list = np.array(data_list.values.tolist())
    labels = list(set(label_list.tolist())) #unique labels
    n_values = np.max(label_list) + 1
    label_list = np.eye(n_values)[label_list]
    X_train, X_test, y_train, y_test = train_test_split(data_list,
                                                    label_list,
                                                    test_size=0.3,
                                                    random_state=7)
    
    data = list(zip(X_train, y_train))
    random.shuffle(data)
    size = len(data)//num_clients
    shards = [data[i:i + size] for i in range(0, size*num_clients, size)]
    test_batched = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(len(y_test))
    
    return shards, test_batched