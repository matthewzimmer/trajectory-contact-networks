from app.lib.ops.tiles import GenerateTilesOp, GraphContactPointsOp
from hypothesis import given, example
import hypothesis.strategies as st


@given(ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(ds=1000, dt=1200, global_origin=(39.75872, 116.04142))
@example(ds=500, dt=600, global_origin=(39.75872, 116.04142))
@example(ds=100, dt=300, global_origin=(39.75872, 116.04142))
def test_generate_user_tiles(ds, dt, global_origin):
    # Commented out due to Travis resource limitations
    tiles = GenerateTilesOp(ds, dt, global_origin).output()
    print(tiles)


@given(ds=st.integers(), dt=st.integers(), global_origin=st.tuples())
@example(ds=1000, dt=1200, global_origin=(39.75872, 116.04142))
@example(ds=500, dt=600, global_origin=(39.75872, 116.04142))
@example(ds=100, dt=300, global_origin=(39.75872, 116.04142))
def test_generate_contact_points(ds, dt, global_origin):
    # select choice of weight
    weight = 'count_weight'  # 'dist_weight'
    tiles = GenerateTilesOp(ds, dt, global_origin).output()

    # find contacts between users (tiles with at least two users)
    # graph_op = GraphContactPointsOp(tiles, weight).perform()

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles, weight).hottest_tile()

    # Test that a graph has been generated
    result = graph_op.output()
    assert result['graph_generated'] is True
# assert result['png_filepath'] == "{}.png".format(tile_hash)
