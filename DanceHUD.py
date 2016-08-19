import os
import sys
import codecs
import time
import sdl2
import sdl2.ext
import imghdr
import random

from ctypes import c_int, pointer, c_uint

import settings
import iTunesBridge as iTB
from GraphicsHelpers import *
from PresentationDisplay import PresentationDisplay, TextObject, ImageObject

def main():
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    # Initialize settings
    settings.init()

    # Setup iTunes ScriptingBridge
    iTB.init()

    # Setup SDL2
    initSDL2()

    # Setup presentation display
    presDisp = PresentationDisplay()

    # Create the song display window on a secondary display (if available)
    if sdl2.SDL_GetNumVideoDisplays() > 1:
        presDisp.setDisplay(1, True)
    else:
        presDisp.setDisplay(0, False)

    presDisp.setBackgroundColor(settings.BACKGROUND_COLOR)

    # Load font files
    currSongNameFont = loadFontFile(settings.CURR_SONG_NAME_FONT, presDisp.height * settings.CURR_SONG_NAME_SIZE)
    currSongGenreFont = loadFontFile(settings.CURR_SONG_GENRE_FONT, presDisp.height * settings.CURR_SONG_GENRE_SIZE)
    nextSongGenreFont = loadFontFile(settings.NEXT_SONG_GENRE_FONT, presDisp.height * settings.NEXT_SONG_GENRE_SIZE)

    # Dancer image for each song
    danceImg = ImageObject(presDisp.renderer, os.path.join(settings.DANCE_IMAGE_PATH, "Salsa_2.gif"))
    danceImgLoc = danceImg.dst
    danceImgLoc.x = 500

    # Current song name
    currSongName = TextObject(presDisp.renderer, "", currSongNameFont, color=settings.CURR_SONG_NAME_COLOR)
    currSongNameLoc = currSongName.dst
    currSongNameLoc.x = 300
    currSongNameLoc.y = 800

    # Current song
    currSongGenre = TextObject(presDisp.renderer, "", currSongGenreFont, color=settings.CURR_SONG_GENRE_COLOR)
    currSongGenreLoc = currSongGenre.dst

    # Next song genres
    nextSongGenres = []
    for x in range(0, settings.NUM_UPCOMING_SONGS):
        next = TextObject(presDisp.renderer, "", nextSongGenreFont, color=settings.NEXT_SONG_GENRE_COLOR)
        nextSongGenres.append(next)

    # New banner icons for songs
    newSongBanners = []
    for x in range(0, settings.NUM_UPCOMING_SONGS + 1):
        next_banner = ImageObject(presDisp.renderer, settings.NEW_SONG_BANNER_ICON)
        next_banner.dst.x = int(presDisp.width * settings.BORDER_PADDING_HORIZONTAL)
        newSongBanners.append(next_banner)

    # Upcoming songs view for projector
    upcoming_view = [danceImg, currSongName, currSongGenre]
    upcoming_view.extend(nextSongGenres)
    upcoming_view.extend(newSongBanners)
    presDisp.addObjects(upcoming_view)

    currSongState = []
    currSongID = ''
    lastUpdate = 0.0
    running = True

    # Main loop for DanceHUD
    while (running):
        # Handle user input and window events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.event == sdl2.SDL_WINDOWEVENT_CLOSE:
                    running = False
                    break
                elif event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                    presDisp.resizeWindow(event.window)
                    break
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
                    break

        # Should not happen unless user messes with the clock
        if time.time() < lastUpdate:
            lastUpdate = time.time()

        # Update the list of songs if enough time has passed since last update (or if currSongState is not initialized)
        if not currSongState or time.time() - lastUpdate > settings.UPDATE_TIME:
            currSongState = getSongState()

            # Update the displayed songs
            maxGenreWidth = updateUpcomingSongDisplay(currSongState, currSongName, currSongGenre, nextSongGenres, newSongBanners, danceImg, presDisp)

            # Check if the current song playing has changed
            if currSongState[0].persistentID() != currSongID:
                # Change image shown
                updateDanceImage(maxGenreWidth, currSongGenre.string, danceImg, presDisp)

                # If there is already a current song, crossfade when updating the display
                if currSongID != '':
                    if settings.ENABLE_CROSSFADE:
                        presDisp.crossfade_type = settings.CROSSFADE_TYPE
                        presDisp.beginCrossfade()
                currSongID = currSongState[0].persistentID()

                # Show a blank screen if no song is playing
                if not currSongID:
                    blankDisplay(currSongName, currSongGenre, nextSongGenres, newSongBanners, danceImg, presDisp)
            lastUpdate = time.time()

        # Render the display and show it on the screen
        presDisp.render()
        presDisp.present()

    # Shut down SDL2
    quitSDL2()

# Gets info for the current track and upcoming tracks
def getSongState():
    songState = []
    songState.append(iTB.currentTrack)
    songState.extend(iTB.getNextTracks(settings.NUM_UPCOMING_SONGS))
    return songState

# Blanks out all of the current song information and the list of upcoming songs
def blankDisplay(currSongName, currSongGenre, nextSongGenres, newSongBanners, danceImg, disp):
    currSongName.changeString(disp.renderer, "")
    currSongGenre.changeString(disp.renderer, "")
    for x in nextSongGenres:
        x.changeString(disp.renderer, "")
    for x in newSongBanners:
        x.changeVisible(False)

