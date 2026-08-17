"""Musicbrainz Query Helper"""

import logging
from dataclasses import dataclass

import musicbrainzngs

from .async_helpers import async_wrap

_LOGGER = logging.getLogger(__name__)

@dataclass
class MusicBrainzInfo:
  disc_id: str
  release_id: str | None = None
  artist: str | None = None
  title: str | None = None
  track_titles: dict[int, str] | None = None
  image: bytes | None = None

def musicbrainz_get_info(disc_id: str) -> MusicBrainzInfo:
  try:
    # the "labels" include enables the cat#s we display
    response = musicbrainzngs.get_releases_by_discid(disc_id, includes=["recordings","artists"])
    return _parse_response(disc_id, response)
  except Exception as err:  # noqa: BLE001 - third-party lookup failures should not break setup
    _LOGGER.info(f"Could not get disc information, error={err}")
    return MusicBrainzInfo(disc_id)

def _parse_response(disc_id: str, response: dict) -> MusicBrainzInfo:
  if response.get('disc'):
    #just use the first release for this disc
    rel = response['disc']['release-list'][0]
    return _info_from_release(disc_id, rel)
  elif response.get("cdstub"):
    _LOGGER.debug("CDSTUB found, returning.")
    return MusicBrainzInfo(
      disc_id=disc_id, 
      artist=response["cdstub"]["artist"],
      title=response["cdstub"]["title"]
    )

  return MusicBrainzInfo(disc_id)

def _info_from_release(disc_id: str, rel: dict) -> MusicBrainzInfo:
  mbid = rel["id"]
  title = rel["title"]
  artist = None
  tracks = {}
  image = None

  _LOGGER.debug(f"Found release {mbid}, title={title}")

  artist_credit = rel["artist-credit"]
  if artist_credit:
    artist = artist_credit[0]["artist"]["name"]

  found = False
  for medium in rel["medium-list"]:
    for disc in medium["disc-list"]:
      if disc["id"] == disc_id:
        for track in medium["track-list"]:
          tracks[int(track["position"])] = track["recording"]["title"]        
        _LOGGER.debug(f"Found {len(tracks)} tracks")
        image = _get_image(mbid)
        if image:
          _LOGGER.debug("Found coverart image")
        found = True
        break
    if found:
      break 

  return MusicBrainzInfo(disc_id, mbid, artist, title, tracks, image)

def _get_image(release_id: str) -> bytes | None:
  try:
    return musicbrainzngs.get_image_front(release_id, "500")
  except Exception as err:  # noqa: BLE001 - third-party lookup failures should not break setup
    _LOGGER.info(f"Could not get image for disc, error={err}")
    return None

async_musicbrainz_get_info = async_wrap(musicbrainz_get_info)

