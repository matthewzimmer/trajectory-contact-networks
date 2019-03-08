from app.lib.ops.tiles import GenerateTilesOp, GraphContactPointsOp


def test_generate_user_tiles():
    ds = 1000
    dt = 1200
    global_origin = (39.75872, 116.04142)

    # Commented out due to Travis resource limitations
    # tiles = GenerateTilesOp(ds, dt, global_origin).output()
    # print(tiles)


def test_generate_contact_points():
    ds = 1000
    dt = 1200
    global_origin = (39.75872, 116.04142)

    # NOTE: Commented out due to Travis resource limitations
    #
    # tiles = GenerateTilesOp(ds, dt, global_origin).output()
    #
    # Mocking the structure of GenerateTilesOp#output for now as follows:
    users = set()
    users.add("000")
    users.add("001")
    users.add("005")

    tile_hash = "40.00lat_117.443lon_12345678987654321t"
    tiles = {tile_hash: users}

    # QUESTION:
    #
    #   Which users are inside of a given tile?
    #
    # TODO:
    #   1. Generate PNGs of contact points for each unique tile.
    #   2. Persist to disk (we can scp them off of cloud server later).
    for tile_hash, tile_data in tiles.items():
        graph_op = GraphContactPointsOp(tile_hash, tile_data).perform()
        result = graph_op.output()

        assert result['png_filepath'] == "{}.png".format(tile_hash)
        assert result['graph_generated'] == False
