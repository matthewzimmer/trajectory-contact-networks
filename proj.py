#Francisco Cancedda ICSI 431 HW2 Petko
import numpy as np
import pprint as pp
class Trajectory:
	def __init__(self, t):
		self.lat = t[0]
		self.lon = t[1]
		self.t = t[2]


class ContactPoint:
	def __init__(self, trajectory1, trajectory2):
		self.lat = (trajectory1.lat + trajectory2.lat)/2
		self.lon = (trajectory1.lon + trajectory2.lon)/2
		self.t = (trajectory1.t + trajectory2.t)/2
	def __str__(self):
		s = []
		s.append('lat : {}'.format(self.lat))
		s.append('lon : {}'.format(self.lon))
		s.append('time : {}'.format(self.t))
		return '\n'.join(s)



def contact(T0, T1, delta):
	T =  abs(T0 - T1)
	contacts = []
	ds, dt = delta
	print(T)
	for i in range((len(T))):
		trajectory = Trajectory(T[i])
		if trajectory.lon <= ds and trajectory.lat <= ds:
			if trajectory.t <= dt:
				contacts.append(ContactPoint(Trajectory(T0[i]),Trajectory(T1[i])))
	return contacts

def main():
	# t0 = np.array([Trajectory(x) for x in ])
	# t1 = np.array([Trajectory(x) for x in ])
	d =  np.array([1,1])
	# pp.pprint(contact(np.array([[1,3,0]]),np.array([[2,4,0]]),d)[0])
	contacts = contact(np.array([[1,3,0]]),np.array([[2,4,0]]),d)
	for c in contacts:
		print(c)

if __name__=="__main__":
    main()
