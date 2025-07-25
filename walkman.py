from colorama import Fore, Style, init
from gtts import gTTS
import os
# hides pygame support message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import keyboard
import youtube_dl
import threading
import discord
import time
from mutagen.mp3 import MP3
from msvcrt import getch
from colorama import Fore, Style, init
from gtts import gTTS
from playsound import playsound
from pypresence import Presence

########################################################################
# CHANGE THIS DIRECTORY TO THE LOCATION YOU WOULD LIKE YOUR MUSIC TO BE#
########################################################################

dir = r"D:\Projects\Walkman\music"                          
                                                                       
########################################################################
# CHANGE THIS DIRECTORY TO THE LOCATION YOU WOULD LIKE YOUR MUSIC TO BE#
########################################################################

# list of all song names
songs = []

# used for text to speech to fix same filename bug
count = 0

playingSong = ""
paused = True
text = None
lock = False

# CHANGE CLIENT ID FOR RICH PRESENCE #
client_id = ""
RPC = Presence(client_id)
RPC.connect()
# CHANGE CLIENT ID FOR RICH PRESENCE #

# initiates pygame
pygame.mixer.init()
pygame.mixer.music.set_volume(.05)

def spacePrint(text):
    print('\n')
    print(text)

def greenPrint(text):
    spacePrint(Fore.GREEN + text)
    print(Style.RESET_ALL)

def redPrint(text):
    spacePrint(Fore.RED + text)
    print(Style.RESET_ALL)
    
# plays a custom text to speech message
def textToSpeech(textSpeech):
    # global gets the global variable
    global count
    fileName = 'speech' + str(count)
    speech = gTTS(text=textSpeech, lang='en', slow=False)
    # adds the count to the save file so text to speech doesnt glitch after multiple
    # attempts
    # str(count) converts int to string
    speech = speech.save(fileName + '.mp3')
    # loads the sound into pygame mixer
    pygame.mixer.music.load(fileName + '.mp3')
    # adjusts the sound volume and plays it
    pygame.mixer.music.play()
    # adds one to count to prevent giving the same name to a file twice
    count += 1

def getStrippedDirectory(dir):
    # gets stripped by splitting the head and tail of basename
    (stripped, tail) = os.path.splitext(os.path.basename(dir))
    return stripped

# plays a song based on the file argument
def playSong(name):
    global playingSong
    # global variable
    global dir
    # 'r' before fixes unicode error
    path = r"" + dir + "\\" + name + ".mp3"
    # prints playing song
    greenPrint('Now playing: ' + name + '.')
    playingSong = name
    # loads and play music
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

# loops through the music folder and returns all mp3 files and stores it in the songs dictionary
def getMusicFiles():
    # gets the global variable of songs
    global songs
    # loops through the music folder
    for file in os.listdir(dir):
        if file.endswith('.mp3'):
            # updates the dictionary with the directory of the song and the name
            songs.append(getStrippedDirectory(file))

def songLength(song):
    audio = MP3(dir + '/' + song + '.mp3')
    return time.time() + audio.info.length

def printSongs():
    print('\n')
    for song in songs:
        print(song)
    print('\n')

# reloads the music files
def reload():
    # clears the music list to prevent multiple copies of the same song
    songs.clear()
    # finds all music files again
    getMusicFiles()

def printCommands():
    print('\n______________________________ Commands ________________________________\n'
    'resume          resumes the stopped song\n'
    'stop            stops the current song\n'
    'list            lists all available songs\n'
    'reload          reloads the music list to detect for new songs\n'
    'play <song>     starts playing music from the specified song\n'
    'download <link> downloads the audio from a youtube video and stores\n'
    '                in it the music folder\n'
    'volume <amount> sets the volume to the specified amount (0 - 100)\n'
    '________________________________________________________________________\n\n')

def updateSong():
    global paused
    global playingSong
    # replays the song by default
    if pygame.mixer.music.get_busy() == 0 and paused is False:
        pygame.mixer.music.play()
    elif pygame.mixer.music.get_busy() == 1 and paused is True:
        RPC.update(details="Currently paused:", state=playingSong, large_image='walkman2', small_image='walkman_icon', large_text=playingSong)
    elif pygame.mixer.music.get_busy() == 1:
        RPC.update(details="Playing song:", state=playingSong, large_image='walkman2', small_image='walkman_icon', large_text=playingSong, end=songLength(playingSong) - pygame.mixer.music.get_pos() / 1000)


            

