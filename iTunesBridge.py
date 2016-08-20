from Foundation import *
from ScriptingBridge import *

def init():
    global iTunes
    global currentTrack
    global currentTrackName
    global currentTrackGenre
    global currentTrackIndex
    global currentPlaylist
    global playlistCount
    global playlistTracks

    iTunes =  SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")
    currentPlaylist = iTunes.currentPlaylist()
    currentTrack = iTunes.currentTrack()
    currentTrackName = currentTrack.name
    currentTrackGenre = currentTrack.genre
    currentTrackIndex = currentTrack.index
    playlistTracks = currentPlaylist.tracks()
    playlistCount = playlistTracks.count

def getNextTracks(numTracks):
    index = currentTrackIndex()
    upcomingTracks = []

    while len(upcomingTracks) < numTracks and index < playlistCount():
        nextTrack = playlistTracks[index]
        if nextTrack.enabled():
            upcomingTracks.append(nextTrack)
        index +=1

    return upcomingTracks

def getNextTrack():
    cTindex = currentTrackIndex()
    if  cTindex < playlistCount():
        return playlistTracks[cTindex]
    else:
        return None