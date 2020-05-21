import math

import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.spatial import distance

learning_coeff = 0.1

# epoch_error = 0.0

momentum_coeff = 0.2


class NeuralNetwork(object):
    def __init__(self, number_of_radial, number_of_linear, input_data_file, is_bias=0):
        np.random.seed(30)
        self.radial_layer_weights = []
        self.linear_layer_weights = []
        self.delta_weights_linear_layer = []
        self.number_of_radial = number_of_radial
        self.number_of_linear = number_of_linear
        self.is_bias = is_bias
        self.input_data, self.expected_data = self.file_input(input_data_file)
        self.initialze_weights()
        self.radial_coefficient = np.ones(number_of_radial)
        # self.set_radial_coefficient()
        self.epoch_error = 0.0
        self.error_for_epoch = []
        self.epoch_for_error = []
        # self.delta_weights_hidden_layer = []
        # self.expected_data = self.file_input(expected_data_file)

    def initialze_weights(self):
        input = self.input_data
        np.random.shuffle(input)
        for i in range(self.number_of_radial):
            self.radial_layer_weights.append(input[i])
        self.linear_layer_weights = 2 * np.random.random(
            (self.number_of_radial + self.is_bias, self.number_of_linear)) - 1
        self.delta_weights_linear_layer = np.zeros((self.number_of_radial + self.is_bias, self.number_of_linear))

    # def calculateDistance(self, inp, forCalculate):
    #     return distance.euclidean(i, inp))

    # def set_radial_coefficient(self):
    #     for i in self.radial_layer_weights:
    #         max = 0
    #         for j in self.radial_layer_weights:
    #             neural_distance = distance.euclidean(i, j)
    #             if neural_distance > max:
    #                 max = neural_distance
    #         self.radial_coefficient.append(max / math.sqrt(2 * self.number_of_radial))

    def linear_func(self, x):
        return x

    def linear_derivative(self, x):
        return 1

    # coefficient to wspoclzynnik z self.coefficient dla danego neuronu
    def rbf_gaussian(self, input, radial_weight, coefficient):
        return np.exp(-1 * ((distance.euclidean(input, radial_weight)) ** 2) / (2 * coefficient ** 2))

    def feed_forward(self, input_data):
        radial_layer_output = []
        for i in range(len(self.radial_layer_weights)):
            radial_layer_output.append(
                self.rbf_gaussian(input_data, self.radial_layer_weights[i], self.radial_coefficient[i]))
        if self.is_bias == 1:
            radial_layer_output = np.insert(radial_layer_output, 0, 1)
        output_layer_output = self.linear_func(np.dot(radial_layer_output, self.linear_layer_weights))
        return radial_layer_output, output_layer_output

    def backward_propagation(self, radial_layer_output, linear_layer_output, input_data, output_data):
        avr_err = 0.0
        output_difference = linear_layer_output - output_data  # required for mean squared error

        for i in output_difference:
            avr_err += i ** 2
        avr_err /= 2
        self.epoch_error += avr_err

        delta_coefficient_outp = output_difference * self.linear_derivative(linear_layer_output)
        output_adj = []
        for i in delta_coefficient_outp:
            output_adj.append(radial_layer_output * i)

        output_adj = np.asarray(output_adj)
        actual_output_adj = (learning_coeff * output_adj.T + momentum_coeff * self.delta_weights_linear_layer)
        self.linear_layer_weights -= actual_output_adj
        self.delta_weights_linear_layer = actual_output_adj

    def train(self, epoch_count):
        combined_data = list(zip(self.input_data, self.expected_data))
        for epoch in range(epoch_count):
            self.epoch_error = 0.0
            np.random.shuffle(combined_data)
            for inp, outp in combined_data:
                radial_layer_output, linear_layer_output = self.feed_forward(inp)
                self.backward_propagation(radial_layer_output, linear_layer_output, inp, outp)
                # TODO: dzielic przez liczbe punktów
            self.epoch_error /= len(self.input_data)
            self.epoch_for_error.append(epoch)
            self.error_for_epoch.append(self.epoch_error)
            print(epoch, "  ", self.epoch_error)

    def file_input(self, file_name):
        with open(file_name, "r") as f:
            expected_val = []
            input_arr = []
            data = csv.reader(f, delimiter=' ')
            for row in data:
                tmp_arr = []
                for i in row:
                    tmp_arr.append(float(i))
                expected_val.append(float(row[1]))
                input_arr.append(tmp_arr)
        return np.asarray(input_arr), np.asarray(expected_val)

    # def graph(self):
    #     plt.plot(self.epoch_for_error, self.error_for_epoch, 'ro', markersize=1)
    #     plt.title("Błąd średniokwadratowy w zależności od epoki")
    #     plt.ylabel("Błąd średniokwadratowy")
    #     plt.xlabel("Epoka")
    #     plt.show()


NeuNet = NeuralNetwork(4, 1, "approximation_2.txt", 1)
NeuNet.train(2000)
# print("Wynik:")
# for i in NeuNet.input_data:
#     print(NeuNet.feed_forward(i, True)[1])
# NeuNet.graph()
