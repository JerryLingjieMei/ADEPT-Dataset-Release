from sklearn.metrics import roc_auc_score
import math
from dataset.human.make_pairs import CASE_PAIRS, SHAPE_CATS, get_shapes_from_cat


class ResultStorage(object):

    def __init__(self, scores, use_surprise_metric=True):
        """
        :param scores: a dict from case name to score
        """
        self.scores = scores
        for k, v in self.scores.items():
            if not isinstance(v, list):
                self.scores[k] = [v]
        self.use_surprise_metric = use_surprise_metric

    def get_relative_accuracy(self, violations=None, shape_cats=None):
        if violations is None:
            violations = list(CASE_PAIRS.keys())
        elif isinstance(violations, str):
            violations = [violations]

        if shape_cats is None:
            shape_cats = SHAPE_CATS
        elif isinstance(shape_cats, str):
            shape_cats = [shape_cats]

        n_correct = 0
        n_all = 0
        for violation in violations:
            case_index_pairs = CASE_PAIRS[violation]
            for shape_cat in shape_cats:
                shapes = get_shapes_from_cat(shape_cat)
                for shape in shapes:
                    case, index = case_index_pairs[0]
                    try:
                        n_case_correct = 0
                        n_case = 0
                        for surprise_score in self.scores["human_{}_{}_{}".format(case, shape, index)]:
                            for case, index in case_index_pairs[1:]:
                                try:
                                    for control_score in self.scores["human_{}_{}_{}".format(case, shape, index)]:
                                        n_case += 1
                                        if self.use_surprise_metric and control_score < surprise_score:
                                            n_case_correct += 1
                                        if self.use_surprise_metric and control_score == surprise_score:
                                            n_case_correct += .5
                                        if not self.use_surprise_metric and control_score > surprise_score:
                                            n_case_correct += 1
                                        if not self.use_surprise_metric and control_score == surprise_score:
                                            n_case_correct += .5
                                except KeyError:
                                    pass
                        if n_case != 0:
                            n_all += 1
                            n_correct += n_case_correct / n_case
                    except KeyError:
                        pass
        return n_correct / n_all if n_all > 0 else math.nan

    def get_absolute_accuracy(self, violations=None, shape_cats=None):
        if violations is None:
            violations = list(CASE_PAIRS.keys())
        elif isinstance(violations, str):
            violations = [violations]

        if shape_cats is None:
            shape_cats = SHAPE_CATS
        elif isinstance(shape_cats, str):
            shape_cats = [shape_cats]

        labels = []
        scores = []

        for violation in violations:
            case_index_pairs = CASE_PAIRS[violation]
            for shape_cat in shape_cats:
                shapes = get_shapes_from_cat(shape_cat)
                for shape in shapes:
                    case, index = case_index_pairs[0]
                    try:
                        for surprise_score in self.scores["human_{}_{}_{}".format(case, shape, index)]:
                            if math.isinf(surprise_score):
                                surprise_score = 1000
                            labels.append(0)
                            scores.append(-surprise_score if self.use_surprise_metric else surprise_score)
                            for case, index in case_index_pairs[1:]:
                                try:
                                    for control_score in self.scores["human_{}_{}_{}".format(case, shape, index)]:
                                        if math.isinf(control_score):
                                            control_score = 1000
                                        labels.append(1)
                                        scores.append(-control_score if self.use_surprise_metric else control_score)
                                except KeyError:
                                    pass
                    except KeyError:
                        pass

        try:
            result = roc_auc_score(labels, scores)
        except ValueError:
            result = math.nan

        return result
