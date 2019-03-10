from itertools import combinations

from app.lib.data_serializer import DataSerializer
from app.lib.datasets import GeolifeData
from app.lib.graph import grapher, save_results
from app.lib.ops.tiles import GraphContactPointsOp, GenerateTilesOp
from app.lib.points import TrajectoryPoint, ContactPoint


def detect_contact_points(user_i, user_j, data, delta):
    ds, dt = delta
    contact_points = load_contact_points(ds, dt)
    if contact_points is None:
        contact_points = []
    total_count = 0
    for traj_plt_i in data.load_user_trajectory_plts(user_i):
        for traj_plt_j in data.load_user_trajectory_plts(user_j):
            pnt_i_count = 0
            next_j_plt = False
            for pnt_i in data.load_trajectory_plt_points(traj_plt_i):
                if next_j_plt:
                    break

                pnt_i = TrajectoryPoint(pnt_i, user_i)
                pnt_i_count = pnt_i_count + 1
                pnt_j_count = 0
                for pnt_j in data.load_trajectory_plt_points(traj_plt_j):
                    pnt_j = TrajectoryPoint(pnt_j, user_j)
                    pnt_j_count = pnt_j_count + 1
                    total_count = total_count + 1

                    tdelta = abs(pnt_i.t - pnt_j.t)
                    cp = ContactPoint(pnt_i, pnt_j, traj_plt_i, traj_plt_j)
                    if tdelta <= dt and cp.dist_apart() <= ds:
                        print(
                            'CONTACT:  t: {}    dist: {}    ui: {}    uj: {}    tot: {}    plt_i: {}    plt_j: {}'.format(
                                tdelta,
                                cp.dist_apart(),
                                user_i,
                                user_j,
                                total_count,
                                traj_plt_i,
                                traj_plt_j))
                        contact_points.append(cp)
                        save_contact_points(ds, dt, contact_points)
                    else:
                        if pnt_j_count == 1:
                            # The first point in user j's trajectory is not within dt seconds so we
                            # signal to move to the next trajectory for user j.
                            next_j_plt = True
                            break  # Move to the next PLT for user j
    return contact_points


def detect_contact(user_i, user_j, data, delta):
    ds, dt = delta
    contacts = load_contacts(ds, dt)
    if contacts is None:
        contacts = []
    total_count = 0
    for traj_plt_i in data.load_user_trajectory_plts(user_i):
        for traj_plt_j in data.load_user_trajectory_plts(user_j):
            pnt_i_count = 0
            next_j_plt = False
            for pnt_i in data.load_trajectory_plt_points(traj_plt_i):
                if next_j_plt:
                    break

                pnt_i = TrajectoryPoint(pnt_i, user_i)
                pnt_i_count = pnt_i_count + 1
                pnt_j_count = 0
                for pnt_j in data.load_trajectory_plt_points(traj_plt_j):
                    pnt_j = TrajectoryPoint(pnt_j, user_j)
                    pnt_j_count = pnt_j_count + 1
                    total_count = total_count + 1

                    tdelta = abs(pnt_i.t - pnt_j.t)
                    cp = ContactPoint(pnt_i, pnt_j, traj_plt_i, traj_plt_j)
                    if tdelta <= dt and cp.dist_apart() <= ds:
                        print(
                            'CONTACT:  t: {}    dist: {}    ui: {}    uj: {}    tot: {}    plt_i: {}    plt_j: {}'.format(
                                tdelta,
                                cp.dist_apart(),
                                user_i,
                                user_j,
                                total_count,
                                traj_plt_i,
                                traj_plt_j))
                        contacts.append(cp)

                        save_contacts(ds, dt, contacts)
                        return [cp]
                    else:
                        if pnt_j_count == 1:
                            # The first point in user j's trajectory is not within dt seconds so we
                            # signal to move to the next trajectory for user j.
                            next_j_plt = True
                            break  # Move to the next PLT for user j
    return []


def save_contacts(ds, dt, contacts):
    DataSerializer.save_data({'ds': ds, 'dt': dt, 'total': len(contacts), 'contacts': contacts},
                             'app/data/contacts/Contacts_ds{}_dt{}.pickle'.format(ds, dt))


def save_contact_points(ds, dt, contact_points):
    DataSerializer.save_data({'ds': ds, 'dt': dt, 'total': len(contact_points), 'contact_points': contact_points},
                             'app/data/contacts/ContactPoints_ds{}_dt{}.pickle'.format(ds, dt))


def load_contact_points(ds, dt):
    return DataSerializer.reload_data('app/data/contacts/ContactPoints_ds{}_dt{}.pickle'.format(ds, dt))


def load_contacts(ds, dt):
    return DataSerializer.reload_data('app/data/contacts/Contacts_ds{}_dt{}.pickle'.format(ds, dt))


def contact_point_combos(data, delta):
    combos = set()
    users = data.users()
    user_combos = combinations(users, 2)
    for i, j in user_combos:
        contact_points = detect_contact_points(i, j, data, delta)
        for c in contact_points:
            combos.add(c)
    return combos


def contact_combos(data, delta):
    combos = set()
    users = data.users()
    user_combos = combinations(users, 2)
    for i, j in user_combos:
        contacts = detect_contact(i, j, data, delta)
        for c in contacts:
            combos.add(c)
    return combos


def generate_contacts(data, deltas):
    ignore_cache = False
    for d in deltas:
        ds, dt = d
        contact_data = load_contacts(ds, dt)
        if ignore_cache or contact_data is None:
            contacts = contact_combos(data, d)
        else:
            contacts = contact_data['contacts']
            total = contact_data['total']
            print('Loaded {} pickled contacts for ds={}, dt={}\n\n'.format(total, ds, dt))
        for c in contacts:
            print(c)
        print('\n\n\n')


def generate_contact_points(data, deltas):
    ignore_cache = False
    for d in deltas:
        ds, dt = d
        contact_point_data = load_contact_points(ds, dt)
        if ignore_cache or contact_point_data is None:
            contact_points = contact_point_combos(data, d)
        else:
            contact_points = contact_point_data['contacts']
            total = contact_point_data['total']
            print('Loaded {} pickled contact points for ds={}, dt={}\n\n'.format(total, ds, dt))
        for cp in contact_points:
            print(cp)
        print('\n\n\n')


def generate_graph(data, deltas):
    largest_comps, avg_degrees = [], []
    results_delta = []
    for d in deltas:
        ds, dt = d
        contact_data = load_contacts(ds, dt)
        contacts = []
        if contact_data:
            contacts = contact_data['contacts']
            total = contact_data['total']
            print('Loaded {} pickled contacts for ds={}, dt={}\n\n'.format(total, ds, dt))

            contacts = list(map(lambda c: c.tuplize(), contacts))
        else:
            contacts = [
                ('003', '004', 40.007548, 116.32172650000001, 1224785351.0000029),
                ('002', '005', 45.007548, 16.32172650000001, 14785351.0000029),
                ('002', '001', 45.007548, 16.32172650000001, 14785351.0000029)
            ]
        largest_component, avg_degree = grapher(contacts)
        largest_comps.append(largest_component)
        avg_degrees.append(avg_degree)
        results_delta.append('{}m {}s'.format(ds, dt))
    save_results(largest_comps, avg_degrees, results_delta)


def main():
    data = GeolifeData().output()

    # [ds, dt] ==> [meters from each other,  seconds apart]
    deltas = [[100, 300], [500, 600], [1000, 1200]]

    # generate_contact_points(data, deltas)
    # generate_contacts(data, deltas)
    generate_graph(data, deltas)


if __name__ == "__main__":
    main()
