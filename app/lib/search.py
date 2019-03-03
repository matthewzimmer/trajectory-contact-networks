import math

from app.lib.pipeline_ops import PipelineOp


class FindNeedleOp(PipelineOp):
    def __init__(self, haystack, needle):
        PipelineOp.__init__(self)
        self.needle = needle
        self.haystack = haystack

    def perform(self):
        return self._apply_output(self.find_needle(0, len(self.haystack) - 1))

    def find_needle(self, p, r):
        n = (r - p) + 1
        if n == 1:
            if self.haystack[p] == self.needle:
                return p
        else:
            m = math.floor((r - p) / 2)
            l = self.find_needle(p, p + m)
            if l >= 0:
                return l
            r = self.find_needle(p + m + 1, r)
            if r >= 0:
                return r
        return -1
