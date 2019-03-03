from app.lib.datasets import GeolifeData


def test_geolife_data():
    data = GeolifeData().output()

    assert 'users' in data
    assert 'trajectories' in data

    notable_uids = set([
        '000', '001', '002', '003', '004',
        '005', '006', '007', '008', '009',
        '010', '011', '012', '013', '014',
        '015', '016', '017', '018', '019',
    ])
    assert set(data['users']).intersection(notable_uids) == notable_uids
