import math
import neuralgas
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.spatial import distance

learning_coeff = 0.1
momentum_coeff = 0.2


class NeuralNetwork(object):
    def __init__(self, number_of_radial, number_of_linear, number_of_class, input_data_file, is_bias=0):
        np.random.seed(0)
        self.radial_layer_weights = []
        self.linear_layer_weights = []
        self.number_of_class = number_of_class
        self.delta_weights_linear_layer = []
        self.number_of_radial = number_of_radial
        self.number_of_linear = number_of_linear
        self.is_bias = is_bias
        self.input_data, self.expected_data = self.file_input(input_data_file)
        self.initialze_weights()
        self.radial_coefficient = []
        self.set_radial_coefficient()
        self.epoch_error = 0.0
        self.error_for_epoch = []
        self.epoch_for_error = []

    def initialze_weights(self):
        input = np.copy(self.input_data)
        SOM = neuralgas.SelfOrganizingMap(numberOfNeurons=self.number_of_radial, input_data_file=input, type=1,
                                          radius=0.5, alpha=0.5, gaussian=0)
        SOM.train(50)
        self.radial_layer_weights = SOM.neuron_weights
        # np.random.shuffle(input)
        # for i in range(self.number_of_radial):
        #     self.radial_layer_weights.append(input[i])
        self.linear_layer_weights = 2 * np.random.random(
            (self.number_of_radial + self.is_bias, self.number_of_linear)) - 1
        self.delta_weights_linear_layer = np.zeros((self.number_of_radial + self.is_bias, self.number_of_linear))

    def set_radial_coefficient(self):
        for i in self.radial_layer_weights:
            max = 0
            for j in self.radial_layer_weights:
                neural_distance = distance.euclidean(i, j)
                if neural_distance > max:
                    max = neural_distance
            self.radial_coefficient.append(max / math.sqrt(2 * self.number_of_radial))

    def linear_func(self, x):
        return x

    def linear_derivative(self, x):
        return 1

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

    def backward_propagation(self, radial_layer_output, linear_layer_output, output_data):
        avr_err = 0.0
        output_difference = linear_layer_output - output_data

        for i in output_difference:
            avr_err += i ** 2
        avr_err /= 2
        self.epoch_error += avr_err

        delta_coefficient_outp = output_difference * self.linear_derivative(linear_layer_output)
        output_adj = []
        val = 0
        for i in delta_coefficient_outp:
            # TODO: poprawic zeby bylo inacej a dialalo tak samo
            val = [i * j for j in radial_layer_output]
            output_adj.append(val)
        output_adj = np.asarray(output_adj)

        output_adj = np.asarray(output_adj)
        actual_output_adj = (learning_coeff * output_adj.T + momentum_coeff * self.delta_weights_linear_layer)
        self.linear_layer_weights -= actual_output_adj
        self.delta_weights_linear_layer = actual_output_adj

    def train(self, epoch_count):
        error_test_data_plot = []
        confusion_matrix = np.zeros([self.number_of_class, self.number_of_class])
        combined_data = list(zip(self.input_data, self.expected_data))
        number_of_expected = np.zeros([self.number_of_class])
        number_of_actual = np.zeros([self.number_of_class])
        number_of_actual_all = []
        outputs = list(self.expected_data)
        for i in range(len(number_of_expected)):
            number_of_expected[i] = outputs.count(i+1)
        for epoch in range(epoch_count):
            self.epoch_error = 0.0
            np.random.shuffle(combined_data)
            for inp, outp in combined_data:
                radial_layer_output, linear_layer_output = self.feed_forward(inp)
                for i in range(len(linear_layer_output)):
                    if int(round(linear_layer_output[i])) == outp:
                        number_of_actual[int(round(linear_layer_output[i] - 1))] += 1
                if epoch == epoch_count - 1:
                    confusion_matrix[int(outp) - 1][int(round(linear_layer_output[0] - 1))] += 1
                self.backward_propagation(radial_layer_output, linear_layer_output, outp)
            number_of_actual_all.append(number_of_actual)
            number_of_actual = np.zeros([self.number_of_class])
            self.epoch_error /= self.input_data.shape[0]
            self.epoch_for_error.append(epoch)
            self.error_for_epoch.append(self.epoch_error)
            error_test_data_plot.append(self.test_network("classification_test.txt", False))
            print(epoch, "  ", self.epoch_error)
        print(confusion_matrix)
        self.plot_number_of_classifications("Klasyfikacja", number_of_expected, number_of_actual_all, "Epoch", "Number")
        self.plot_uni_graph("Błąd średniokwadratowy dla danych testowych", np.arange(0, epoch_count, 1),
                            error_test_data_plot,
                            "Epoki",
                            "Wartość błędu")
        self.plot_uni_graph("Błąd średniokwadratowy", self.epoch_for_error, self.error_for_epoch, "Epoki",
                            "Wartość błędu")
        print(self.test_network("classification_test.txt", True))

    def file_input(self, file_name):
        with open(file_name, "r") as f:
            expected_val = []
            input_arr = []
            data = csv.reader(f, delimiter=' ')
            for row in data:
                expected_val.append(float(row[-1]))
                input_arr.append(np.float_(row[:-1]))
        return np.asarray(input_arr), np.asarray(expected_val)

    def plot_number_of_classifications(self, title, expected_matrix, actual_matrix, x_label, y_label):
        colors = ['#116315', '#FFD600', '#FF6B00', '#5199ff', '#FF2970', '#B40A1B', '#E47CCD', '#782FEF', '#45D09E',
                  '#FEAC92']
        inputX = []
        epoch = []
        for j in range(self.number_of_class):
            inputY = []
            for i in range(len(actual_matrix)):
                inputY.append(actual_matrix[i][j])
                if j == 0:
                    epoch.append(i)
            inputY = np.asarray(inputY)
            inputY = inputY / expected_matrix[j]
            plt.plot(inputY, colors[j], markersize=3, marker='o', ls='', label=str(j+1))
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.legend()
        plt.show()

    def plot_uni_graph(self, title, x_val, y_val, x_label, y_label):
        plt.plot(x_val, y_val, 'r', markersize=3)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def plot_uni_graph_2_functions(self, title, x_val, y_val, x_label, y_label, x_val_1, y_val_1, function):
        plt.plot(x_val, y_val, 'ro', markersize=1, label=function)
        plt.plot(x_val_1, y_val_1, 'bo', markersize=1, label='Aproksymacja funkcji')
        plt.title(title)
        plt.legend()
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def test_network(self, test_file, is_graph=False):
        test_data, expected_data = self.file_input(test_file)
        test_output = []
        err = 0.0
        for test_pair in test_data:
            hidden_layer_output_test, output_layer_output_test = self.feed_forward(test_pair)
            test_output.append(output_layer_output_test)
        for i in range(len(test_output)):
            err += (test_output[i] - expected_data[i]) ** 2
        err /= 2
        # if is_graph:
        #     self.plot_uni_graph_2_functions("Przebieg funkcji testowej oraz jej aproksymacji", test_data,
        #                                     expected_data, "X",
        #                                     "Y", test_data, test_output, "Funkcja testowa")
        return (err / len(test_output))


NeuNet = NeuralNetwork(10, 1, 3, "classification_train.txt", 1)
NeuNet.train(100)