def main():
    # initiates colorama
    init()

    # loads the music files into the dictionary
    getMusicFiles()
    
    # plays a welcome message
    # textToSpeech('Welcome to walkman')
    
    # gets the global variable of songs and directory
    global songs
    global dir
    global paused
    global text
    
    while True:
        updateSong()
        
        if text:
            # converts to lower case which is equivalent to ignore case
            if text.lower() == 'resume':
                # resumes stopped music
                if (pygame.mixer.music.get_busy()):
                    paused = False
                    pygame.mixer.music.unpause()
                    greenPrint('Resumed the paused music!')
                else:
                    redPrint('No music is currently playing!')
            elif text.lower() == 'stop':
                # stop music
                if (pygame.mixer.music.get_busy()):
                    paused = True
                    pygame.mixer.music.pause()
                    greenPrint('Stopped playing music!')
                else:
                    redPrint('No music is currently playing!')
            elif text.lower() == 'list':
                # lists all available songs
                greenPrint('Available Songs:')
                printSongs()
            # uses starts with because this command requires the song arg
            elif text.lower() == 'reload':
                reload()
                greenPrint("Reloaded the music list! Use 'list' to check for new songs!")
            elif text.lower().startswith('play '):
                # play music based on arg
                # song is the arguments in the play command
                song = text[5:]
                # filters out songs that contain the arguments
                filtered = filter(lambda x: song.lower() in x.lower(), songs)
                # converts filtered to a list to check if its empty
                filteredList = list(filtered)
                if filteredList:
                    # gets the first filtered song from the lambda and plays it
                    selectedSong = filteredList[0]
                    playSong(selectedSong)
                    paused = False
                else:
                    # if no song is found prints error
                    redPrint("No song was found! Use 'list' to check for available songs!")
            # uses starts with because this command requires the song arg
            elif text.lower().startswith('download '):
                # downloads youtube audio from the link
                # gets the argument of the command
                link = text[9:]
                # sets the options for youtube-dl
                ydl_opts = {
                    'format': 'best/bestaudio',
                    'outtmpl': dir + '\%(title)s.%(ext)s',
                    'no_warnings': True,
                    'quiet': True,
                    'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
                }                   
                # downloads audio
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    try:
                        greenPrint('Downloading...')
                        ydl.download([link])
                    except youtube_dl.DownloadError as e:
                        continue
                # reloads music files
                reload()
                greenPrint('Sucessfully downloaded the song from ' + link + ' and reloaded the music files!')
            # uses starts with because this command requires the song arg
            elif text.lower().startswith('volume '):
                # checks if music is playing
                if (pygame.mixer.music.get_busy()):
                    # gets the volume inputted
                    volumeText = text[7:]
                    # checks if the variable is an integer
                    if volumeText.isdigit():
                        # converts the volumeText to an integer
                        volume = int(volumeText)
                        # checks if the volume is betwen 0 and 100
                        if volume >= 0 and volume <= 100:
                            # sets the volume
                            if (volume == 0):
                                pygame.mixer.music.set_volume(0)
                                greenPrint('Volume set to 0!')
                            else:   
                                pygame.mixer.music.set_volume(volume / 100)
                                greenPrint('Volume set to ' + volumeText + '!')
                        else:
                            # sends if volume isnt between 1 and 100
                            redPrint('The volume must be between 0 and 100!')
                    else:
                        # sends if the text inputted isn't an int
                        redPrint('You must input an integer between 0 and 100!')
                # errors if music isnt playing                        
                else:
                    redPrint('Music must be playing to adjust volume!')
            printCommands()
            text = None    
        else:
            # if the sender enters a blank input just continues to prevent error
            text = None

# seperate thread to detect input without pausing the entire main thread
def inputThread():
    global text
    
    while True:
        text = input()

if __name__ == "__main__":  
    print(' __     __     ______     __         __  __     __    __     ______     __   __    ')
    print('/\ \  _ \ \   /\  __ \   /\ \       /\ \/ /    /\ "-./  \   /\  __ \   /\ "-.\ \   ')
    print('\ \ \/ ".\ \  \ \  __ \  \ \ \____  \ \  _"-.  \ \ \-./\ \  \ \  __ \  \ \ \-.  \  ')
    print(' \ \__/".~\_\  \ \_\ \_\  \ \_____\  \ \_\ \_\  \ \_\ \ \_\  \ \_\ \_\  \ \_\\"\_\ ')
    print('  \/_/   \/_/   \/_/\/_/   \/_____/   \/_/\/_/   \/_/  \/_/   \/_/\/_/   \/_/ \/_/ ')
    print('                                                                                   ')

    threading.Thread(target = inputThread).start()
    printCommands()
    main()

