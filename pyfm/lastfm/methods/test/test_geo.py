from lastfm.methods.geo import Geo
from lastfm.methods.test import MethodTestCase
from lastfm.models import GeoTopArtists, GeoTopTracks
from pyfm.lastfm.methods.test import fixture


class GeoTests(MethodTestCase):
    def setUp(self):
        self.geo = Geo("greece")
        super(GeoTests, self).setUp()

    @fixture.use_cassette(path="geo/get_top_artists")
    def test_get_top_artists(self):
        result = self.geo.get_top_artists(page=1, limit=10)
        actual = result.to_dict()
        response = result.response.json()

        self.assertEqual("Geo", result.namespace)
        self.assertEqual("get_top_artists", result.method)
        self.assertEqual(
            {"country": "greece", "limit": "10", "page": "1"}, result.params
        )
        self.assertIsNone(None, result.data)
        self.assertIsInstance(result, GeoTopArtists)
        self.assertGreater(len(result.artist), 0)
        self.assertDictEqual(response["topartists"], actual)

    @fixture.use_cassette(path="geo/get_top_tracks")
    def test_get_top_tracks(self):
        result = self.geo.get_top_tracks(page=1, limit=10)
        actual = result.to_dict()
        response = result.response.json()

        self.assertEqual("Geo", result.namespace)
        self.assertEqual("get_top_tracks", result.method)
        self.assertEqual(
            {"country": "greece", "limit": "10", "page": "1"}, result.params
        )
        self.assertIsNone(None, result.data)
        self.assertIsInstance(result, GeoTopTracks)
        self.assertGreater(len(result.track), 0)
        self.assertDictEqual(response["tracks"], actual)