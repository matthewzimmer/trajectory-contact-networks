from app.lib.ops.tiles import GenerateTilesOp, GraphContactPointsOp


def test_generate_user_tiles():
    ds = 1000
    dt = 1200
    global_origin = (39.75872, 116.04142)

    # Commented out due to Travis resource limitations
    tiles = GenerateTilesOp(ds, dt, global_origin).output()
    print(tiles)


def test_generate_count_by_weight():
    # select granularity
    ds = 100  # 1000
    dt = 300  # 1200
    global_origin = (39.75872, 116.04142)

    tiles = GenerateTilesOp(ds, dt, global_origin).output()

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles, weight='count_weight').hottest_tile()

    # Test that a graph has been generated
    result = graph_op.output()
    assert result['graph_generated'] is True


def test_generate_count_by_distance():
    # select granularity
    ds = 100  # 1000
    dt = 300  # 1200
    global_origin = (39.75872, 116.04142)

    tiles = GenerateTilesOp(ds, dt, global_origin).output()

    # find contact points involving most users. (most occupied tile/s)
    graph_op = GraphContactPointsOp(tiles, weight='dist_weight').hottest_tile()

    # Test that a graph has been generated
    result = graph_op.output()
    assert result['graph_generated'] is True

