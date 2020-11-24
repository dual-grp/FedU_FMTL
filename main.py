#!/usr/bin/env python
import h5py
import matplotlib.pyplot as plt
import numpy as np
import argparse
import importlib
import random
import os
from FLAlgorithms.servers.serveravg import FedAvg
from FLAlgorithms.servers.serverpFedMe import pFedMe
from FLAlgorithms.servers.serverperavg import PerAvg
from FLAlgorithms.servers.serverSSGD import FedSSGD
from utils.model_utils import read_data
from FLAlgorithms.trainmodel.models import *
from utils.plot_utils import *
import torch
torch.manual_seed(0)

def main(dataset, algorithm, model, batch_size, learning_rate, beta, L_k, num_glob_iters,
         local_epochs, optimizer, numusers, K, personal_learning_rate, times):\
    
    # Get device status: Check GPU or CPU
    device = torch.device("cuda:{}".format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else "cpu")

    data = read_data(dataset) , dataset

    for i in range(times):
        print("---------------Running time:------------",i)
        # Generate model
        if(model == "mclr"):
            if(dataset == "human_activity"):
                model = Mclr_Logistic(561,6).to(device), model
            elif(dataset == "gleam"):
                model = Mclr_Logistic(561,6).to(device), model
            elif(dataset == "vehicle_sensor"):
                model = Mclr_Logistic(100,2).to(device), model
            elif(dataset == "Synthetic"):
                model = Mclr_Logistic(60,10).to(device), model
            else:#(dataset == "Mnist"):
                model = Mclr_Logistic().to(device), model

        if(model == "dnn"):
            if(dataset == "human_activity"):
                model = DNN2(561,100,100,12).to(device), model
            elif(dataset == "gleam"):
                model = DNN(561,20,6).to(device), model
            elif(dataset == "vehicle_sensor"):
                model = DNN(100,20,2).to(device), model
            elif(dataset == "Synthetic"):
                model = DNN(60,20,10).to(device), model
            else:#(dataset == "Mnist"):
                model = DNN().to(device), model

        # select algorithm

        if(algorithm == "FedAvg"):
            server = FedAvg(device, data, algorithm, model, batch_size, learning_rate, beta, L_k, num_glob_iters, local_epochs, optimizer, numusers, i)
        if(algorithm == "pFedMe"):
            server = pFedMe(device, data, algorithm, model, batch_size, learning_rate, beta, L_k, num_glob_iters, local_epochs, optimizer, numusers, K, personal_learning_rate, i)
        if(algorithm == "SSGD"):
            server = FedSSGD(device, data, algorithm, model, batch_size, learning_rate, beta, L_k, num_glob_iters, local_epochs, optimizer, numusers, i)

        server.train()
        server.test()

    average_data(num_users=numusers, loc_ep1=local_epochs, Numb_Glob_Iters=num_glob_iters, lamb=L_k,learning_rate=learning_rate, beta = beta, algorithms=algorithm, batch_size=batch_size, dataset=dataset, k = K, personal_learning_rate = personal_learning_rate,times = times)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="vehicle_sensor", choices=["human_activity", "gleam","vehicle_sensor","Mnist", "Synthetic", "Cifar10"])
    parser.add_argument("--model", type=str, default="mclr", choices=["dnn", "mclr", "cnn"])
    parser.add_argument("--batch_size", type=int, default=20)
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Local learning rate")
    parser.add_argument("--beta", type=float, default=1.0, help="Average moving parameter for pFedMe, or Second learning rate of Per-FedAvg")
    parser.add_argument("--L_k", type=int, default=0, help="Regularization term")
    parser.add_argument("--num_global_iters", type=int, default=200)
    parser.add_argument("--local_epochs", type=int, default=20)
    parser.add_argument("--optimizer", type=str, default="SGD")
    parser.add_argument("--algorithm", type=str, default="FedAvg",choices=["pFedMe", "PerAvg", "FedAvg", "SSGD"]) 
    parser.add_argument("--numusers", type=int, default=23, help="Number of Users per round")
    parser.add_argument("--K", type=int, default=5, help="Computation steps")
    parser.add_argument("--personal_learning_rate", type=float, default=0.09, help="Persionalized learning rate to caculate theta aproximately using K steps")
    parser.add_argument("--times", type=int, default=1, help="running time")
    args = parser.parse_args()

    print("=" * 80)
    print("Summary of training process:")
    print("Algorithm: {}".format(args.algorithm))
    print("Batch size: {}".format(args.batch_size))
    print("Learing rate       : {}".format(args.learning_rate))
    print("Average Moving       : {}".format(args.beta))
    print("Subset of users      : {}".format(args.numusers))
    print("Number of global rounds       : {}".format(args.num_global_iters))
    print("Number of local rounds       : {}".format(args.local_epochs))
    print("Dataset       : {}".format(args.dataset))
    print("Local Model       : {}".format(args.model))
    print("=" * 80)

    main(
        dataset=args.dataset,
        algorithm = args.algorithm,
        model=args.model,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        beta = args.beta, 
        L_k = args.L_k,
        num_glob_iters=args.num_global_iters,
        local_epochs=args.local_epochs,
        optimizer= args.optimizer,
        numusers = args.numusers,
        K=args.K,
        personal_learning_rate=args.personal_learning_rate,
        times = args.times
        )
