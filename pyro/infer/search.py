from six.moves.queue import Queue

import pyro.poutine as poutine
from pyro.infer import TracePosterior


class Search(TracePosterior):
    """
    :param model: probabilistic model defined as a function
    :param max_tries: the maximum number of times to try completing a trace from the queue.
    :type max_tries: int

    New Trace and Poutine-based implementation of systematic search
    """
    def __init__(self, model, max_tries=1e6):
        """
        Constructor. Default max_tries to something sensible - 1e6.
        """
        self.model = model
        self.max_tries = int(max_tries)

    def _traces(self, *args, **kwargs):
        """
        algorithm entered here
        Returns traces from the posterior
        Running until the queue is empty and collecting the marginal histogram
        is performing exact inference
        """
        # currently only using the standard library queue
        self.queue = Queue()
        self.queue.put(poutine.Trace())

        p = poutine.trace(
            poutine.queue(self.model, queue=self.queue, max_tries=self.max_tries))
        while not self.queue.empty():
            tr = p.get_trace(*args, **kwargs)
            yield (tr, tr.log_pdf())

    def log_z(self, *args, **kwargs):
        """
        harmonic mean log-evidence estimator
        """
        log_z = 0.0
        n = 0
        # TODO parallelize
        for _, log_weight in self._traces(*args, **kwargs):
            n += 1
            log_z = log_z + log_weight
        return log_z / n
