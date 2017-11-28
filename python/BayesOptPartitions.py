from __future__ import absolute_import, division, print_function, \
    unicode_literals
from GPyOpt.methods import BayesianOptimization
import numpy as np
import subprocess
import pickle
import os

print("Starting...")

TRAJECTORIES = 2
PAIRS_0 = 250
ALTS_0 = 10
E_P = 10/7
E_A = 1/7

CPLEX_PATH = os.environ.get(
    'CPLEX_PATH',
    '/Users/curry/Applications/IBM/ILOG/CPLEX_Studio1271/cplex/bin/x86-64_osx')
output_dir = os.environ.get('RUN_OUTPUT', './')
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
{'BloodTypePatient': 0,
'BloodTypeDonor': 0,
'isWifePatient': 0,
'isCompatible': 0}
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

# time for some classes
# we want a class that 
class SimulatorFunction:
    def __init__(self, vars_to_optimize, default_vals, all_vars):
        self.vars_to_optimize = vars_to_optimize
        self.default_vals = default_vals
        self.all_vars = all_vars
    
    def __call__(self,Xl):
        r = np.empty([0,1])
        for x in Xl:
            input_dict = dict(zip(self.vars_to_optimize, x))
            mt = 0
            for i in range(TRAJECTORIES):
                java_call = [
                    "java",
                    "-Djava.library.path=" + CPLEX_PATH,
                    "-Xmx8g", "-jar", "Simulation1.jar"
                ]
                for j in self.all_vars:
                    if j in input_dict:
                        java_call.append(str(input_dict[j]))
                    else:
                        java_call.append(str(self.default_vals[j]))
                java_call.append(str(PAIRS_0))
                java_call.append(str(ALTS_0))
                java_call.append(str(E_P))
                java_call.append(str(E_A))
                print("Running the simulator")
                out = subprocess.check_output(java_call,timeout=100).decode()
                out = out.split(" ")
                print("Finished")
                mt += float(out[13])
            mt /= TRAJECTORIES

            r = np.append(r, [[mt]], axis=0)
        print("Returned")
        return r

def f(Xl):
    print(Xl)
    r = np.empty([0, 1])
    print(len(Xl))
    for XI in range(len(Xl)):
        arg = Xl[XI]
        mt = 0
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
            mt += float(out[13])
        mt /= TRAJECTORIES

        r = np.append(r, [[mt]], axis=0)
    print("Returned")
    return r



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

# 
if __name__ == '__main__':
    mixed_domain = complete_domain[1:6]
    print(mixed_domain)
    myBopt = BayesianOptimization(
        f=f     ,
           domain=mixed_domain,
        acquisition_type='LCB',
        num_cores=4)
    # Continue optimization until maximized normalized standard deviation
    # is 0.1
    myBopt.run_optimization(
        max_iter=1,
        eps=.1,
        evaluations_file=output_dir + "E1.txt",
        models_file=output_dir+"M1.txt"
    )
        
    
    # using the "context" keyword arg we can fix certain variables. this is exactly what we need!
    # myBopt.x_op gives the current optimal location, after we've run a few iterations.