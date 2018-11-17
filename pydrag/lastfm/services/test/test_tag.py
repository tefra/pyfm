from pydrag.lastfm.models.common import (
    AlbumList,
    ArtistList,
    ChartList,
    TagInfo,
    TagInfoList,
    TrackList,
)
from pydrag.lastfm.services.tag import TagService
from pydrag.lastfm.services.test import MethodTestCase, fixture


class TagServiceTests(MethodTestCase):
    def setUp(self):
        self.tag = TagService("rap")
        super(TagServiceTests, self).setUp()

    @fixture.use_cassette(path="tag/get_info")
    def test_get_info(self):
        result = self.tag.get_info(lang="en")

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_info", result.method)
        self.assertEqual({"lang": "en", "tag": "rap"}, result.params)
        self.assertIsInstance(result, TagInfo)
        self.assertFixtureEqual("tag/get_info", result.to_dict())

    def test_get_info_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_info()

    @fixture.use_cassette(path="tag/get_similar")
    def test_get_similar(self):
        """
        @todo investigate why I cant get any results for this
        """
        self.tag.tag = "Disco"
        result = self.tag.get_similar()

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_similar", result.method)
        self.assertEqual({"tag": "Disco"}, result.params)
        self.assertIsInstance(result, TagInfoList)
        self.assertFixtureEqual("tag/get_similar", result.to_dict())

    def test_get_similar_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_similar()

    @fixture.use_cassette(path="tag/get_top_albums")
    def test_get_top_albums(self):
        result = self.tag.get_top_albums(page=1, limit=2)

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_top_albums", result.method)
        self.assertEqual({"limit": 2, "page": 1, "tag": "rap"}, result.params)

        self.assertIsInstance(result, AlbumList)
        self.assertFixtureEqual("tag/get_top_albums", result.to_dict())

    def test_get_top_albums_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_top_albums()

    @fixture.use_cassette(path="tag/get_top_artists")
    def test_get_top_artists(self):
        result = self.tag.get_top_artists(page=1, limit=2)

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_top_artists", result.method)
        self.assertEqual({"limit": 2, "page": 1, "tag": "rap"}, result.params)

        self.assertIsInstance(result, ArtistList)
        self.assertFixtureEqual("tag/get_top_artists", result.to_dict())

        self.assertEqual(1, result.get_page())
        self.assertEqual(2, result.get_limit())
        self.assertEqual(61526, result.get_total())
        self.assertEqual(30763, result.get_total_pages())
        self.assertFalse(result.has_prev())
        self.assertTrue(result.has_next())

    def test_get_top_artists_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_top_artists()

    @fixture.use_cassette(path="tag/get_top_tracks")
    def test_get_top_tracks(self):
        result = self.tag.get_top_tracks(page=1, limit=2)

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_top_tracks", result.method)
        self.assertEqual({"limit": 2, "page": 1, "tag": "rap"}, result.params)

        self.assertIsInstance(result, TrackList)
        self.assertFixtureEqual("tag/get_top_tracks", result.to_dict())

    def test_get_top_tracks_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_top_tracks()

    @fixture.use_cassette(path="tag/get_top_tags")
    def test_get_top_tags(self):
        result = self.tag.get_top_tags(page=3, limit=10)

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_top_tags", result.method)
        self.assertEqual({"num_res": 10, "offset": 20}, result.params)
        self.assertEqual(10, len(result.tag))
        self.assertIsInstance(result, TagInfoList)
        self.assertFixtureEqual("tag/get_top_tags", result.to_dict())

    @fixture.use_cassette(path="tag/get_weekly_chart_list")
    def test_get_weekly_chart_list(self):
        result = self.tag.get_weekly_chart_list()

        self.assertEqual("Tag", result.namespace)
        self.assertEqual("get_weekly_chart_list", result.method)
        self.assertEqual({"tag": "rap"}, result.params)

        self.assertIsInstance(result, ChartList)
        self.assertFixtureEqual("tag/get_weekly_chart_list", result.to_dict())

    def test_get_weekly_chart_list_no_tag(self):
        with self.assertRaises(AssertionError):
            TagService().get_weekly_chart_list()
