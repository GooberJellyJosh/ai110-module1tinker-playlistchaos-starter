import random
from typing import Dict, List, Optional, Tuple

# A song is a dict with the keys: title, artist, genre, energy, tags (and mood
# once it has been classified).
Song = Dict[str, object]
# Maps a mood name ("Hype", "Chill", "Mixed") to the songs in that playlist.
PlaylistMap = Dict[str, List[Song]]

DEFAULT_PROFILE = {
    "name": "Default",
    "hype_min_energy": 7,
    "chill_max_energy": 3,
    "favorite_genre": "rock",
    "include_mixed": True,
}

# Mood names, used as both the playlist keys and the labels shown in the app.
HYPE = "Hype"
CHILL = "Chill"
MIXED = "Mixed"

# A song is Hype if its genre contains one of these words.
HYPE_GENRE_KEYWORDS = ["rock", "punk", "party"]
# A song is Chill if its title contains one of these words.
CHILL_TITLE_KEYWORDS = ["lofi", "ambient", "sleep"]


# ---------------------------------------------------------------------------
# Normalization: clean up raw input so songs can be compared consistently
# ---------------------------------------------------------------------------


def normalize_title(title: str) -> str:
    """Normalize a song title for comparisons."""
    if not isinstance(title, str):
        return ""
    # Titles keep their capitalization for display; only extra spaces go.
    return title.strip()


def normalize_artist(artist: str) -> str:
    """Normalize an artist name for comparisons."""
    if not artist:
        return ""
    return artist.strip().lower()


def normalize_genre(genre: str) -> str:
    """Normalize a genre name for comparisons."""
    return genre.lower().strip()


def normalize_song(raw: Song) -> Song:
    """Return a normalized song dict with expected keys."""
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    energy = raw.get("energy", 0)

    # Energy typed in as text becomes a number; anything unreadable becomes 0.
    if isinstance(energy, str):
        try:
            energy = int(energy)
        except ValueError:
            energy = 0

    # A single tag given as plain text is wrapped so tags is always a list.
    tags = raw.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


# ---------------------------------------------------------------------------
# Classification: decide which mood playlist a song belongs to
# ---------------------------------------------------------------------------


def contains_any_keyword(text: str, keywords: List[str]) -> bool:
    """Return True if any of the keywords appears somewhere inside the text."""
    return any(keyword in text for keyword in keywords)


def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """Return a mood label given a song and user profile."""
    energy = song.get("energy", 0)
    genre = song.get("genre", "")
    title = song.get("title", "")

    hype_min_energy = profile.get("hype_min_energy", 7)
    chill_max_energy = profile.get("chill_max_energy", 3)
    favorite_genre = profile.get("favorite_genre", "")

    has_hype_genre = contains_any_keyword(genre, HYPE_GENRE_KEYWORDS)
    # FIX: compare against a lowercase title so "Lofi Beats" or "SLEEP" still
    # match the lowercase chill keywords.
    has_chill_title = contains_any_keyword(str(title).lower(), CHILL_TITLE_KEYWORDS)

    # Hype is checked first, so a song that meets both sets of rules is Hype.
    if genre == favorite_genre or energy >= hype_min_energy or has_hype_genre:
        return HYPE
    if energy <= chill_max_energy or has_chill_title:
        return CHILL
    # Anything that is neither Hype nor Chill.
    return MIXED


def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """Group songs into playlists based on mood and profile."""
    playlists: PlaylistMap = {
        HYPE: [],
        CHILL: [],
        MIXED: [],
    }

    for song in songs:
        normalized_song = normalize_song(song)
        mood = classify_song(normalized_song, profile)
        # Remember the mood on the song so the app can display it later.
        normalized_song["mood"] = mood
        playlists[mood].append(normalized_song)

    return playlists


