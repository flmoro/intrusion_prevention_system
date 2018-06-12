import os
from model import Gatherer
from model import Formatter
from model import Modifier
from model import Extractor
from model import Detector
from view import print_flows, export_flows, evaluation_metrics, scatter_plot

print("anomaly detector")
print("1 - build dataset")
print("2 - training the model")
print("3 - execute the model")
print("4 - stop", end="\n\n")

option = int(input("choose an option: "))
print()

pcap_path = "/home/flmoro/research_project/dataset/pcap/"
nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
csv_path = "/home/flmoro/research_project/dataset/csv/"
file_name = ["", "", ""]
ml_models = []

while option != 4:

    if option == 1:

        print("building the dataset", end="\n\n")
        print("1 - split pcap")
        print("2 - convert pcap to nfcapd")
        print("3 - convert nfcapd to flows")
        print("4 - format and modify the flows")
        print("5 - clean nfcapd files")
        print("6 - merge flows files")
        print("7 - back to main", end="\n\n")

        option = int(input("choose an option: "))
        print()

        gt = Gatherer(pcap_path, nfcapd_path, csv_path)
        while option != 7:
            if option == 1:
                print("splitting file", end="\n\n")
                gt.split_pcap(int(input("split size: ")))
                print("split file", end="\n\n")

            elif option == 2:
                print("converting pcap to nfcapd", end="\n\n")
                wtime = input("window time: ")
                file_name[0] = wtime

                gt.convert_pcap_nfcapd(int(wtime))
                print("converted pcap files", end="\n\n")

            elif option == 3:
                print("converting nfcapd to flows")
                file_name[2] = gt.convert_nfcapd_csv()
                print("converted nfcapd files", end="\n\n")

            elif option == 4:
                print("opening, format and modify the file", end="\n\n")
                sample = input("csv sample: ")
                file_name[1] = sample

                flows = gt.open_csv(sample=int(sample))

                ft = Formatter(flows)
                header, flows = ft.format_flows()

                md = Modifier(flows, header)
                header, flows = md.modify_flows()
                print_flows(flows, header, 5)
                export_flows(flows, csv_path + "flows/", "flows_w" + file_name[0] + "_s" + file_name[1] + "_"
                             + file_name[2], header)

                print("completed file", end="\n\n")
            elif option == 5:
                print("cleaning nfcapd files", end="\n\n")
                gt.clean_nfcapd_files()
                print("completed cleaning", end="\n\n")
            elif option == 6:
                print("merging flows", end="\n\n")
                dataset_name = input("dataset name: ") + ".csv"
                print()

                flows = gt.open_csv()

                if not os.path.exists(csv_path + dataset_name):
                    export_flows([flows[0]], csv_path, dataset_name, mode='a')
                export_flows(flows[1:], csv_path, dataset_name, mode='a')

                print("merged flows", end="\n\n")
            elif option == 7:
                exit()
            else:
                print("Invalid option")

            print("building the dataset", end="\n\n")
            print("1 - split pcap")
            print("2 - convert pcap to nfcapd")
            print("3 - convert nfcapd to flows")
            print("4 - format and modify the flows")
            print("5 - clean nfcapd files")
            print("6 - merge flows files")
            print("7 - back to main", end="\n\n")

            option = int(input("choose an option: "))
            print()

        print("dataset built", end="\n\n")

    elif option == 2:
        print("training the model")
        try:
            gt = Gatherer(csv_path=csv_path)
            flows = gt.open_csv()

            ft = Formatter(flows)
            flows = ft.format_flows(train_model=True)[1]

            """scatter_plot(flows, 10, 11, 'td', 'ipkt', 'time duration x input packets')
            scatter_plot(flows, 10, 15, 'td', 'pps', 'time duration x packets per second')
            scatter_plot(flows, 10, 12, 'td', 'ibyt', 'time duration x input bytes')
            scatter_plot(flows, 10, 13, 'td', 'bps', 'time duration x bits per second')
            scatter_plot(flows, 11, 12, 'ipkt', 'ibyt', 'input packets x input bytes')
            scatter_plot(flows, 15, 13, 'pps', 'bps', 'packets per second x bits per second')
            scatter_plot(flows, 11, 15, 'ipkt', 'pps', 'input packets x packets per second')
            scatter_plot(flows, 12, 13, 'ibyt', 'bps', 'input packets x bits per second')"""

            ex = Extractor(flows)
            dataset = ex.kfold(int(input("split data in: ")), True)
            print()

            dt = Detector()

            num = 1
            for training_features, test_features, training_labels, test_labels in dataset:
                print("Test ", num)

                pred = dt.execute_classifiers(training_features, test_features, training_labels)

                evaluation_metrics(pred[0], test_labels, "decision tree")
                evaluation_metrics(pred[1], test_labels, "support vector machine")
                scatter_plot(pred[2], 0, 1, title="pca")

                num += 1

            ml_models.extend(dt.get_ma_models())

            option = int(input("proceed or stop training the model: "))
            print()
        except ValueError as error:
            print(error, end="\n\n")

        print("model finished", end="\n\n")

    elif option == 3:
        pass

    elif option == 4:
        exit()
    else:
        print("Invalid option")

    print("anomaly detector")
    print("1 - build dataset")
    print("2 - training the model")
    print("3 - execute the model")
    print("4 - stop", end="\n\n")

    option = int(input("choose an option: "))
    print()