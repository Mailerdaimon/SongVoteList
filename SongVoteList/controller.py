# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 11:55:06 2014

@author: Martin
"""

import spotify_remote, time, threading, server

class SpotifyController(threading.Thread):
    currentSong = None
    remote = None
    newTrackCallback = None
    def __init__(self, newTrackCallback):      
        print 'controller'
        threading.Thread.__init__(self)
        self.newTrackCallback = newTrackCallback
        self.remote = spotify_remote.SpotifyRemote()
        self.remote.handshake()
        track = self.GetNextSong()
        if track != 'pause':
            self.remote.play(track['href'])
            self.currentSong = track

            
        
    def run(self):       
        while True:
            try:
                status = self.remote.status()
                playPos = float(status['playing_position'])
                length = float(status['track']['length'])
                if(length - playPos <= 1.5):
                    track = self.GetNextSong()
                    print 'next track:', track
                    while track == 'pause':
                        time.sleep(1)
                        track = self.GetNextSong()
                    self.remote.play(track['href'])
                    self.currentSong = track
                    time.sleep(1)
                else:
                    time.sleep(0.3)
            except: 
                time.sleep(0.3)
                
    def GetNextSong(self):
        print 'next song'
        try:
            currentSong = server.web.songqueue.pop(0)
        except IndexError:
            print 'index error'
            currentSong = 'pause'
        server.web.oldqueue.append(currentSong)
        self.newTrackCallback()
        return currentSong