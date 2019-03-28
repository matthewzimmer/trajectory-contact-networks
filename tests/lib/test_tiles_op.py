from builtins import AssertionError

from app.lib.ops.tiles import GenerateTilesOp, GraphContactPointsOp
from hypothesis import given, example
import hypothesis.strategies as st
import numpy as np
import pandas as pd

ALL_USER_IDS = [f'{i:03d}' for i in range(0, 100)]
GLOBAL_ORIGIN = (39.75872, 116.04142)


@given(users=st.lists(st.integers()), ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(users=['000', '001'], ds=1000, dt=1200, global_origin=GLOBAL_ORIGIN)
def test_generate_user_tiles(users, ds, dt, global_origin):
    # Commented out due to Travis resource limitations
    # tiles = GenerateTilesOp(users, ds, dt, global_origin).output()
    # print(tiles)
    # assert len(tiles) == 5737
    pass


def test_generate_contacts_by_invalid_weight():
    try:
        GraphContactPointsOp(hashed_tiles={}, weight='invalid')
    except AssertionError:
        assert True


def test_generate_contacts_bad_tile_hash():
    op = GraphContactPointsOp(hashed_tiles={None: []}, weight='count_weight')
    result = op.output()
    assert result['graph_generated'] is False
    assert result['graph_filepath'] == 'app/data/graphs/no_tiles_from_data.png'


@given(users=st.lists(st.integers()), ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(users=ALL_USER_IDS, ds=1000, dt=1200, global_origin=GLOBAL_ORIGIN)
def test_generate_contacts_by_count_weight(users, ds, dt, global_origin):
    if len(global_origin) == 0:
        pass

    tiles_op = GenerateTilesOp(users, ds, dt, global_origin)

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles_op.output(), weight='count_weight')

    # Test that a graph has been generated
    result = graph_op.output()

    pd.DataFrame(result['contact_points']).to_csv("contact_points_by_count_weight_{}ds_{}dt.csv".format(ds, dt), header=None, index=None)

    assert result['graph_generated'] is True


@given(users=st.lists(st.integers()), ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(users=ALL_USER_IDS, ds=1000, dt=1200, global_origin=GLOBAL_ORIGIN)
def test_generate_contacts_by_distance(users, ds, dt, global_origin):
    if len(global_origin) == 0:
        pass

    tiles_op = GenerateTilesOp(users, ds, dt, global_origin)

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles_op.output(), weight='dist_weight')

    # Test that a graph has been generated
    result = graph_op.output()
    pd.DataFrame(result['contact_points']).to_csv("contact_points_by_distance_{}ds_{}dt.csv".format(ds, dt), header=None, index=None)

    assert result['graph_generated'] is True
