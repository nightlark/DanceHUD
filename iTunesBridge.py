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
    cTindex = currentTrackIndex()
    upcomingTracks = playlistTracks[cTindex:(cTindex+numTracks)]
    replacementTracksNeeded = 0
    for x in upcomingTracks:
        if not x.enabled():
            upcomingTracks.remove(x)
            replacementTracksNeeded += 1

    index = cTindex + numTracks

    while replacementTracksNeeded > 0 and index < playlistCount():
        nextTrack = playlistTracks[index]
        if nextTrack.enabled():
            upcomingTracks.append(nextTrack)
            replacementTracksNeeded -= 1
        index +=1

    return upcomingTracks

def getNextTrack():
    cTindex = currentTrackIndex()
    if  cTindex < playlistCount():
        return playlistTracks[cTindex]
    else:
        return None