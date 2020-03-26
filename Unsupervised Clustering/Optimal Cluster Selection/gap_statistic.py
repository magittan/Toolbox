import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs 
import seaborn as sns; sns.set()
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

def creating_classifiers(max_number_clusters,train_data,random_state=0):
    k_means_algos = []
    ks = list(range(1,max_number_clusters+1))
    for k in ks:
        print(k)
        kmeans = KMeans(init='k-means++',n_clusters = k,n_init=10,verbose=3,n_jobs=-1,random_state=random_state)
        kmeans.fit(train_data)
        k_means_algos.append(kmeans)
    return k_means_algos

def W_k(clusters):
    total=0
    for i in range(len(clusters)):
        D = pairwise_distances(clusters[i])
        total += np.sum(D)/(2*len(clusters[i]))
    return total

def calculation_of_W_ks(max_number_clusters,X):
    output = []
    classifiers = creating_classifiers(max_number_clusters,X)
    for i in range(max_number_clusters-1):
        clusters = np.array([X[classifiers[i].labels_==j] for j in range(i+1)])
        output.append(W_k(clusters))
                      
    return np.array(output)
                      
def bounding_dimensions(X):
    dimension_ranges = []
    for i in range(X.shape[1]):
        dimension_ranges.append([min(X[:,i]),max(X[:,i])])
    return np.array(dimension_ranges)

def generating_uniform_over_variables(ranges,size=1000):
    return np.array([np.random.uniform(low=r[0],high=r[1],size=size) for r in ranges]).T

def calculation_of_W_ks_star(max_number_clusters,X,random_state=0):
    """
    Input
    -----
    
    X: (number of samples, dimension of samples)
    
    """
    output = []
    dimension_ranges = bounding_dimensions(X)
    uniform_sample = generating_uniform_over_variables(dimension_ranges,size=len(X))
    
    classifiers = creating_classifiers(max_number_clusters,uniform_sample,random_state=random_state)
    
    for i in range(max_number_clusters-1):
        clusters = np.array([uniform_sample[classifiers[i].labels_==j] for j in range(i+1)])
        output.append(W_k(clusters))
                      
    return np.array(output)

def calculation_of_log_W_ks_star_B(max_number_clusters,X,B):
    B_simulations = np.array([np.log(calculation_of_W_ks_star(max_number_clusters,X,random_state=i)) for i in range(B)])
    B_means = np.mean(B_simulations,axis=0)
    
    return B_means

def calculation_of_log_W_ks(max_number_clusters,X):
    return np.log(calculation_of_W_ks(max_number_clusters,X))

def calculation_of_log_W_ks_star_B_A(max_number_clusters,X,B):
    B_simulations = np.array([np.log(calculation_of_W_ks_star(max_number_clusters,X,random_state=i)) for i in range(B)])
    B_means = np.mean(B_simulations,axis=0)
    
    #Calculating Standard Deviation
    sd_k = np.power(np.mean([np.power((B_simulations[i]-B_means),2) for i in range(B)],axis=0),0.5)
    s_k = sd_k*np.power(1+1/B,0.5)
    
    return B_means,s_k