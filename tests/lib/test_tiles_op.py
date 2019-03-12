from app.lib.ops.tiles import GenerateTilesOp, GraphContactPointsOp
from hypothesis import given, example
import hypothesis.strategies as st


@given(ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(ds=1000, dt=1200, global_origin=(39.75872, 116.04142))
@example(ds=500, dt=600, global_origin=(39.75872, 116.04142))
@example(ds=100, dt=300, global_origin=(39.75872, 116.04142))
def test_generate_user_tiles(ds, dt, global_origin):
    # Commented out due to Travis resource limitations
    # tiles = GenerateTilesOp(ds, dt, global_origin).output()
    # print(tiles)
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


@given(ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(ds=1000, dt=1200, global_origin=(39.75872, 116.04142))
@example(ds=500, dt=600, global_origin=(39.75872, 116.04142))
@example(ds=100, dt=300, global_origin=(39.75872, 116.04142))
def test_generate_contacts_by_count_weight(ds, dt, global_origin):
    tiles = GenerateTilesOp(ds, dt, global_origin).output()

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles, weight='count_weight')

    # Test that a graph has been generated
    result = graph_op.output()
    assert result['graph_generated'] is True


@given(ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(ds=1000, dt=1200, global_origin=(39.75872, 116.04142))
@example(ds=500, dt=600, global_origin=(39.75872, 116.04142))
@example(ds=100, dt=300, global_origin=(39.75872, 116.04142))
def test_generate_contacts_by_distance(ds, dt, global_origin):
    tiles = GenerateTilesOp(ds, dt, global_origin).output()

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles, weight='dist_weight')

    # Test that a graph has been generated
    result = graph_op.output()
    assert result['graph_generated'] is True