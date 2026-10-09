import streamlit as st

from playlist_logic import (
    DEFAULT_PROFILE,
    Song,
    build_playlists,
    compute_playlist_stats,
    history_summary,
    lucky_pick,
    merge_playlists,
    normalize_song,
    search_songs,
)

# Genres offered in both the "Favorite genre" and "Add a song" dropdowns.
GENRE_OPTIONS = ["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"]


def init_state():
    """Initialize Streamlit session state."""
    # Session state survives reruns, so each value is only set the first time.
    if "songs" not in st.session_state:
        st.session_state.songs = default_songs()
    if "profile" not in st.session_state:
        st.session_state.profile = dict(DEFAULT_PROFILE)
    if "history" not in st.session_state:
        st.session_state.history = []


def default_songs():
    """Return a default list of songs."""
    return [
        {
            "title": "Thunderstruck",
            "artist": "AC/DC",
            "genre": "rock",
            "energy": 9,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Lo-fi Rain",
            "artist": "DJ Calm",
            "genre": "lofi",
            "energy": 2,
            "tags": ["study"],
        },
        {
            "title": "Night Drive",
            "artist": "Neon Echo",
            "genre": "electronic",
            "energy": 6,
            "tags": ["synth"],
        },
        {
            "title": "Soft Piano",
            "artist": "Sleep Sound",
            "genre": "ambient",
            "energy": 1,
            "tags": ["sleep"],
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "energy": 8,
            "tags": ["classic", "opera"],
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "energy": 8,
            "tags": ["synth", "dance"],
        },
        {
            "title": "Take Five",
            "artist": "Dave Brubeck",
            "genre": "jazz",
            "energy": 4,
            "tags": ["classic", "instrumental"],
        },
        {
            "title": "Strobe",
            "artist": "Deadmau5",
            "genre": "electronic",
            "energy": 7,
            "tags": ["progressive", "long"],
        },
        {
            "title": "Weightless",
            "artist": "Marconi Union",
            "genre": "ambient",
            "energy": 1,
            "tags": ["relax", "sleep"],
        },
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana",
            "genre": "rock",
            "energy": 9,
            "tags": ["grunge", "90s"],
        },
        {
            "title": "Levitating",
            "artist": "Dua Lipa",
            "genre": "pop",
            "energy": 8,
            "tags": ["dance", "party"],
        },
        {
            "title": "So What",
            "artist": "Miles Davis",
            "genre": "jazz",
            "energy": 3,
            "tags": ["trumpet", "cool"],
        },
        {
            "title": "Midnight City",
            "artist": "M83",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "dream"],
        },
        {
            "title": "Gymnopedie No.1",
            "artist": "Erik Satie",
            "genre": "ambient",
            "energy": 1,
            "tags": ["piano", "calm"],
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "genre": "rock",
            "energy": 8,
            "tags": ["guitar", "80s"],
        },
        {
            "title": "Bad Guy",
            "artist": "Billie Eilish",
            "genre": "pop",
            "energy": 6,
            "tags": ["bass", "dark"],
        },
        {
            "title": "Fly Me to the Moon",
            "artist": "Frank Sinatra",
            "genre": "jazz",
            "energy": 5,
            "tags": ["vocal", "swing"],
        },
        {
            "title": "Sandstorm",
            "artist": "Darude",
            "genre": "electronic",
            "energy": 10,
            "tags": ["trance", "meme"],
        },
        {
            "title": "Clair de Lune",
            "artist": "Claude Debussy",
            "genre": "ambient",
            "energy": 2,
            "tags": ["piano", "classical"],
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "genre": "pop",
            "energy": 9,
            "tags": ["funk", "dance"],
        },
        {
            "title": "Feeling Good",
            "artist": "Nina Simone",
            "genre": "jazz",
            "energy": 6,
            "tags": ["soul", "vocal"],
        },
    ]


