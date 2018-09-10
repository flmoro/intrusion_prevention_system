"""This module..."""
import ast
from datetime import datetime
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer


class Formatter:
    """Formats the raw csv"""

    def __init__(self, flows):
        """Initializes the main variable"""

        self.flows = flows

    def format_flows(self, training_model=False):
        """Formats the raw flows into flows to used in machine learning algorithms"""

        header = []
        for entry in self.flows:
            if training_model == False:
                self.delete_features(entry)
                self.change_columns(entry)
                # checks if is the header
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.replace_missing_features(entry)
                    self.change_data_types(entry)
                    self.format_flag(entry)
            else:
                if "ts" in entry[0]:
                    header.append(entry)
                else:
                    self.change_data_types(entry, True)
        del self.flows[0]

        return header, self.flows

    @staticmethod
    def delete_features(entry):
        """Deletes features that won't be used"""

        del entry[9:11]  # deletes fwd and stos
        del entry[11:25]  # deletes from opkt to dvln
        del entry[13:]  # deletes from idmc to the end

    @staticmethod
    def change_columns(entry):
        """Changes the columns in order to separate the features
        that will be used in the machine learning algorithms"""

        index_order = [0, 1, 11, 12, 3, 4, 7, 8, 5, 6, 2, 9, 10]
        # temporary store the entry with its new order
        tmp = [entry[idx] for idx in index_order]
        # replaces all features with new ones
        for idx, features in enumerate(tmp):
            entry[idx] = features

    @staticmethod
    def change_data_types(entry, training_model=False):
        """Changes the data type according to the type of the feature"""

        entry[0:2] = [datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in entry[0:2]]
        entry[8:10] = [int(i) for i in entry[8:10]]
        entry[10] = round(float(entry[10]))
        entry[11:] = [int(i) for i in entry[11:]]

        if training_model == True:
            entry[7] = ast.literal_eval(entry[7])
        else:
            entry[6:8] = [i.lower() for i in entry[6:8]]

    @staticmethod
    def format_flag(entry):
        """Changes the flag feature by deleting the dots in the middle of
        the characters"""

        entry[7] = list(filter(lambda flg: flg != ".", entry[7]))

    @staticmethod
    def replace_missing_features(entry):
        """Replaces the missing features for specific values"""
        replacement = {0:"0001-01-01 01:01:01", 1:"0001-01-01 01:01:01", 2:"00:00:00:00:00:00",
                       3:"00:00:00:00:00:00", 4:"000.000.000.000", 5:"000.000.000.000", 6:"nopr",
                       7:"......", 8:"0", 9:"0", 10:"0.0", 11:"0", 12:"0"}

        for idx, feature in enumerate(entry):
            # check if the feature are empty
            if feature == '':
                entry[idx] = replacement.get(idx)


class Modifier:
    def __init__(self, flows, header):
        self.flows = flows
        self.header = header

    def modify_flows(self, execute_model=False):
        lbl_num = 2
        #self.header[0].append("lbl")
        self.header[0].extend(["flw", "lbl"])
        self.header[0][7] = "iflg"

        if execute_model == False:
            lbl_num = int(input("label number: "))
            print()

        for entry in self.flows:
            self.count_flags(entry)
            entry.append(1)
            entry.append(lbl_num)

        return self.header, self.flows

    def create_features(self):
        """Creates new features"""
        self.header[0][13:13] = ["bps", "bpp", "pps"]

        for entry in self.flows:
            # checks if the packet value isn't zero

            if entry[11] != 0:
                # bits per packet
                bpp = int(round(((8 * entry[12]) / entry[11]), 0))
            else:
                bpp = 0

            # checks if the time duration isn't zero
            if entry[10] > 0:
                # bits per second
                bps = int(round(((8 * entry[12]) / entry[10])))
                # packet per second
                pps = int(round(entry[11] / entry[10]))
            else:
                bps = 0
                pps = 0

            entry[13:13] = [bps, bpp, pps]

        return self.header, self.flows

    @staticmethod
    def count_flags(entry):
        """Counts the quantity of each TCP flags"""
        tmp = [0, 0, 0, 0, 0, 0]

        # checks if the protocol that was used is tcp
        if entry[6] == "tcp":
            tmp[0] = entry[7].count('u')
            tmp[1] = entry[7].count('a')
            tmp[2] = entry[7].count('s')
            tmp[3] = entry[7].count('f')
            tmp[4] = entry[7].count('r')
            tmp[5] = entry[7].count('p')

            entry[7] = tmp
        else:
            entry[7] = [0]

    def aggregate_flows(self, threshold=-1):
        """Aggregates the flows according to features of mac, ip and protocol"""

        # replaces sp and dp to isp and idp
        self.header[0][8] = "isp"
        self.header[0][9] = "idp"

        # aggregates the flows entries in the first occurrence
        for idx, entry in enumerate(self.flows):
            count = 1
            # checks if the entry has already been aggregated
            if entry != [None]:
                # keeps only the ports with unique numbers
                sp = {entry[8]}
                dp = {entry[9]}
                # checks if there are more occurrences in relation to the first one
                for tmp_idx, tmp_entry in enumerate(self.flows):
                    rules1 = [tmp_idx > idx, tmp_entry != [None], count < threshold]

                    if all(rules1):
                        rules2 = [entry[0].minute == tmp_entry[0].minute, entry[2:7] == tmp_entry[2:7]]
                        if all(rules2):
                            self.aggregate_features(entry, tmp_entry, sp, dp)
                            # marks the occurrences already aggregated
                            self.flows[tmp_idx] = [None]

                            count += 1
                # counts the quantity of ports with the same occurences
                entry[8] = len(sp)
                entry[9] = len(dp)
                print(entry[10])

                if not isinstance(entry[10], int):
                    entry[10] = entry[10].seconds
                else:
                    entry[10] = int(entry[10])

        # filters only the entries of aggregate flows
        self.flows = list(filter(lambda entry: entry != [None], self.flows))

        return self.header, self.flows

    @staticmethod
    def aggregate_features(entry, tmp_entry, sp, dp):
        """Aggregates the features from the first occurrence with the another
        occurrence equal"""

        entry[1] = tmp_entry[1]
        entry[7] = [x + y for x, y in zip(entry[7], tmp_entry[7])]
        sp.add(tmp_entry[8])
        dp.add(tmp_entry[9])
        entry[10] = tmp_entry[1] - entry[0]
        entry[11] += tmp_entry[11]
        entry[12] += tmp_entry[12]
        entry[13] += tmp_entry[13]


class Extractor:
    """Extracts the features and labels"""

    def __init__(self, header, flows):
        """Initializes the main variables"""
        self.header = header
        self.flows = flows

    def extract_features(self, start, end):
        """Extracts the features"""

        features = []

        for entry in self.flows:
            features.append(entry[start:end+1])

        return features

    def extract_header_features(self, start, end):
        """Extracts the features"""

        header_features = []

        for entry in self.header:
            header_features.append(entry[start:end+1])

        return header_features

    def extract_labels(self):
        """Extracts the labels"""

        labels = []

        for entry in self.flows:
            labels.append(entry[-1])

        return labels

    def preprocessing_features(self, features):
        ppa = QuantileTransformer(output_distribution='normal')
        std_features = ppa.fit_transform(features)

        return std_features

    def k_fold(self, n_splits, shuffle): #, features, labels):
        """Divides into many sets the features and labels to training and test"""
        kf = KFold(n_splits=n_splits, shuffle=shuffle)

        return kf

    def train_test_split(self, features, labels):
        dataset = train_test_split(features, labels, test_size=0.30)

        return dataset


