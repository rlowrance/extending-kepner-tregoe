# implementation of Nadan's car example
# figures are in this doc: https://docs.google.com/document/d/1qpDdSXRoTDl8URJmFxYtTHO2ixG5NDsAUfFYDg8O_YY/edit#heading=h.752jmnqq7khc

import math

def p(*x):
    "print without a trailing new line"
    print(*x, end='') # print without trailing newline

class KTDA:
    "A Kepner-Tregoe Decision Analysis table"
    def __init__(self, criteria, weights, alternatives, scores):
        self.criteria = criteria
        self.weights = weights
        self.alternatives = alternatives
        self.scores = scores

    def _weighted_score(self, alternative_index, criterion_index):
        #print("_weighted_score", alternative_index, criterion_index)
        #print(self.weights)
        #print(self.scores)
        return self.weights[criterion_index] * self.scores[alternative_index][criterion_index]

    def _total_weighted_score(self, alternative_index):
        total = 0.0
        for c in range(len(self.criteria)):
            total += self._weighted_score(alternative_index, c)
        return total

    def _print_header(self, nAlternatives):
        p('criterion         W')
        for i in range(nAlternatives): # display scores heading
            p(f'    S{i+1:1}')
        for i in range(nAlternatives): # display weighted scores heading
            p(f'     WS{i+1:1}')
        print()

    def _print_criteria_detail(self, criterion_index, nAlternatives):
        p(f'{self.criteria[criterion_index]:14}') # criterion name
        p(f'{self.weights[criterion_index]:5.2f}') # criterion weight
        for i in range(nAlternatives): # alternative scores
            p(f' {self.scores[i][criterion_index]:5.2f}')
        for i in range(nAlternatives): # alternative weighted scores
            p(f'  {self._weighted_score(i, criterion_index):6.2f}')
        print()

    def _print_weighted_totals(self,nAlternatives,nCriteria):
        p(' TOTALS             ')
        for i in range(nAlternatives):
            p('      ')
        for i in range(nAlternatives):
            p(f' {self._total_weighted_score(i):5.2f} ')
        print()

    def print(self):
        "print Kepner Tregoe decisiion analysis table to stdout"
        nAlternatives = len(self.alternatives)
        self._print_header(nAlternatives)
        nCriteria = len(self.criteria)
        for criterion_index in range(nCriteria):
            self._print_criteria_detail(criterion_index, nAlternatives)
        self._print_weighted_totals(nAlternatives,nCriteria)

    def best_alternative(self) -> int:
        "return index of best alternative"
        weighted_scores = map(lambda i: self._total_weighted_score(i), range(len(self.alternatives)))
        #print("alternatives", self.alternatives)
        #print("weighted_scores", weighted_scores)
        return argmax(tuple(weighted_scores))

    def new_normalized(self, max_score=10):
        "return an equivalent KTDA with crteria weights totaling 100 and scores in [0,1]"
        # make the weights total 100
        sum_weights = sum(self.weights)
        new_weights = tuple(map(lambda x: 100*x/sum_weights, self.weights))

        # make each score be in [0,1]
        new_scores = []
        for scores_for_alternative in self.scores:
            new_scores.append(tuple(map(lambda x: x/max_score, scores_for_alternative)))

        return KTDA(self.criteria, new_weights, self.alternatives, new_scores)

    def _closest_index(self, query_index: int) -> int:
        "return index of closest alternative that has no missing data"
        result_index = -1
        result_distance = math.inf
        query_scores = self.scores[query_index]
        for i in range(len(self.alternatives)):
            if i == query_index: 
                continue
            if has_missing(self.scores[i]):
                continue
            d = euclidean_distance(self.scores[i], query_scores)
            if d < result_distance:
                result_index = i
                result_distance = d
        return result_index

    def new_imputed_missing_scores(self, distance):
        "return new KTDA with scores imputed"
        new_scores = []
        nAlternatives = len(self.alternatives)
        for i in range(nAlternatives):
            scores_i = self.scores[i]
            if has_missing(scores_i):
                closest = list(self.scores[self._closest_index(i)])
                for k, score in enumerate(scores_i):
                    if not is_missing(score):
                        closest[k] = score
                new_scores.append(closest)
            else:
                new_scores.append(scores_i)
        return KTDA(self.criteria, self.weights, self.alternatives, new_scores)

def argmax(seq) -> int:
    "return the index of the largest element"
    return max(range(len(seq)), key=lambda i: seq[i])

def argmin(seq) -> int:
    "return the index of the smallest element"
    return min(range(len(seq)), key=lambda i: seq[i])

##########
# Figure 1
##########

fig1 = KTDA(
    ('Safety', 'Cost', 'Comfort', 'Resale Value', 'Prestige'),
    (10, 8, 5, 6, 2),
    ('Lexus RX 350', 'Audi A6', 'Toyota Prius'),
    ( # [alternative_index][criterion_index]
    (8, 7, 9, 8, 6),  # for Lexus RX 350
    (9, 3, 6, 6, 10), # for Audi A6
    (5,10, 3, 6, 2))  # for Toyota Prius
)
print('\n\nFigure 1: Original Table')
fig1.print()

##########
# Figure 2
##########

print('\n\nFigure 2: With Normalized Weights and Scores')
fig1.new_normalized().print()

##########
# Figure 3
##########

# Tables for sensitivity analysis for the criteria weights
analysis = []
for criterion_index in range(len(fig1.criteria)):
    for factor in (.9, 1.1):
        criterion_name = fig1.criteria[criterion_index]
        new_weights = list(fig1.weights)
        new_weights[criterion_index] *= factor
        new_criterion_weight = new_weights[criterion_index]
        print(f'\n\nSensitity Analysis{criterion_name} weight={new_criterion_weight:4.1f}')
        #KTDA(kt1.criteria, new_weights, kt1.alternatives, kt1.scores).print()
        next = (criterion_name,new_criterion_weight,1+fig1.best_alternative())
        analysis.append(next)
print('\n\nFigure 3. sensitivity results')
for next in analysis:
    print(next)


##########
# Figure 4
##########

dk = math.nan # don't know
fig4 = KTDA(
    fig1.criteria,
    fig1.weights,
    fig1.alternatives + tuple(['Lexus RX 460', 'Honda Civic']),
    fig1.scores + tuple([[dk, dk, 10, dk, 7],[dk, dk, dk, dk, 1]])
)
print('\n\nFigure 4: sparse data without imputations')
fig4.print()

##########
# Figure 5
##########

# represent missing values with NaN
def is_missing(x: float):
    "return true iff the value represents a missing value"
    return math.isnan(x)

def has_missing(scores: tuple):
    "return true iff at least one score is missing"
    return any(map(is_missing, scores))

def euclidean_distance(x, y):
    "treat NaN items as not known"
    sum_squared_differences = 0
    for i, xx in enumerate(x):
        if is_missing(xx):
            continue
        yy = y[i]
        if is_missing(yy):
            continue
        difference = xx - yy
        sum_squared_differences += difference * difference
    return math.sqrt(sum_squared_differences)

fig5 = fig4.new_imputed_missing_scores(euclidean_distance)
print('\n\nFigure 5: after imputation')
fig5.print()

exit()
