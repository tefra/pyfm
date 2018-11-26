from typing import List, Optional, TypeVar

from attr import dataclass

from pydrag.core import BaseModel
from pydrag.lastfm.models.album import Album
from pydrag.lastfm.models.artist import Artist
from pydrag.lastfm.models.common import (
    Attributes,
    Date,
    Image,
    RootAttributes,
    Wiki,
)
from pydrag.lastfm.models.tag import Tag


@dataclass
class Corrected(BaseModel):
    text: Optional[str] = None
    code: Optional[str] = None
    corrected: Optional[int] = None


@dataclass
class TrackUpdateNowPlaying(BaseModel):
    album: Optional[Corrected] = None
    artist: Optional[Corrected] = None
    track: Optional[Corrected] = None
    timestamp: Optional[int] = None
    ignored_message: Optional[Corrected] = None
    album_artist: Optional[Corrected] = None
    attr: Optional[Attributes] = None


@dataclass
class TrackScrobble(BaseModel):
    scrobble: List[TrackUpdateNowPlaying]
    attr: Attributes

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data, dict) and data.get("scrobble"):
            if isinstance(data["scrobble"], dict):
                data["scrobble"] = [data["scrobble"]]
        return super().from_dict(data)


@dataclass
class ScrobbleTrack(BaseModel):
    artist: str
    track: str
    timestamp: int
    album: Optional[str] = None
    context: Optional[str] = None
    stream_id: Optional[str] = None
    chosen_by_user: Optional[bool] = None
    track_number: Optional[str] = None
    mbid: Optional[str] = None
    album_artist: Optional[str] = None
    duration: Optional[int] = None


T = TypeVar("T", bound="Track")
TC = TypeVar("TC", bound="TrackCorrection")


