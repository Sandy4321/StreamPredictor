def combine_normalize_distribution(distributions, weights):
    """
    Combines multiple distribution into one according to weights, normalizing everything.

    :type distributions: list[dict[str,float]]
    :type weights: list[float]
    :rtype: dict[str,float]
    """
    words_list = []
    for distribution in distributions:
        words_list.extend(distribution.keys())
    vocabulary = set(words_list)
    final_distribution = dict((i, 0.0) for i in vocabulary)
    for word in vocabulary:
        final_distribution[word] = float(sum([(d[word] * w if word in d else 0)
                                              for d, w in zip(distributions, weights)]))
    sum_of_weights = sum(final_distribution.values())
    for word in vocabulary:
        final_distribution[word] /= sum_of_weights
    return final_distribution