def profile_sidebar():
    """Render and update the user profile."""
    st.sidebar.header("Mood profile")

    profile = st.session_state.profile

    profile["name"] = st.sidebar.text_input(
        "Profile name",
        value=str(profile.get("name", "")),
    )

    # Energy cut-offs: at or above the first is Hype, at or below the second
    # is Chill.
    profile["hype_min_energy"] = st.sidebar.slider(
        "Hype min energy",
        min_value=1,
        max_value=10,
        value=int(profile.get("hype_min_energy", 7)),
    )
    profile["chill_max_energy"] = st.sidebar.slider(
        "Chill max energy",
        min_value=1,
        max_value=10,
        value=int(profile.get("chill_max_energy", 3)),
    )

    # Songs in the favorite genre always count as Hype.
    profile["favorite_genre"] = st.sidebar.selectbox(
        "Favorite genre",
        options=GENRE_OPTIONS,
        index=0,
    )

    profile["include_mixed"] = st.sidebar.checkbox(
        "Include Mixed playlist in views",
        value=bool(profile.get("include_mixed", True)),
    )

    st.sidebar.write("Current profile:", profile["name"])


def song_identity(song):
    """Return the (title, artist) pair that makes a song unique."""
    normalized_song = normalize_song(song)
    # Titles keep their capitalization when stored, so lowercase them here.
    return (normalized_song["title"].lower(), normalized_song["artist"])


def is_duplicate_song(new_song, existing_songs):
    """Return True if new_song is already in existing_songs."""
    new_song_identity = song_identity(new_song)
    return any(
        song_identity(existing_song) == new_song_identity
        for existing_song in existing_songs
    )


def add_song_sidebar():
    """Render the Add Song controls in the sidebar."""
    st.sidebar.header("Add a song")

    title = st.sidebar.text_input("Title")
    artist = st.sidebar.text_input("Artist")
    genre = st.sidebar.selectbox(
        "Genre",
        options=GENRE_OPTIONS,
    )
    energy = st.sidebar.slider("Energy", min_value=1, max_value=10, value=5)
    tags_text = st.sidebar.text_input("Tags (comma separated)")

    if st.sidebar.button("Add to playlist"):
        # Split "a, b, c" into separate tags and drop any empty ones.
        trimmed_tags = [tag.strip() for tag in tags_text.split(",")]
        tags = [tag for tag in trimmed_tags if tag]

        song: Song = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "energy": energy,
            "tags": tags,
        }
        # FIX: validate the normalized song, so a title or artist made only of
        # spaces is rejected instead of being saved as a blank entry.
        normalized_song = normalize_song(song)
        if not normalized_song["title"] or not normalized_song["artist"]:
            st.sidebar.warning("Enter both a title and an artist.")
            return

        # FIX: skip songs that are already in the list (same title and artist,
        # ignoring case and extra spaces) so totals count each song once.
        if is_duplicate_song(normalized_song, st.session_state.songs):
            st.sidebar.warning("That song is already in the playlist.")
            return

        # Store a new list (the old songs plus the new one) in session state.
        st.session_state.songs = st.session_state.songs + [normalized_song]


def playlist_tabs(playlists):
    """Render playlists in tabs."""
    include_mixed = st.session_state.profile.get("include_mixed", True)

    # The Mixed tab is only shown when the profile asks for it.
    tab_labels = ["Hype", "Chill"]
    if include_mixed:
        tab_labels.append("Mixed")

    tabs = st.tabs(tab_labels)

    for label, tab in zip(tab_labels, tabs):
        with tab:
            render_playlist(label, playlists.get(label, []))


