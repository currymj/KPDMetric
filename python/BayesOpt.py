from __future__ import absolute_import, division, print_function, unicode_literals
import os
import pickle
import subprocess

import numpy as np
from GPyOpt.methods import BayesianOptimization

print("Starting...")

TRAJECTORIES = 32
PAIRS_0 = 250
ALTS_0 = 10
E_P = 10
E_A = 1
CPLEX_PATH=os.environ['CPLEX_PATH']

jargs = []


def l2f(a):
    s = ""
    for i in a:
        s += str(i)
    return s


def f(Xl):
    global X
    global Y
    R = np.empty([0, 1])
    for XI in range(len(Xl)):
        arg = Xl[XI]
        X = np.append(X, [arg], axis=0)
        MT = 0 
        for i in range(TRAJECTORIES):
            I = [
                "java",
                "-Djava.library.path=" + CPLEX_PATH,
                "-Xmx8g", "-jar", "Simulation1.jar"
            ]
            I.append(str(arg[0]))
            for j in jargs:
                I.append(str(j))
            I.append(str(PAIRS_0))
            I.append(str(ALTS_0))
            I.append(str(E_P))
            I.append(str(E_A))
            print("Running the simulator")
            out = subprocess.check_output(I).decode()
            out = out.split(" ")
            print("Finished")
            MT += float(out[13])
        MT /= TRAJECTORIES
        Y = np.append(Y, [[MT]], axis=0)
        ci = open("X" + l2f(jargs), "wb")
        co = open("Y" + l2f(jargs), "wb")
        pickle.dump(X, ci)
        pickle.dump(Y, co)
        ci.close()
        co.close()

        R = np.append(R, [[MT]], axis=0)
    print("Returned")
    return R


dom = [{'name': 'PatientCPRA', 'type': 'continuous', 'domain': (0, 1)}]
for BTP in range(4):
    print("done {}".format(BTP))
    for BTD in range(4):
        print("intermediate {}".format(BTD))
        maxi = 5
        X = np.empty([0, 1])
        Y = np.empty([0, 1])
        jargs = [BTP, BTD, 0, 0]
        if jargs == [1, 3, 0, 0]:
            TRAJECTORIES = 64
        if jargs == [2, 1, 0, 0]:
            TRAJECTORIES = 128
        elif jargs == [3, 3, 0, 0]:
            TRAJECTORIES = 128
        else:
            TRAJECTORIES = 32
        print("Bayesian optimization for master features " + str(jargs))
        myBopt = BayesianOptimization(
            f=f, domain=dom, acquisition_type='LCB', num_cores=8)
        myBopt.run_optimization(
            max_iter=maxi,
            eps=0,
            evaluations_file="E" + l2f(jargs) + ".txt",
            models_file="M" + l2f(jargs) + ".txt")
        myBopt.plot_acquisition("Plot" + l2f(jargs) + ".png")
