import math
import numpy as np

class KalmanFilter(object):
    def __init__(self, initial_distance=1.35, initial_distance_var=0.1**2):
        self.state = np.transpose(np.array([initial_distance, 0.0]))     # distance, velocity
        self.state_predict = None
        self.cov = np.array([[initial_distance_var, 0],
                   [0, (0.05/0.1)**2]])
        self.cov_predict = None

    def distance(self):
        return self.state[0]

    def distance_std(self):
        return math.sqrt(self.cov[0,0])

    def velocity(self):
        return self.state[1]

    def velocity_std(self):
        return math.sqrt(self.cov[1,1])

    def predict(self, delta_t):
        self.state_predict = np.copy(self.state)
        self.state_predict[0] += self.state_predict[1] * delta_t
        self.F = np.array([[1, delta_t],
                      [0, 1]])
        self.Q = np.array([[0.005 * delta_t/0.1, 0],
                     [0, 0.005/0.1 * delta_t/0.1]])
        self.cov_predict = np.matmul(np.matmul(self.F, self.cov), np.transpose(self.F)) + self.Q

    def correct(self, distance):
        # correct
        H = np.array([[1, 0]])
        y_correct = distance - np.matmul(H, self.state_predict)
        R = np.array([0.2])
        S = np.matmul(np.matmul(H, self.cov_predict), np.transpose(H)) + R
        S_inv = np.array([1.0/S[0]])
        #print(cov_predict.shape)
        #print(H.shape)
        #print(S_inv.shape)
        K = np.matmul(np.matmul(self.cov_predict, np.transpose(H)), S_inv)
        state_correct = np.copy(self.state_predict)
        state_correct += np.matmul(K, y_correct)
        cov_correct = np.matmul((np.identity(2) - np.matmul(K, H)), self.cov_predict)

        self.state = state_correct
        self.cov = cov_correct

    def print_predict(self):
        print(f"F:\n{F}")
        print(f"Q:\n{Q}")
        print(f"State predict: \n{self.state_predict}")
        print(f"Cov predict: \n{self.cov_predict}")

    def print_correct(self):
        print(f"State correct: \n{self.state}")
        print(f"Cov correct: \n{self.cov}")

