import numpy as np
from itertools import combinations

from app.lib.datasets import GeolifeTrajectories


class Trajectory:
    def __init__(self, t):
        self.lat = t[0]
        self.lon = t[1]
        self.alt = t[3]
        self.t = t[4]

    def __str__(self):
        return '[lat: {}  lon: {}  alt: {}  time: {}]'.format(self.lat, self.lon, self.alt, self.t)


class ContactPoint(Trajectory):
    def __init__(self, t1, t2):
        Trajectory.__init__(self, [0, 0, 0, 0, 0])
        self.lat = np.mean([t1.lat, t2.lat])
        self.lon = np.mean([t1.lon, t2.lon])
        self.t = np.mean([t1.t, t2.t])


def contact(T0, T1, delta=(-1, -1)):
    contacts = []
    ds, dt = delta
    for i in range(len(T0)):
        for j in range(len(T1)):
            t0 = T0[i]
            t1 = T1[j]
            tdelta = Trajectory(abs(t0-t1))
            if dt < 0 or tdelta.t <= dt:
                if ds < 0 or (tdelta.lon <= ds and tdelta.lat <= ds):
                    cp = ContactPoint(Trajectory(t0), Trajectory(t1))
                    contacts.append(cp)
    return contacts


def contact_combos(user_trajectories, delta):
    combos = set()
    d = user_trajectories
    keys = np.asarray(list(d.keys()))
    combo_keys = combinations(keys, 2)
    for i, j in combo_keys:
        contacts = contact(user_trajectories[i], user_trajectories[j], delta)
        for c in contacts:
            combos.add((i, j, c.lat, c.lon, c.t))
    return combos


def main():
    user_trajectories = GeolifeTrajectories().load()
    d0 = [100, 300]
    d1 = [500, 600]
    d2 = [1000, 1200]

    for d in [d0, d1, d2]:
        # contacts = contact(np.array([[1, 3, 0]]), np.array([[2, 4, 0]]), d)
        combos = contact_combos(user_trajectories, d)
        print(d)
        for c in combos:
            print(c)
        print('\n\n\n')


if __name__ == "__main__":
    main()
