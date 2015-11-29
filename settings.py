import os
from sdl2 import SDL_Color

def init():
    global NUM_UPCOMING_SONGS
    global UPDATE_TIME

    global CURR_SONG_NAME_FONT
    global CURR_SONG_GENRE_FONT
    global NEXT_SONG_GENRE_FONT

    global CURR_SONG_NAME_SIZE
    global CURR_SONG_GENRE_SIZE
    global NEXT_SONG_GENRE_SIZE

    global COLOR_THEME

    global CURR_SONG_GENRE_COLOR
    global CURR_SONG_NAME_COLOR
    global NEXT_SONG_GENRE_COLOR
    global BACKGROUND_COLOR

    global DANCE_IMAGE_PATH

    global BORDER_PADDING_HORIZONTAL
    global BORDER_PADDING_VERTICAL

    global CROSSFADE_DURATION
    global CROSSFADE_TYPE
    global ENABLE_CROSSFADE

    NUM_UPCOMING_SONGS = 4

    UPDATE_TIME = 0.75

    # Available fonts are Noto<Serif/Sans>-<Regular/Italic/Bold>.ttf and Glametrix.otf
    CURR_SONG_NAME_FONT = os.path.join(os.getcwd(), "font", "Glametrix.otf")
    CURR_SONG_GENRE_FONT = os.path.join(os.getcwd(), "font", "NotoSerif-Bold.ttf")
    NEXT_SONG_GENRE_FONT = os.path.join(os.getcwd(), "font", "NotoSerif-Bold.ttf")

    CURR_SONG_NAME_SIZE = 3.0 / 32.0
    CURR_SONG_GENRE_SIZE = 13.0 / 128.0
    NEXT_SONG_GENRE_SIZE = 13.0 / 128.0

    COLOR_THEME = 'DARK'

    if COLOR_THEME == 'LIGHT':
        CURR_SONG_GENRE_COLOR = SDL_Color(255, 75, 75)
        CURR_SONG_NAME_COLOR = SDL_Color(175, 175, 175)
        NEXT_SONG_GENRE_COLOR = SDL_Color(15, 15, 15)
        BACKGROUND_COLOR = SDL_Color(255, 255, 255)
    elif COLOR_THEME == 'DARK':
        CURR_SONG_GENRE_COLOR = SDL_Color(255, 75, 75)
        CURR_SONG_NAME_COLOR = SDL_Color(165, 165, 165)
        NEXT_SONG_GENRE_COLOR = SDL_Color(215, 215, 215)
        BACKGROUND_COLOR = SDL_Color(0, 0, 0)

    DANCE_IMAGE_PATH = os.path.join(os.getenv("HOME"), "DanceHUD Settings", "image")

    BORDER_PADDING_HORIZONTAL = 1.0 / 16.0
    BORDER_PADDING_VERTICAL = 1.0 / 32.0

    # Types of crossfades - 'OutIn', 'Cross', 'Sine'
    CROSSFADE_TYPE = 'Cross'
    CROSSFADE_DURATION = 0.7
    ENABLE_CROSSFADE = True


