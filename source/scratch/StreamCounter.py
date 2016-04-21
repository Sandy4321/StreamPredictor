class StreamCounter:
    """
    Used to analyze few variables of Pop Manager.
    """

    def __init__(self):
        self.time = []
        self.pop_count = []
        self.prediction_gain = []

    def update(self, time, popcount, prediction_gain):
        self.time.append(time)
        self.pop_count.append(popcount)
        self.prediction_gain.append(prediction_gain)