def merge_playlists(
    first_playlists: PlaylistMap,
    second_playlists: PlaylistMap,
) -> PlaylistMap:
    """Merge two playlist maps into a new map."""
    merged: PlaylistMap = {}
    # Every mood that appears in either map.
    all_moods = set(first_playlists) | set(second_playlists)

    for mood in all_moods:
        # FIX: copy the list so extending it does not also change the first
        # playlist map.
        merged[mood] = list(first_playlists.get(mood, []))
        merged[mood].extend(second_playlists.get(mood, []))
    return merged


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """Compute statistics across all playlists."""
    # Flatten every playlist into one list of songs.
    all_songs: List[Song] = []
    for playlist_songs in playlists.values():
        all_songs.extend(playlist_songs)

    hype_songs = playlists.get(HYPE, [])
    chill_songs = playlists.get(CHILL, [])
    mixed_songs = playlists.get(MIXED, [])

    total_songs = len(all_songs)

    # FIX: the ratio is Hype songs out of ALL songs (it used to divide the Hype
    # count by itself, so it was always 1.0).
    hype_ratio = len(hype_songs) / total_songs if total_songs > 0 else 0.0

    # FIX: add up the energy of every song, not only the Hype songs.
    average_energy = 0.0
    if all_songs:
        total_energy = sum(song.get("energy", 0) for song in all_songs)
        average_energy = total_energy / total_songs

    top_artist, top_artist_count = most_common_artist(all_songs)

    return {
        "total_songs": total_songs,
        "hype_count": len(hype_songs),
        "chill_count": len(chill_songs),
        "mixed_count": len(mixed_songs),
        "hype_ratio": hype_ratio,
        "avg_energy": average_energy,
        "top_artist": top_artist,
        "top_artist_count": top_artist_count,
    }


def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """Return the most common artist and count."""
    # Count how many songs each artist has.
    song_count_by_artist: Dict[str, int] = {}
    for song in songs:
        artist = str(song.get("artist", ""))
        if not artist:
            continue
        song_count_by_artist[artist] = song_count_by_artist.get(artist, 0) + 1

    if not song_count_by_artist:
        return "", 0

    # Sort the (artist, count) pairs so the biggest count comes first.
    artists_by_count = sorted(
        song_count_by_artist.items(),
        key=lambda artist_and_count: artist_and_count[1],
        reverse=True,
    )
    return artists_by_count[0]


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def search_songs(
    songs: List[Song],
    query: str,
    field: str = "artist",
) -> List[Song]:
    """Return songs matching the query on a given field."""
    # An empty search box means "show everything".
    if not query:
        return songs

    search_text = query.lower().strip()
    matching_songs: List[Song] = []

    for song in songs:
        field_value = str(song.get(field, "")).lower()
        # FIX: the query must be contained in the song's value (partial match),
        # not the other way around, so "AC" finds "AC/DC".
        if field_value and search_text in field_value:
            matching_songs.append(song)

    return matching_songs


# ---------------------------------------------------------------------------
# Lucky pick
# ---------------------------------------------------------------------------


def lucky_pick(
    playlists: PlaylistMap,
    mode: str = "any",
) -> Optional[Song]:
    """Pick a song from the playlists according to mode."""
    if mode == "hype":
        candidate_songs = playlists.get(HYPE, [])
    elif mode == "chill":
        candidate_songs = playlists.get(CHILL, [])
    else:
        # FIX: "any" draws from every playlist, including Mixed.
        candidate_songs = (
            playlists.get(HYPE, [])
            + playlists.get(CHILL, [])
            + playlists.get(MIXED, [])
        )

    return random_choice_or_none(candidate_songs)


def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """Return a random song or None."""
    # FIX: random.choice crashes on an empty list, so return None instead.
    if not songs:
        return None
    return random.choice(songs)


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def history_summary(history: List[Song]) -> Dict[str, int]:
    """Return a summary of moods seen in the history."""
    picks_per_mood = {HYPE: 0, CHILL: 0, MIXED: 0}
    for song in history:
        mood = song.get("mood", MIXED)
        # A missing or unrecognized mood is counted as Mixed.
        if mood not in picks_per_mood:
            picks_per_mood[MIXED] += 1
        else:
            picks_per_mood[mood] += 1
    return picks_per_mood
