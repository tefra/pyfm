import os
import time
from collections import UserList
from typing import Dict, List, Optional, Sequence, Type, TypeVar, Union

from attr import Factory, asdict, attrib, dataclass, fields

from pydrag.utils import md5, to_camel_case

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    params: Union[List, Dict, None] = attrib(init=False, default=None)

    def to_dict(self) -> Dict:
        """
        Convert our object to a traditional dictionary. Filter out None values
        and dictionary values. The last one is like a validation for the unit
        tests in case we forgot to properly deserialize an dict to an object.

        :rtype: Dict
        """
        return asdict(
            self, filter=lambda f, v: v is not None and type(v) != dict
        )

    @classmethod
    def from_dict(cls: Type, data: Dict) -> "BaseModel":
        for f in fields(cls):
            if f.name not in data or data[f.name] is None:
                continue

            if f.type == str or f.type == Optional[str]:
                data[f.name] = str(data[f.name])
            elif f.type == int or f.type == Optional[int]:
                data[f.name] = int(data[f.name])
            elif f.type == float or f.type == Optional[float]:
                data[f.name] = float(data[f.name])

        return cls(**data)


@dataclass(cmp=False)
class ListModel(UserList, Sequence[T], BaseModel):
    data: List[T] = []

    def to_dict(self) -> Dict:
        return dict(data=[item.to_dict() for item in self])

    @classmethod
    def from_dict(cls: Type, data: Dict):
        raise NotImplementedError()


@dataclass
class RawResponse(BaseModel):
    data: Optional[dict] = None

    def to_dict(self):
        return self.data

    @classmethod
    def from_dict(cls, data):
        return cls(data)


@dataclass(auto_attribs=False)
class Config:
    api_key: str = attrib()
    api_secret: str = attrib()
    username: str = attrib()
    password: str = attrib(converter=md5)
    session: "AuthSession" = attrib(default=None)  # type: ignore  # noqa: F821

    api_url: str = "https://ws.audioscrobbler.com/2.0/"
    auth_url: str = "https://www.last.fm/api/auth?token={}&api_key={}"
    _instance: Optional["Config"] = None

    def __attrs_post_init__(self):
        Config._instance = self

    @property
    def auth_token(self):
        return md5(str(self.username) + str(self.password))

    @staticmethod
    def instance(
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        session: Optional[str] = None,
    ):

        params = dict(
            api_key=api_key,
            api_secret=api_secret,
            username=username,
            password=password,
            session=session,
        )
        if Config._instance is None or api_key:
            kwargs = {k: v for k, v in params.items() if v is not None}
            if not kwargs:
                kwargs = {
                    k: os.getenv("LASTFM_{}".format(k.upper()), "")
                    for k in params.keys()
                }
            Config(**kwargs)
        return Config._instance


@dataclass
class Attributes(BaseModel):
    timestamp: Optional[int] = None
    rank: Optional[int] = None
    date: Optional[str] = None
    position: Optional[int] = None


@dataclass
class Image(BaseModel):
    size: str
    text: str


@dataclass
class Date(BaseModel):
    timestamp: int
    text: str


@dataclass
class Chart(BaseModel):
    text: str
    from_date: str
    to_date: str


@dataclass
class Link(BaseModel):
    href: str
    rel: str
    text: str


@dataclass
class Wiki(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    published: Optional[str] = None
    links: Optional[List[Link]] = None

    @classmethod
    def from_dict(cls, data: Dict):
        if "links" in data:
            if isinstance(data["links"]["link"], dict):
                data["links"]["link"] = [data["links"]["link"]]

            data["links"] = list(map(Link.from_dict, data["links"]["link"]))
        return super().from_dict(data)


@dataclass
class ScrobbleTrack(BaseModel):
    artist: str
    track: str
    timestamp: int = attrib(default=Factory(lambda: int(time.time())))
    track_number: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    duration: Optional[int] = None
    mbid: Optional[str] = None
    context: Optional[str] = None
    stream_id: Optional[str] = None
    chosen_by_user: Optional[bool] = None

    def to_api_dict(self):
        return {to_camel_case(k): v for k, v in self.to_dict().items()}

    @classmethod
    def from_dict(cls, data: Dict):
        data.update(
            {
                k: data[k]["text"]
                if data.get(k, {}).get("text", "") != ""
                else None
                for k in ["album", "artist", "track", "album_artist"]
            }
        )
        return super().from_dict(data)
