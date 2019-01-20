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


def contact(u_i, u_j, data, delta):
    contacts = []
    ds, dt = delta
    for t0 in data.trajectories(u_i):
        for t1 in data.trajectories(u_j):
            tdelta = Trajectory(abs(t0-t1))
            if tdelta.t <= dt:
                if tdelta.lon <= ds and tdelta.lat <= ds:
                    print('{} {} {} {} {}'.format(u_i, u_j, tdelta, Trajectory(t0), Trajectory(t1)))
                    cp = ContactPoint(Trajectory(t0), Trajectory(t1))
                    contacts.append(cp)
    return contacts


def contact_combos(data, delta):
    combos = set()
    users = data.users()
    user_combos = combinations(users, 2)
    for i, j in user_combos:
        contacts = contact(i, j, data, delta)
        for c in contacts:
            combos.add((i, j, c.lat, c.lon, c.t))
    return combos


def main():
    data = GeolifeTrajectories().load()
    d0 = [100, 300]
    d1 = [500, 600]
    d2 = [1000, 1200]

    for d in [d0, d1, d2]:
        combos = contact_combos(data, d)
        print(d)
        for c in combos:
            print(c)
        print('\n\n\n')


if __name__ == "__main__":
    main()
