import argparse
import json
import os
import csv
from collections import defaultdict

from dataset.human.result_storage import ResultStorage, CASE_PAIRS, SHAPE_CATS, get_shapes_from_cat
from utils.io import read_serialized
from utils.constants import CONTENT_FOLDER

_prefix = "| negative log likelihood: "

_human_pairs = read_serialized(os.path.join(CONTENT_FOLDER, "dataset", "human", "pairs.json"))["origin"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary_folder", type=str)
    parser.add_argument("--summary_folders", type=str, nargs="+")
    parser.add_argument("--summary_file", type=str)
    parser.add_argument("--violations", type=str)
    parser.add_argument("--shape_cats", type=str)
    parser.add_argument("--use_surprise_metric", type=int, default=True)
    parser.add_argument("--output_folder", type=str)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    max_scores = {}
    if args.summary_folder is not None:
        for file_name in os.listdir(args.summary_folder):
            if file_name.endswith(".txt"):
                with open(os.path.join(args.summary_folder, file_name)) as f:
                    s = f.readline()
                    s = s[len(_prefix):]
                    max_score = json.loads(s.replace("\'", "\""))["max"]
                max_scores[file_name[:-4]] = max_score
        if args.summary_folder.endswith("/"):
            experiment = os.path.split(args.summary_folder[:-1])[-1]
        else:
            experiment = os.path.split(args.summary_folder)[-1]
        if args.output_folder is None:
            args.output_folder = os.path.join(args.summary_folder, "results")
    elif args.summary_folders is not None:
        max_scores = defaultdict(list)
        for args.summary_folder in args.summary_folders:
            for file_name in os.listdir(args.summary_folder):
                if file_name.endswith(".txt"):
                    with open(os.path.join(args.summary_folder, file_name)) as f:
                        s = f.readline()
                        s = s[len(_prefix):]
                        max_score = json.loads(s.replace("\'", "\""))["max"]
                    max_scores[file_name[:-4]].append(max_score)
        if args.summary_folder.endswith("/"):
            experiment = os.path.split(args.summary_folder[:-1])[-1]
        else:
            experiment = os.path.split(args.summary_folder)[-1]
        if args.output_folder is None:
            args.output_folder = os.path.join(args.summary_folders[0], "results")
    elif args.summary_file is not None:
        max_scores = read_serialized(args.summary_file)
        experiment = os.path.split(args.summary_file)[-1][:-5]
    else:
        raise FileNotFoundError("Should specific summary folder / file")

    with open("{}{}_absolute.csv".format(
            args.output_folder, experiment), "w")as f_absolute, open(
        "{}/{}_relative.csv".format(
            args.output_folder, experiment), "w")as f_relative:

        absolute_writer = csv.DictWriter(f_absolute, fieldnames=["name", "all", *CASE_PAIRS],
                                         dialect="excel-tab")
        relative_writer = csv.DictWriter(f_relative, fieldnames=["name", "all", *CASE_PAIRS],
                                         dialect="excel-tab")

        absolute_writer.writeheader()
        relative_writer.writeheader()

        for i in range(2):
            if i == 1:
                scores = {k: v for k, v in max_scores.items() if k in _human_pairs}
                experiment = experiment + "_on-human"
            else:
                scores = max_scores
            max_storage = ResultStorage(scores, use_surprise_metric=args.use_surprise_metric)

            absolute_score = dict(all=max_storage.get_absolute_accuracy())
            for case in CASE_PAIRS:
                absolute_score[case] = max_storage.get_absolute_accuracy(violations=case)
            absolute_writer.writerow(dict(name=experiment, **absolute_score))
            for shape in SHAPE_CATS:
                absolute_score = dict(all=max_storage.get_absolute_accuracy(shape_cats=shape))
                for case in CASE_PAIRS:
                    absolute_score[case] = max_storage.get_absolute_accuracy(violations=case, shape_cats=shape)
                absolute_writer.writerow(dict(name=experiment + "_" + shape, **absolute_score))

            relative_score = dict(all=max_storage.get_relative_accuracy())
            for case in CASE_PAIRS:
                relative_score[case] = max_storage.get_relative_accuracy(violations=case)
            relative_writer.writerow(dict(name=experiment, **relative_score))
            for shape in SHAPE_CATS:
                relative_score = dict(all=max_storage.get_relative_accuracy(shape_cats=shape))
                for case in CASE_PAIRS:
                    relative_score[case] = max_storage.get_relative_accuracy(violations=case, shape_cats=shape)
                relative_writer.writerow(dict(name=experiment + "_" + shape, **relative_score))