# Updates the displayed information
def updateUpcomingSongDisplay(songState, currSongName, currSongGenre, nextSongGenres, newSongBanners, danceImg, disp):
    maxGenreWidth = 0
    if iTB.currentPlaylist.name():
        # Updates the upcoming genre list
        maxGenreWidth = updateGenreList(songState, currSongGenre, nextSongGenres, newSongBanners, disp)

        # Updates the current song name shown
        updateSongName(songState, currSongName, maxGenreWidth, disp)

        # Updates visibility of new song banners
        for banner in newSongBanners:
            banner.changeVisible(False)
        for index, song in enumerate(songState):
            newSongBanners[index].changeVisible("check" in song.comment().lower())

        # Resizes the dance image to avoid overlap with the upcoming dance list
        resizeDanceImage(maxGenreWidth, danceImg, disp)
    return maxGenreWidth

# Updates the song genre list
def updateGenreList(songState, currSongGenre, nextSongGenres, newSongBanners, disp):
    maxGenreWidth = 0
    track_num = 0

    # Update the genre for the current track
    currSongGenre.changeString(disp.renderer, songState[track_num].genre())
    currSongGenre.dst.x = int(disp.width * settings.BORDER_PADDING_HORIZONTAL)
    currSongGenre.dst.y = int(disp.height * settings.BORDER_PADDING_VERTICAL) + currSongGenre.dst.h*track_num
    newSongBanners[track_num].dst.y =  int(currSongGenre.dst.y + disp.height*settings.BORDER_PADDING_VERTICAL)
    newSongBanners[track_num].changeVisible("check" in songState[track_num].comment().lower())
    maxGenreWidth = currSongGenre.dst.w

    # Updates the genre for upcoming tracks
    for next in nextSongGenres:
        track_num += 1
        if track_num < len(songState):
            next.changeString(disp.renderer, songState[track_num].genre())
            next.dst.x = int(disp.width * settings.BORDER_PADDING_HORIZONTAL)
            next.dst.y = int(disp.height * settings.BORDER_PADDING_VERTICAL) + next.dst.h*track_num
            newSongBanners[track_num].dst.y =  int(next.dst.y + disp.height*settings.BORDER_PADDING_VERTICAL)
            newSongBanners[track_num].changeVisible("check" in songState[track_num].comment().lower())
            maxGenreWidth = max(next.dst.w, maxGenreWidth)
        else:
            next.changeString(disp.renderer, "")

    return maxGenreWidth

# Updates the currently playing song name to display
def updateSongName(songState, currSongName, maxGenreWidth, disp):
    maxNameWidth = float(disp.width*13.0/16.0 - maxGenreWidth)
    currSongName.changeString(disp.renderer, songState[0].name())
    currSongName.dst.x = int(disp.width*1.0/16.0 + maxGenreWidth + disp.width*1.0/16.0 + (maxNameWidth-currSongName.dst.w)/2.0)
    currSongName.dst.y = int(disp.height*24.0/32.0)

# Changes the current dance image shown
def updateDanceImage(maxGenreWidth, currGenre, danceImg, disp):
    print os.getenv("HOME")
    imagepath = os.path.join(os.getenv("HOME"), "DanceHUD Settings", "image")
    print imagepath
    dirlist = os.listdir(imagepath)
    imagelist = listImages(imagepath)
    newImage = None

    for x in dirlist:
        if os.path.isdir(os.path.join(imagepath, currGenre)) and x == currGenre:
            # Only switch if Genre folder has images
            subdir_list = listImages(os.path.join(imagepath, currGenre))
            if subdir_list:
                imagepath = os.path.join(imagepath, currGenre)
                imagelist = os.listdir(imagepath)
            break

    if len(imagelist) > 1:
        # Remove current image from list
        for x in imagelist:
            if x == os.path.basename(danceImg.imagepath):
                imagelist.remove(x)
                break
        newImage = os.path.join(imagepath, imagelist[random.randint(0, len(imagelist)-1)])
    else:
        newImage = os.path.join(imagepath, imagelist[0])

    danceImg.changeImage(disp.renderer, newImage)
    resizeDanceImage(maxGenreWidth, danceImg, disp)

# Returns a list of images in a directory
def listImages(imagepath):
    filelist = os.listdir(imagepath)
    imagelist = []
    for x in filelist:
        if not (os.path.isdir(os.path.join(imagepath, x)) or x.startswith('.') or imghdr.what(os.path.join(imagepath, x)) is None):
            imagelist.append(x)
    return imagelist

# Resizes the dance image to constrain it to a maximum width
def resizeDanceImage(maxGenreWidth, danceImg, disp):
    maxImageWidth = float(disp.width*13.0/16.0 - maxGenreWidth)
    maxImageHeight = float(disp.height*23.0/32.0)
    imageWidth = float(danceImg.dst.w)
    imageHeight = float(danceImg.dst.h)

    if imageWidth  < 1 or imageHeight < 1:
        print "Bad Image: "
        print danceImg.imagepath
        return

    dstAspect = maxImageWidth/maxImageHeight
    srcAspect = imageWidth/imageHeight

    scalingFactor = 1
    if srcAspect < dstAspect:
        scalingFactor = maxImageHeight/imageHeight
    else:
        scalingFactor = maxImageWidth/imageWidth

    danceImg.dst.w = int(imageWidth*scalingFactor)
    danceImg.dst.h = int(imageHeight*scalingFactor)
    danceImg.dst.x = int(disp.width*1.0/16.0 + maxGenreWidth + disp.width*1.0/16.0 + (maxImageWidth-danceImg.dst.w)/2.0)
    danceImg.dst.y = int(disp.height*1/32 + (maxImageHeight - danceImg.dst.h)/2.0)


if __name__ == "__main__":
    main()