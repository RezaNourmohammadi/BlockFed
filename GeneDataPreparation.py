import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def geneDataPreparation():
    path = "/home/iman/projects/kara/blockchain_based_Federated_learning/federatedlearning/codes/Devices/Gene_expression_data.txt"
    columnNames = []
    for i in range(60660):
        text = f'gene_ID_{i}'
        columnNames.append(text)

    targets = []

    for i in range(200):
        if i <= 99:
            targets.append(0)
        if i > 99:
            targets.append(1)

    gene_ExpressionData = pd.read_csv(
                path, sep=',', names= columnNames)

    #gene_ExpressionData["activity"] = targets

    print(gene_ExpressionData.head())

    var_val = gene_ExpressionData.var()
    num_dim = 400
    sorted_features = var_val.sort_values(ascending = False, axis = 'index')[0:num_dim].index

    #normalized_data=(gene_ExpressionData-gene_ExpressionData.min())/(gene_ExpressionData.max()-gene_ExpressionData.min())

    gene_ExpressionRedeucedData = gene_ExpressionData[sorted_features]
    normalized_data=(gene_ExpressionRedeucedData-gene_ExpressionRedeucedData.min())/(gene_ExpressionRedeucedData.max()-gene_ExpressionRedeucedData.min())
    return normalized_data, np.array(targets)