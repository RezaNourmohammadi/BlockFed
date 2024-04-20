import numpy as np
from GeneDataPreparation import geneDataPreparation
from utils.flutils import *
from clients.learningModel import *

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
learningModel = FLlearningModel(10, 400, 2, 0.1)
learningModel.train_model(data)
test_batched = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(len(y_test))

accuracy = []
for(X_test, Y_test) in test_batched:
            acc, loss = learningModel.test_model(X_test, Y_test, 0, "device_0")
            accuracy.append(np.array(acc))

print(np.mean(accuracy))