@dataclass
class Track(BaseModel):
    name: str
    artist: Artist
    url: Optional[str] = None
    mbid: Optional[str] = None
    image: Optional[List[Image]] = None
    playcount: Optional[int] = None
    listeners: Optional[int] = None
    streamable: Optional[str] = None
    duration: Optional[str] = None
    match: Optional[float] = None
    wiki: Optional[Wiki] = None
    album: Optional[Album] = None
    top_tags: Optional[List[Tag]] = None
    attr: Optional[RootAttributes] = None
    date: Optional[Date] = None
    loved: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> T:
        """
        In order to be more consistent than Last.fm api we have to normalize
        the input dictionary to fix a couple of things:

        * Flatten top tags list
        * Make sure artist field is always a dictionary

        :param data:
        :rtype: :class:`~pydrag.lastfm.models.track.Track`
        """
        try:
            data["top_tags"] = data["top_tags"]["tag"]
        except KeyError:
            pass

        try:
            if isinstance(data["album"]["artist"], str):
                data["album"]["artist"] = dict(name=data["album"]["artist"])
        except KeyError:
            pass

        if isinstance(data.get("artist"), str):
            data["artist"] = dict(name=data["artist"])

        return super().from_dict(data)

    @classmethod
    def find(
        cls, artist: str, track: str, user: str = None, lang: str = "en"
    ) -> T:

        """
        Get the metadata for a track.

        :param artist: The artist name
        :param track: The track name
        :param user: The username for the context of the request. If supplied, response will include the user's playcount for this track
        :param lang: The language to return the biography in, ISO 639
        :rtype: :class:`~pydrag.lastfm.models.track.Track`
        """
        return cls.retrieve(
            params=dict(
                method="track.getInfo",
                artist=artist,
                track=track,
                autocorrect=True,
                username=user,
                lang=lang,
            )
        )

    @classmethod
    def find_by_mbid(cls, mbid: str, user: str = None, lang: str = "en") -> T:
        """
        Get the metadata for a track.

        :param mbid: The musicbrainz id for the track
        :param user: The username for the context of the request. If supplied, response will include the user's playcount for this track
        :param lang: The language to return the biography in, ISO 639
        :rtype: :class:`~pydrag.lastfm.models.track.Track`
        """
        return cls.retrieve(
            params=dict(
                method="track.getInfo",
                mbid=mbid,
                autocorrect=True,
                username=user,
                lang=lang,
            )
        )

    @classmethod
    def get_correction(cls, track: str, artist: str) -> TC:
        """
        Use the last.fm corrections data to check whether the supplied track
        has a correction to a canonical track.

        :rtype: :class:`~pydrag.lastfm.models.track.TrackCorrection`
        """
        return cls.retrieve(
            bind=TrackCorrection,
            params=dict(
                method="track.getCorrection", artist=artist, track=track
            ),
        )

    @classmethod
    def search(cls, track: str, limit: int = 50, page: int = 1) -> List[T]:
        """
        Search for an track by name. Returns track matches sorted by relevance.

        :param track: The track name.
        :param page: The page number to fetch.
        :param limit: The number of results to fetch per page.
        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.track.Track`
        """
        return cls.retrieve(
            bind=Track,
            many=("tracks", "track"),
            params=dict(
                method="track.search", limit=limit, page=page, track=track
            ),
        )

    @classmethod
    def get_top_tracks_by_country(
        cls, country: str, limit: int = 50, page: int = 1
    ) -> List[T]:
        """
        :param country: The country to fetch the top tracks.
        :param limit: The number of results to fetch per page.
        :param page: The page number to fetch.
        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.track.Track`
        """
        return cls.retrieve(
            bind=Track,
            many="track",
            params=dict(
                method="geo.getTopTracks",
                country=country,
                limit=limit,
                page=page,
            ),
        )

    @classmethod
    def get_top_tracks_chart(cls, limit: int = 50, page: int = 1) -> List[T]:
        """
        Get the top tracks chart.

        :param limit: The number of results to fetch per page.
        :param page: The page number to fetch.
        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.track.Track`
        """
        return cls.retrieve(
            bind=Track,
            many="track",
            params=dict(method="chart.getTopTracks", limit=limit, page=page),
        )

    def add_tags(self, tags: List[str]) -> BaseModel:
        """
        Tag an track with one or more user supplied tags.

        :param tags: A list of user supplied tags to apply to this track. Accepts a maximum of 10 tags.
        :type tags: :class:`list` of :class:`str`
        :rtype: :class:`~pydrag.core.BaseModel`
        """
        return self.submit(
            bind=BaseModel,
            stateful=True,
            params=dict(
                method="track.addTags", track=self.name, tags=",".join(tags)
            ),
        )

    def remove_tag(self, tag: str) -> BaseModel:
        """
        Remove a user's tag from an track.

        :param tag: A single user tag to remove from this track.
        :rtype: :class:`~pydrag.core.BaseModel`
        """
        return self.submit(
            bind=BaseModel,
            stateful=True,
            params=dict(method="track.removeTag", track=self.name, tag=tag),
        )

    def get_similar(self, limit: int = 50) -> List[T]:
        """
        Get all the tracks similar to this track.

        :param limit: Limit the number of similar tracks returned
        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.track.Track`
        """
        return self.retrieve(
            bind=Track,
            many="track",
            params=dict(
                method="track.getSimilar",
                mbid=self.mbid,
                artist=self.artist.name,
                track=self.name,
                autocorrect=True,
                limit=limit,
            ),
        )

    def get_tags(self, user: str) -> List[Tag]:
        """
        Get the tags applied by an individual user to an track on Last.fm.

        :param user: The username for the context of the request.
        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.tag.Tag`
        """
        return self.retrieve(
            bind=Tag,
            many="tag",
            params=dict(
                method="track.getTags",
                mbid=self.mbid,
                artist=self.artist.name,
                track=self.name,
                autocorrect=True,
                user=user,
            ),
        )

    def get_top_tags(self) -> List[Tag]:
        """
        Get the top tags for an track on Last.fm, ordered by popularity.

        :rtype: :class:`list` of :class:`~pydrag.lastfm.models.tag.Tag`
        """
        return self.retrieve(
            bind=Tag,
            many="tag",
            params=dict(
                method="track.getTopTags",
                mbid=self.mbid,
                artist=self.artist.name,
                track=self.name,
                autocorrect=True,
            ),
        )

    def love(self) -> BaseModel:
        """
        Love a track for a user profile.

        :rtype: :class:`~pydrag.core.BaseModel`
        """
        return self.submit(
            bind=BaseModel,
            stateful=True,
            params=dict(
                method="track.love", artist=self.artist.name, track=self.name
            ),
        )

    def unlove(self) -> BaseModel:
        """
        Unlove a track for a user profile.

        :rtype: :class:`~pydrag.core.BaseModel`
        """
        return self.submit(
            bind=BaseModel,
            stateful=True,
            params=dict(
                method="track.unlove", artist=self.artist.name, track=self.name
            ),
        )

    @classmethod
    def scrobble(cls, tracks: List[ScrobbleTrack]) -> TrackScrobble:
        params = dict(method="track.scrobble")
        for idx, track in enumerate(tracks):
            for field, value in track.to_dict().items():
                if value is None:
                    continue
                params.update({"{}[{}]".format(field, idx): value})
        return cls.submit(bind=TrackScrobble, stateful=True, params=params)

    @classmethod
    def scrobble_tracks(
        cls, tracks: List[ScrobbleTrack], batch_size=10
    ) -> Optional[TrackScrobble]:
        """
        Split tracks into the desired batch size, with maximum size set to 50
        and send the tracks for processing, I am debating if this even belongs
        here.

        :param tracks: The tracks to scrobble
        :param batch_size: The number of tracks to submit per cycle
        :rtype: :class:`~pydrag.lastfm.models.track.TrackScrobble`
        """
        batch_size = min(batch_size, 50)

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        status = None
        batches = list(divide_chunks(tracks, batch_size))
        for batch in batches:
            result = Track.scrobble(batch)
            if status is None:
                status = result
                status.response = None
            elif result.scrobble:
                status.attr.accepted += result.attr.accepted
                status.attr.ignored += result.attr.ignored
                status.scrobble.extend(status.scrobble)
        return status

    @classmethod
    def update_now_playing(
        cls,
        artist: str,
        track: str,
        album: str = None,
        track_number: int = None,
        context: str = None,
        duration: int = None,
        album_artist: str = None,
    ) -> TrackUpdateNowPlaying:
        """
        :param artist: The artist name
        :param track: The track name
        :param album: The album name
        :param track_number: The track number of the track on the album
        :param context: Sub-client version (not public)
        :param duration: The length of the track in seconds
        :param album_artist: The album artist
        :rtype: :class:`~pydrag.core.BaseModel`
        """

        return cls.submit(
            bind=TrackUpdateNowPlaying,
            stateful=True,
            params=dict(
                method="track.updateNowPlaying",
                artist=artist,
                track=track,
                album=album,
                trackNumber=track_number,
                context=context,
                duration=duration,
                albumArtist=album_artist,
            ),
        )


@dataclass
class CorrectionAttributes(BaseModel):
    index: int
    track_corrected: int
    artist_corrected: int


@dataclass
class CorrectionTrack(BaseModel):
    attr: CorrectionAttributes
    track: Track


@dataclass
class TrackCorrection(BaseModel):
    correction: CorrectionTrack
