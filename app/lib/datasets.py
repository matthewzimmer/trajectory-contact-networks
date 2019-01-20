import datetime
import glob
import os
import re

import numpy as np
import pytz

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

    @staticmethod
    def __load_user_trajectories(uid):
        plt_files = np.sort(glob.glob('app/data/geolife/Data/{}/Trajectory/*.plt'.format(uid)))
        for filepath in plt_files:
            user_trajectories = np.genfromtxt(filepath, delimiter=',', dtype=float, skip_header=6, usecols=range(0, 5), converters={4: lambda days: (float(days) * 24 * 60 * 60 )})
            # (datetime.datetime(1899, 12, 30, tzinfo=pytz.utc) + datetime.timedelta(days=float(days))).timestamp()})
            for t in user_trajectories:
                yield t
