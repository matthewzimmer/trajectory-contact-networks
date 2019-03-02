# Contact Network from Trajectories

### Build Status

[![Build Status](https://travis-ci.com/matthewzimmer/trajectory-contact-networks.svg?branch=master)](Build Status)

### Python Environments
By default, when you create an environment named `venv` in the project root directory, 
most .gitignore templates ignore this directory. 

We will take advantage of this convenience for this project.
```
// CREATE
$ python3 -m venv venv

// ACTIVATE
$ source venv/bin/activate

// CLOSE
$ deactivate
```

Check out codeenvy online c virtual environment.


# Instructions

The goal of this task is to process GPS trajectory data with time information, 
create contact networks from it and summarize properties of these networks.

### 1 From trajectories to networks
#### 1.1 Trajectories and their intersection

A trajectory `T = {(lat0, lon0, t0), (lat1, lon1, t1) ... }` is a sequence of position
triplets denoting the latitude (lat), longitude (lon) and time (t) of a moving
object. This object may be a moving vehicle, pedestrian or any other moving
object in 2D. The goal in this part is to identify when two moving objects come
into contact, based on co-location threshold parameters `d = (ds, dt)`, where the
meaning of these two parameters is: the two objects form a contact if they are
within `ds` meters from each other at times that are at most `dt` seconds apart.

#### 1.2 Pairwise trajectory intersection

Implement (in a language of your choice) a function that takes as an input two
trajectories: `T0` and `T1` and threshold parameters `d` and outputs a sequence
of contacts in the form of `C = {(lat0, lon0, t0), (lat1, lon1, t1) ...}`, where each
contact point contains the average coordinates and times of the corresponding
locations of the two moving objects.

What is the asymptotic _O()_ complexity of your solution if the sizes of the
compared trajectories are both _n_?


#### 1.3 Multiple trajectories from multiple users

Implement a function that takes trajectories from _m_ users (each user may have
potentially multiple associated trajectories) and computes contact points from
all pairings of trajectories from dierent users in the form:
`C = {(ui, uj, lat0, lon0, t0) ...}` (The format is the same as the above, only the
user ids are included for each contact).

* What would be the overall complexity of this function assuming each user
has _k_ trajectories each of size _n_? Discuss how you arrive to the answer provided.

* Can you improve your implementation based on the threshold parameter
`d = (ds; dt)`? If yes, do not implement it, only discuss and provide pseudo
code. Also discuss what would be the change in asymptotic complexity if any
(Note: practical improvements may be possible without guaranteed asymptotic
changes.)


#### 1.4 A contact network

Assuming a set of contact points `C` reported in the previous task, construct a
contact graph `G(V, E)` with vertices `V` the users and edges among users if the
two users were in contact at least once. Provide functions to compute the size
of the largest connected component in the network and the average degree of
nodes. Choose the data structures of your graph representation accordingly.


### 2 Real-World Data
#### 2.1 Data import

To test your implementation, you will use the Geolife dataset (Download from
here: https://www.microsoft.com/en-us/download/details.aspx?id=52367). It
contains trajectories for users in China (multiple trajectories per user). Get
familiar with the included data le to understand how the data is organized.
Write a data parser to be able to load the trajectories in your program.


#### 2.2 Analysis

Consider all trajectories for the first 20 users (folders `000` through `019`) and
compute the contact network for three settings of the co-location parameters:
`d0 = (100m, 300s)`, `d1 = (500m, 600s)` and `d2 = (1000m, 1200s)`. Compute the
corresponding sizes of the largest connected component and average degrees and
plot them in two figures, where on the x axis you have the settings of 0, 1 and
2 and on the y axis you have the corresponding values of the largest connected
component or average degree. Also record and report the time that it takes to
compute the above for each of the settings.

Discuss your observations: 

* Why do you observe the behavior you observe?
* What do your need to do if you want to increase the average degree? 
* What additional observations can you make?


