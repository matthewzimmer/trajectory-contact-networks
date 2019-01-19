import numpy as np

from app.lib.datasets import GeolifeTrajectories

class Trajectory:
    def __init__(self, t):
        self.lat = t[0]
        self.lon = t[1]
        self.t = t[2]

    def __str__(self):
        return '[lat: {}  lon: {}  time: {}]'.format(self.lat, self.lon, self.t)


class ContactPoint(Trajectory):
    def __init__(self, t1, t2):
        self.lat = np.mean([t1.lat, t2.lat])
        self.lon = np.mean([t1.lon, t2.lon])
        self.t = np.mean([t1.t, t2.t])


def contact(T0, T1, delta):
    T = abs(T0 - T1)
    contacts = []
    ds, dt = delta
    for i in range(len(T)):
        trajectory = Trajectory(T[i])
        if trajectory.lon <= ds and trajectory.lat <= ds:
            if trajectory.t <= dt:
                contacts.append(ContactPoint(Trajectory(T0[i]), Trajectory(T1[i])))
    return contacts

def contact_combos(user_trajectories):
	contact_points = []
	for i in user_trajectories:
		for j in user_trajectories:
			contact_points.append(contact(i,j,delta))
            
def main():
    user_trajectories = GeolifeTrajectories().load()

    # t0 = np.array([Trajectory(x) for x in ])
    # t1 = np.array([Trajectory(x) for x in ])
    d = np.array([1, 1])
    # pp.pprint(contact(np.array([[1,3,0]]),np.array([[2,4,0]]),d)[0])
    contacts = contact(np.array([[1, 3, 0]]), np.array([[2, 4, 0]]), d)
    for c in contacts:
        print(c)


if __name__ == "__main__":
    main()
