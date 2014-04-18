# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\Martin\.spyder2\.temp.py
"""

import web
from web import form
import spotimeta
import controller
import os
import csv
import random
render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/add/(.*)', 'add',
    '/search/', 'search',
    '/search/(.*)', 'search',
    '/images/(.*)', 'images'
)

myform = form.Form( 
    form.Textbox("Track"))

web.config.debug = False
app = web.application(urls, globals())          
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'urilist':[0]})     

def GetCurrentTrack():
    print 'GetCur'
    try:
        if(len(web.oldqueue) > 0):
            print web.oldqueue[-1]
            return web.oldqueue[-1]
        else:
            ret = {}
            ret['name'] = 'None'
            ret['artist'] = {}
            ret['artist']['name'] = 'None'
        return ret
    except:
        ret = {}
        ret['name'] = 'None'
        ret['artist'] = {}
        ret['artist']['name'] = 'None'
        return ret
        
def NextTrackCallback():
    if (len(web.songqueue) > 0):
        if (len(web.songqueue) < 10) and False:
            for i in range(0,10):
                num = random.randint(1,len(web.oldqueue))
                web.songqueue.append(web.oldqueue[num])
        try:
            with open('playlist.spl','w') as f:
                xmlw = csv.DictWriter(f, web.songqueue[0].keys())
                xmlw.writeheader()
                for elem in web.songqueue:
                    xmlw.writerow(elem)
        except:
            return
            
def ReadPlaylist():
    songs = []
    name = None
    if(os.path.isfile('std.spl')):
        name = 'std.spl'
    else:
        if(os.path.isfile('playlist.spl')):
            name = 'playlist.spl'
        else:
            return
        
    with open(name, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            elem = {}
            elem['artist'] = {}
            elem['name'] = row['name']
            temp = row['artist']
            temp = eval(temp)
            
            elem['artist']['name'] = temp['name']
            elem['href'] = row['href']
            elem['count'] = row['count']
            elem['track-number'] = row['track-number']
            elem['popularity'] = row['popularity']
            elem['ids'] = row['ids']
            elem['length'] = row['length']
            songs.append(elem)
    web.songqueue = songs
     
class index:
    GetCurrentTrack()  
    def GET(self):
        return render.index(GetCurrentTrack(), web.songqueue)
        

class add:
    
    def GET(self, songuri):
        track = None
        if songuri:
            print songuri
            try:
                track = spotimeta.lookup(str(songuri))
            except:
                return render.index(GetCurrentTrack(), web.songqueue)
            track['result']['href'] = songuri
            
            

            try:
                uris = session.get('urilist',[])
                if songuri in uris:
                    return render.add(track['result'],True)
                else:
                    # check if song already there -> upvote
                    self.AddToList(track['result'])  
                    web.songqueue.sort(key = lambda x: x['count']*-1)
                    session.urilist.append(songuri)   
                    return render.add(track['result'],False)
            except AttributeError:
                # check if song already there -> upvote
                self.AddToList(track['result'])  
                web.songqueue.sort(key = lambda x: x['count']*-1)
                session.urilist = []
                session.urilist.append(songuri)  
                return render.add(track['result'],False)
        else:
            return render.index(GetCurrentTrack(), web.songqueue)
        
            
    def AddToList(self, track):
        for elem in web.songqueue:
            if elem['name'] == track['name']:
                if elem['artist']['name'] == track['artist']['name']:
                    idx = web.songqueue.index(elem)
                    web.songqueue[idx]['count'] = int(web.songqueue[idx]['count']) + 1
                    return
        #not found
        track['count'] = 1
        web.songqueue.append(track)  
    
    
class search:
  
    def GET(self):
        formObj = myform()
        result = None
        return render.search(formObj, result)
        
    def POST(self):
        formObj = myform()
        result = None
        if not formObj.validates():
            return render.index(GetCurrentTrack() , web.songqueue)
        else:
            result = spotimeta.search_track(formObj['Track'].value)
            return render.search(formObj, result['result'])


class images:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"            }

        if name in os.listdir('images'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()
            

        
        
if __name__ == "__main__":
    web.internalerror = web.debugerror
    web.config.debug = False
    web.songqueue = []
    web.oldqueue = []
    ReadPlaylist()
    controller = controller.SpotifyController(NextTrackCallback)
    controller.start()
    
    app.run()