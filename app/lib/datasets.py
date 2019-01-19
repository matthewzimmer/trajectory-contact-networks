import glob
import os
import numpy as np

from app.lib.pipeline_ops import PipelineOp


class GeolifeTrajectories(PipelineOp):
    def __init__(self):
        PipelineOp.__init__(self)
        self.__trajectories = {}

    def load(self):
        return self.perform().output()

    def perform(self):
        return self._apply_output(self.trajectories())

    def trajectories(self):
        return self.__load_trajectories()

    def __load_trajectories(self):
        trajectories = self.__trajectories
        if len(trajectories) <= 0:
            user_ids = os.listdir('app/data/geolife/Data')
            for uid in user_ids:
                plt_files = glob.glob('app/data/geolife/Data/{}/Trajectory/*.plt'.format(uid))
                for filepath in plt_files:
                    user_trajectories = np.loadtxt(filepath, delimiter=',', skiprows=6, usecols=range(0, 5),
                                                   converters={4: lambda d: float(d)})
                    trajectories[uid] = user_trajectories
                if len(trajectories) is 2:
                    break
            self.__trajectories = trajectories
        return trajectories