def render_playlist(label, songs):
    """Render one playlist: its heading, artist search box, and song list."""
    st.subheader(f"{label} playlist")
    if not songs:
        st.write("No songs in this playlist.")
        return

    # Each tab gets its own search box (the key keeps them separate).
    search_query = st.text_input(
        f"Search {label} playlist by artist", key=f"search_{label}"
    )
    matching_songs = search_songs(songs, search_query, field="artist")

    if not matching_songs:
        st.write("No matching songs.")
        return

    # One bullet point per song.
    for song in matching_songs:
        mood = song.get("mood", "?")
        tags = ", ".join(song.get("tags", []))
        st.write(
            f"- **{song['title']}** by {song['artist']} "
            f"(genre {song['genre']}, energy {song['energy']}, mood {mood}) "
            f"[{tags}]"
        )


def lucky_section(playlists):
    """Render the lucky pick controls and result."""
    st.header("Lucky pick")

    mode = st.selectbox(
        "Pick from",
        options=["any", "hype", "chill"],
        index=0,
    )

    if st.button("Feeling lucky"):
        picked_song = lucky_pick(playlists, mode=mode)
        # None means the chosen playlist has no songs to pick from.
        if picked_song is None:
            st.warning("No songs available for this mode.")
            return

        st.success(
            f"Lucky song: {picked_song['title']} by {picked_song['artist']} "
            f"(mood {picked_song.get('mood', '?')})"
        )

        # Remember the pick so it shows up in the History section.
        st.session_state.history.append(picked_song)


def stats_section(playlists):
    """Render statistics based on the playlists."""
    st.header("Playlist stats")

    stats = compute_playlist_stats(playlists)

    # First row: song counts.
    total_column, hype_column, chill_column = st.columns(3)
    total_column.metric("Total songs", stats["total_songs"])
    hype_column.metric("Hype songs", stats["hype_count"])
    chill_column.metric("Chill songs", stats["chill_count"])

    # Second row: Mixed count and the calculated values.
    mixed_column, ratio_column, energy_column = st.columns(3)
    mixed_column.metric("Mixed songs", stats["mixed_count"])
    # FIX: show the hype ratio as a percentage of all songs.
    ratio_column.metric("Hype ratio", f"{stats['hype_ratio']:.0%}")
    energy_column.metric("Average energy", f"{stats['avg_energy']:.2f}")

    top_artist = stats["top_artist"]
    if top_artist:
        st.write(
            f"Most common artist: {top_artist} "
            f"({stats['top_artist_count']} songs)"
        )
    else:
        st.write("No top artist yet.")


def history_section():
    """Render the pick history overview."""
    st.header("History")

    history = st.session_state.history
    if not history:
        st.write("No history yet.")
        return

    # How many lucky picks came from each mood.
    picks_per_mood = history_summary(history)
    st.write("Recent picks by mood:", picks_per_mood)

    show_details = st.checkbox("Show full history")
    if show_details:
        for song in history:
            st.write(
                f"{song.get('mood', '?')}: {song['title']} by {song['artist']}"
            )


def clear_controls():
    """Render a small section for clearing data."""
    st.sidebar.header("Manage data")
    if st.sidebar.button("Reset songs to default"):
        st.session_state.songs = default_songs()
    if st.sidebar.button("Clear history"):
        st.session_state.history = []


def main():
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    st.title("Playlist Chaos")

    st.write(
        "An AI assistant tried to build a smart playlist engine. "
        "The code runs, but the behavior is a bit unpredictable."
    )

    # Sidebar: profile settings, the add-song form, and reset buttons.
    init_state()
    profile_sidebar()
    add_song_sidebar()
    clear_controls()

    profile = st.session_state.profile
    songs = st.session_state.songs

    # Sort every song into its mood playlist using the current profile.
    base_playlists = build_playlists(songs, profile)
    merged_playlists = merge_playlists(base_playlists, {})

    # Main page: playlists, lucky pick, stats, then pick history.
    playlist_tabs(merged_playlists)
    st.divider()
    lucky_section(merged_playlists)
    st.divider()
    stats_section(merged_playlists)
    st.divider()
    history_section()


if __name__ == "__main__":
    main()
