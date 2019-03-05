import math

from app.lib.pipeline_ops import PipelineOp


class TemplateOp(PipelineOp):
    def __init__(self, x, y):
        PipelineOp.__init__(self)
        self.x = x
        self.y = y

    def perform(self):
        result = {
            'x': self.x,
            'y': self.y,
            'distance': self.distance_between()
        }

        return self._apply_output(result)

    def distance_between(self):
        return math.sqrt(self.x**2 + self.y**2)
