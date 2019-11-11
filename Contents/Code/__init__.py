from base64 import b64encode
import hashlib

from helper import *
from log import *
from xml import *

from mutagen import File as MFile

version = "2.0.0"


# noinspection PyClassHasNoInit
class AvalonXmlTvAgent(Agent.TV_Shows):
    name = "Avalon XML TV Agent"
    ver = version
    primary_provider = True
    languages = [Locale.Language.NoLanguage]
    accepts_from = ["com.plexapp.agents.localmedia"]

    def search(self, results, media, lang, manual):
        Log("==================== Search Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)
        Log("Search for %s" % get_show_title(media))

        # Get the root element in nfo
        root_element = get_show_xml(media)

        if root_element is None:
            Log("Cannot find tvshow.nfo in show directory.")
            return None

        if root_element.tag != "tvshow":
            Log("Invalid format. The root tag should be <tvshow>.")
            return None

        tv_xml = TvXml(root_element)

        title = tv_xml.title
        if title is None:
            Log("Invalid format. Missing <title> tag.")
            return None

        year = tv_xml.originally_available_at.year if tv_xml.originally_available_at is not None else 0
        Log("Title: %s" % title)
        Log("Year: %d" % year)

        # Plex throws exception that have "/" in ID
        mid = b64encode("%s:%d" % (title, year)).replace("/", "_")

        results.Append(MetadataSearchResult(id=mid, name=title, year=year, lang=lang, score=100))

        Log("====================  Search end  ====================")

    def update(self, metadata, media, lang, force):
        Log("==================== Update Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)
        Log("Search for %s" % get_show_title(media))

        # Get the root element in xml
        root_element = get_show_xml(media)

        if root_element is None:
            Log("Cannot find tvshow.nfo in show directory.")
            return None

        if root_element.tag != "tvshow":
            Log("Invalid format. The root tag should be <tvshow>.")
            return None

        tv_xml = TvXml(root_element)
        put_update(str(media.id), "2", tv_xml.original_title, tv_xml.tagline)
        tv_xml.set_metadata(metadata)
        self.update_episode(metadata, media)

        Log("====================  Update end  ====================")

    @staticmethod
    def update_episode(metadata, media):
        title = get_show_title(media)
        for season in media.seasons:
            updated_summary = False
            for episode in media.seasons[season].episodes:
                if not updated_summary:
                    season_id = media.seasons[season].id
                    summary = get_summary_txt(media, season, episode)
                    if summary is not None:
                        put_update(season_id, "3", summary=summary)
                    updated_summary = True
                Log("Update %s (season: %s, episode: %s)" % (title, season, episode))
                episode_metadata = metadata.seasons[season].episodes[episode]
                root_element = get_episode_xml(media, season, episode)
                if root_element is None:
                    PlexLog.warn("Cannot find episode nfo (Season: %s, Episode: %s)" % (season, episode))
                    continue
                if root_element.tag != "episodedetails":
                    PlexLog.warn("Invalid format. The root tag should be <episodedetails>.")
                    continue

                episode_xml = EpisodeXml(root_element)
                episode_xml.set_metadata(episode_metadata)
                """
                thumb_result = get_episode_thumb(media, season, episode)
                if thumb_result is not None:
                    thumb_path, thumb = thumb_result
                    episode_metadata.thumbs[thumb_path] = thumb
                """


# noinspection PyClassHasNoInit
class AvalonXmlMovieAgent(Agent.Movies):
    name = "Avalon XML Movie Agent"
    ver = version
    primary_provider = True
    languages = [Locale.Language.NoLanguage]
    accepts_from = ["com.plexapp.agents.localmedia"]

    def search(self, results, media, lang, manual):
        Log("==================== Search Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)
        Log("Search for %s" % get_movie_title(media))

        # Get the root element in xml
        root_element = get_movie_xml(media)

        if root_element is None:
            Log("Cannot find xml in movie directory.")
            return None

        if root_element.tag != "movie":
            Log("Invalid format. The root tag should be <movie>.")
            return None

        movie_xml = MovieXml(root_element)

        title = movie_xml.title
        if title is None:
            Log("Invalid format. Missing <title> tag.")
            return None

        year = movie_xml.originally_available_at.year if movie_xml.originally_available_at is not None else 0
        Log("Title: %s" % title)
        Log("Year: %d" % year)

        # Plex throws exception that have "/" in ID
        mid = b64encode("%s:%d" % (title, year)).replace("/", "_")
        results.Append(MetadataSearchResult(id=mid, name=title, year=year, lang="xn", score=100))
        Log(MetadataSearchResult(id=mid, name=title, year=year, lang="xn", score=100))
        Log("====================  Search end  ====================")

    def update(self, metadata, media, lang, force):
        Log("==================== Update Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)
        Log("Search for %s" % get_movie_title(media))

        # Get the root element in nfo
        root_element = get_movie_xml(media)

        if root_element is None:
            Log("Cannot find nfo in movie directory.")
            return None

        if root_element.tag != "movie":
            Log("Invalid format. The root tag should be <movie>.")
            return None
        movie_xml = MovieXml(root_element)
        movie_xml.set_metadata(metadata)
        Log("====================  Update end  ====================")


# noinspection PyClassHasNoInit
class AvalonXmlArtistAgent(Agent.Artist):
    name = "Avalon XML Artist Agent"
    ver = version
    primary_provider = True
    languages = [Locale.Language.NoLanguage]
    accepts_from = ["com.plexapp.agents.localmedia"]

    def search(self, results, media, lang, manual):
        Log("==================== Search Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)

        # Get the root element in xml
        root_element = get_artist_xml(media)

        if root_element is None:
            Log("Cannot find xml in movie directory.")
            return None

        if root_element.tag != "artist":
            Log("Invalid format. The root tag should be <artist>.")
            return None

        Log("Artist: %s" % media.title)

        results.Append(MetadataSearchResult(id=media.id, name=media.title, lang=lang, year=None, score=100))

        Log("====================  Search end  ====================")

    def update(self, metadata, media, lang, force):
        Log("==================== Update Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)

        # Get the root element in xml
        root_element = get_artist_xml(media)

        if root_element is None:
            Log("Cannot find xml in movie directory.")
            return None

        if root_element.tag != "artist":
            Log("Invalid format. The root tag should be <artist>.")
            return None

        artist_xml = ArtistXml(root_element)
        artist_xml.set_metadata(metadata)

        artist_cover = get_artist_cover(media)
        if artist_cover is not None:
            cover, proxy = artist_cover
            key = hashlib.md5(cover).hexdigest()
            metadata.posters[key] = proxy

        Log("====================  Update end  ====================")


# noinspection PyClassHasNoInit
class AvalonXmlAlbumAgent(Agent.Album):
    name = "Avalon XML Album Agent"
    ver = version
    primary_provider = True
    languages = [Locale.Language.NoLanguage]
    accepts_from = ["com.plexapp.agents.localmedia"]

    def search(self, results, media, lang, manual):
        Log("==================== Search Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)

        # Get the root element in xml
        root_element = get_album_xml(media)

        if root_element is None:
            Log("Cannot find xml in movie directory.")
            return None

        if root_element.tag != "album":
            Log("Invalid format. The root tag should be <album>.")
            return None

        Log("Album: %s" % media.title)

        results.Append(MetadataSearchResult(id=media.id, name=media.title, lang=lang, year=None, score=100))

        Log("====================  Search end  ====================")

    def update(self, metadata, media, lang, force):
        Log("==================== Update Start ====================")
        Log("%s (%s)" % (self.name, self.ver))
        Log("Plex version: %s" % Platform.ServerVersion)

        # Get the root element in xml
        root_element = get_album_xml(media)

        if root_element is None:
            Log("Cannot find xml in movie directory.")
            return None

        if root_element.tag != "album":
            Log("Invalid format. The root tag should be <album>.")
            return None

        album_xml = AlbumXml(root_element)
        album_xml.set_metadata(metadata)
        update_album(str(media.id), media.title, album_xml)

        Log("====================  Update track  ====================")
        for track in media.children:
            part = track.items[0].parts[0].file
            self.update_tracks(track.id, part)
        Log("====================  Update end  ====================")

    def update_tracks(self, media_id, file):
        try:
            tags = MFile(file, None, True)
            artist_str = " / ".join(tags["artist"])
            update_track(media_id, artist_str)
        except Exception, e:
            Log(e)
