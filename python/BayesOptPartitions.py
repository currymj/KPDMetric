from __future__ import absolute_import, division, print_function, \
    unicode_literals
from GPyOpt.methods import BayesianOptimization
import numpy as np
import subprocess
import pickle
import os

print("Starting...")

TRAJECTORIES = 100
PAIRS_0 = 250
ALTS_0 = 10
E_P = 10/7
E_A = 1/7

CPLEX_PATH = os.environ.get(
    'CPLEX_PATH',
    '/Users/curry/Applications/IBM/ILOG/CPLEX_Studio1271/cplex/bin/x86-64_osx')
output_dir = os.environ.get('RUN_OUTPUT', '.')
cacheIN = np.empty([0, 5])
cacheOUT = np.empty([0, TRAJECTORIES, 14])
jargs = []
XL = []
for i in range(6):
    XL.append(np.empty([0, 5]))
XL.append(np.empty([0, 6]))
XL.append(np.empty([0, 5]))
for i in range(5):
    XL.append(np.empty([0, 6]))
XL.append(np.empty([0, 5]))

YL = []
for i in range(14):
    YL.append(np.empty([0, 1]))


MD = []
for i in range(14):
    MD.append(None)

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
        if len(X) == 0:
            X = np.array([arg])
        else:
            X = np.append(X, [arg], axis=0)
        MT = 0
        for i in range(TRAJECTORIES):
            java_call = [
                "java",
                "-Djava.library.path=" + CPLEX_PATH,
                "-Xmx8g", "-jar", "Simulation1.jar"
            ]
            for j in arg:
                java_call.append(str(j))
            java_call.append(str(PAIRS_0))
            java_call.append(str(ALTS_0))
            java_call.append(str(E_P))
            java_call.append(str(E_A))
            print("Running the simulator")
            out = subprocess.check_output(java_call).decode()
            out = out.split(" ")
            print("Finished")
            MT += float(out[13])
        MT /= TRAJECTORIES
        if len(Y) == 0:
            Y = np.array([[MT]])
        else:
            Y = np.append(Y, [[MT]], axis=0)
        ci = open(output_dir + "X" + l2f(jargs), "wb")
        co = open(output_dir + "Y" + l2f(jargs), "wb")
        pickle.dump(X, ci)
        pickle.dump(Y, co)
        ci.close()
        co.close()

        R = np.append(R, [[MT]], axis=0)
    print("Returned")
    return R



complete_domain = [{'name': 'patientWeight', 'type': 'continuous',
                    'domain': (0, 500)},  # 0
                   {'name': 'PatientCPRA', 'type': 'continuous',
                       'domain': (0, 1)},  # 1
                   {'name': 'BloodTypePatient', 'type': 'discrete',
                       'domain': (0, 1, 2, 3)},  # 2
                   {'name': 'BloodTypeDonor', 'type': 'discrete',
                       'domain': (0, 1, 2, 3)},  # 3
                   {'name': 'isWifePatient', 'type': 'discrete',
                       'domain': (0, 1)},  # 4
                   {'name': 'isCompatible', 'type': 'discrete',
                       'domain': (0, 1)},  # 5
                   {'name': 'isPatientMale', 'type': 'discrete',
                       'domain': (0, 1)},  # 6
                   {'name': 'patientHLAB1', 'type': 'discrete',
                    'domain': (5, 7, 8, 12, 13, 14, 15, 16, 17, 18, 21, 22, 27,
                               35, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48,
                               49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                               61, 62, 63, 64, 65, 67, 70, 71, 72, 73, 75, 76,
                               77, 78, 81, 82, 703, 804, 1304, 2708, 3901,
                               3902, 3905, 4005, 5102, 5103, 7801, 8201)},
                   {'name': 'patientHLAB2', 'type': 'discrete',
                    'domain': (5, 7, 8, 12, 13, 14, 15, 16, 17, 18, 21, 22, 27,
                               35, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48,
                               49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                               61, 62, 63, 64, 65, 67, 70, 71, 72, 73, 75, 76,
                               77, 78, 81, 82, 703, 804, 1304, 2708, 3901,
                               3902, 3905, 4005, 5102, 5103, 7801, 8201)},
                   {'name': 'patientHLADR1', 'type': 'discrete',
                    'domain': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                               15, 16, 17, 18, 103, 1403, 1404)},
                   {'name': 'patientHLADR2', 'type': 'discrete',
                    'domain': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                               15, 16, 17, 18, 103, 1403, 1404)}]  # 10

complete_range = [
    "Donor Age",
    "Donor eGFR",
    "Donor BMI",
    "Donor systolic BP",
    "Is the donor African American?",
    "Is the donor a cigarette user?",
    "Are both donor and patient male?",
    "Is the donor ABO compatible with the patient?",
    "HLAB1 mismatch?",
    "HLAB2 mismatch?",
    "HLADR1 mismatch?",
    "HLADR2 mismatch?",
    "Donor to patient weight ratio",
    "Match time"]

if __name__ == '__main__':
    global X
    global Y
    X = np.array([])
    Y = np.array([])

    mixed_domain = complete_domain[1:6]
    myBopt = BayesianOptimization(
        f=f,
        domain=mixed_domain,
        acquisition_type='LCB',
        num_cores=8)
    # Continue optimization until maximized normalized standard deviation
    # is 0.1
    myBopt.run_optimization(
        max_iter=100,
        eps=.1,
        evaluations_file=output_dir + "E1.txt",
        models_file=output_dir+"M1.txt")
