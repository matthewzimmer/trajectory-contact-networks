import glob
import os
import re

import numpy as np

from app.lib.pipeline_ops import PipelineOp


class GeolifeTrajectories(PipelineOp):
    def __init__(self):
        PipelineOp.__init__(self)
        self.__users = []
        self.__trajectories = {}

    def load(self):
        return self.perform()

    def perform(self):
        self.__load_trajectories()
        return self._apply_output({'users': self.users(), 'trajectories': self.trajectories()})

    def users(self):
        return self.__users

    def trajectories(self, uid=None):
        self.__load_trajectories()
        if uid is None:
            return self.__trajectories
        else:
            return self.__load_user_trajectories(uid)

    def __load_trajectories(self):
        trajectories = self.__trajectories
        if len(trajectories) <= 0:
            self.__users = np.sort(np.array([uid for uid in os.listdir('app/data/geolife/Data') if re.findall('\d{3}', uid)]))
            for uid in self.__users:
                trajectories[uid] = trajectories.get(uid, self.__load_user_trajectories(uid))
            self.__trajectories = trajectories
        return trajectories

    def __load_user_trajectories(self, uid):
        trajectories = []
        plt_files = glob.glob('app/data/geolife/Data/{}/Trajectory/*.plt'.format(uid))
        for filepath in plt_files:
            user_trajectories = np.loadtxt(filepath, delimiter=',', skiprows=6, usecols=range(0, 5),
                                           converters={4: lambda d: float(d)})
            for t in user_trajectories:
                trajectories.append(t)
        trajectories = np.array(trajectories)[0:2]
        for t in trajectories:
            yield t
