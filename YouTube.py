
### START BOILERPLATE CODE

# Sample Python code for user authorization

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0" 

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("youtube-api-snippets-oauth2.json")
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  return build(API_SERVICE_NAME, API_VERSION,
      http=credentials.authorize(httplib2.Http()))


args = argparser.parse_args()
service = get_authenticated_service(args)

def print_results(results):
  print(results)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      # Convert a name like "snippet.tags[]" to snippet.tags, but handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True
      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

### END BOILERPLATE CODE

# Sample python code for search.list for YouTube API

def parse_resutls(results,Search_Type):
  '''
  This code will collect the videoids, channelIds, playlist ids in search results
  '''
  k = results.keys()
  nextPageToken = results.get('nextPageToken')
  m = results['items']
  videolist = []
  channellist = []
  playlist = []
  misc =[]

  if(Search_Type =="Playlist"):
    for l in range(len(m)):
      videolist.append(m[l]['contentDetails']['videoId'])
      print m[l]['contentDetails']['videoId']
  else:
      for l in range(len(m)):
        if('videoId' in m[l]['id'].keys()):
          videolist.append(m[l]['id']['videoId'])
        elif('playlistId' in m[l]['id'].keys()):
          playlist.append(m[l]['id']['playlistId'])
        elif('channelId' in m[l]['id'].keys()): 
          channellist.append(m[l]['id']['channelId'])
        else:
          mis.append(m[l]['id'])
  return(videolist, channellist, playlist,misc, nextPageToken)

def Search(service, Search_Type, **kwargs):
  '''
  This code is copied from sample example on https://developers.google.com/youtube/v3/docs/playlistItems/list 
  '''
  kwargs = remove_empty_kwargs(**kwargs) # See full sample for function
  results = service.playlistItems().list(
    **kwargs
  ).execute()
  return(parse_resutls(results,Search_Type))

# Below code will print out videos list, play list and channel list

def search_word(wordsearch , nextpage = False):
  videolist=[]
  playlist=[]
  misclist =[]
  channellist = []

  v,p,c,m,n = Search(service,
      part='snippet',
      maxResults=50, type='id',
      q=wordsearch
      )
  videolist.append(v)
  playlist.append(p)
  channellist.append(c)
  misclist.append(m)
  if(nextpage == True):
    while(n):
      v,p,c,m,n = Search(service,
        part='snippet',
        maxResults=50,
        q='Justin Bieber',
        pageToken = n,
        type='id')
      videolist.append(v)
      playlist.append(p)
      channellist.append(c)
      misclist.append(m)

  print "videos"
  print videolist
  print "playlist"
  print playlist
  print "channels"
  print channellist
  print "misc"
  print misclist
  return(videolist,playlist,channellist,misclist)


def General_Search(nextpage = False, Search_Type = "Playlist", *args, **kwargs):
  '''
  This function will create list of videoids, playlists, channellist 
  When nextpage is set to True, this function will bring all the videos until nextPageToken is False
  Search_Type = "Playlist" or "KeyWord" - YouTube API will return different JSONs to parse 

  '''
  videolist=[]
  playlist=[]
  misclist =[]
  channellist = []

  v,p,c,m,n = Search(service,Search_Type, *args, **kwargs)
  videolist.append(v)
  playlist.append(p)
  channellist.append(c)
  misclist.append(m)
  if(nextpage == True):
    while(n):
      v,p,c,m,n = Search(service,*args, **kwargs)
      videolist.append(v)
      playlist.append(p)
      channellist.append(c)
      misclist.append(m)

  print "videos"
  print videolist
  print "playlist"
  print playlist
  print "channels"
  print channellist
  print "misc"
  print misclist
  return(videolist,playlist,channellist,misclist)




def search_playlist(PlayListID):
  '''
  Given a user's playlistID - This function will return all videoIds in the playlist
  '''
  return(General_Search(service,
      part='snippet,contentDetails',
      maxResults=50,
      playlistId=PlayListID))


def download(VideoList, FilePath,File_Type):
  '''  
  Given VideoList, FilePath and File_Type -- This Funciton will you pytube to download the file
  '''
  from pytube import YouTube
  for i in range(len(VideoList)):
    for vid in VideoList[i]:
      url = "http://www.youtube.com/watch?v="+vid
      try:
        yt = YouTube(url)
        video = yt.get(File_Type)
        video.filename
        video.download(FilePath)
      except:
        print "Could not downlod this video ", vid

def main():
  playlist_string = ""
  FilePath = ''
  File_Type = "mp4"
  # search_word('KeyWord')  
  VideoList = search_playlist(playlist_string)
  VideoList = [item for sublist in VideoList for item in sublist]
  download(VideoList,FilePath, File_Type)

if __name__ == "__main__":
    main()