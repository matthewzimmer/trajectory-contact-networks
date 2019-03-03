from app.lib.datasets import GeolifeData


def test_geolife_data():
    data = GeolifeData().output()

    assert 'users' in data
    assert 'trajectories' in data
    assert len(data['users']) == 20
