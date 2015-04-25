#!/usr/bin/python

import sys
import subprocess
import shlex
import pickle
from processimage import *
###TODO LIST###


#Get terminal size
def get_terminal_size_tput():
    try:
        cols = int(subprocess.check_output(shlex.split('tput cols')))
        rows = int(subprocess.check_output(shlex.split('tput lines'))) - 1
        return (cols, rows)
    except:
        pass

#Get pane size
def get_pane_size(hsplits, vsplits):
    w,h = get_terminal_size_tput()
    panex = (w - (int(hsplits)-1)) / int(hsplits)
    paney = (h - (int(vsplits)-1)) / int(vsplits)
    return (panex, paney)

#Build PS1
#Modify this function to take a tmux box value (0,0) or (0,1)
def buildPS1(boxtuple, width, height):
    global box
    tmuxels = tmuxarray(width, height)
    #print tmuxels
    #ps1=" " + "*" * (width-2) + " \n"
    ps1 =" "
    for i in tmuxels:
        if ((tmuxels.index(i) + 1) % (width-2)) == 0 and (i != tmuxels[-1]):
            #print box[boxtuple]
            #print box[boxtuple][i]
            try:
                ps1+= box[boxtuple][i] + " \n "
            except:
                ps1+="* \n "
        else:
            try:
                ps1 +=box[boxtuple][i]
            except:
                ps1 +="*"
    return ps1
    #for i in range(height-2):
        #ps1+=" " + "*" * (width-2) + " \n"
    #ps1+=" " + "*" * (width-2)
    #return ps1

def tmuxarray(w, h):
    tmuxels = buildTmuxelBoxArray(w-2, h)
    return sorted(tmuxels, key=itemgetter(1))

#Create tmux session
def createTmux():
    subprocess.call(['tmux', '-2', 'new-session', '-d', '-n', '"tmuxtest"'])


#Horizontal splits
def splitHorizontal(hsplits):
    x, y = get_pane_size(sys.argv[1], sys.argv[2])
    #x = x/2
    for i in range(int(hsplits)-1):
        subprocess.call(['tmux', 'split-window', '-d', '-h', '-l', str(x), '-t', '0'])

#Calculate Even Splits for Window size
def calc_even_splits():
    w,h = get_terminal_size_tput()
    for i in range(1,30):
        if ((w - (i - 1)) % i) == 0:
            print 'Try ' + str(i) + ' Hsplits.'
        if ((h - (i - 1)) % i) == 0:
            print 'Try ' + str(i) + ' Vsplits.'

#Vertical Splits
def splitVertical(vsplits):
    x, y = get_pane_size(sys.argv[1], sys.argv[2])
    for j in range(0, (int(sys.argv[1]) * int(sys.argv[2])) - 1, int(vsplits)):
        #print j
        for k in range(int(vsplits) - 1):
            #print k
            if (j == 0):
                l = 0
            else:
                l = j + k

            subprocess.call(['tmux', 'split-window', '-v', '-l', str(y), '-t', str(l)])


def fillpanes():
    w,h = get_pane_size(sys.argv[1],sys.argv[2])
    numpanes = int(int(sys.argv[1]) * int(sys.argv[2]))
    for i in range(numpanes):
        index = paneNumToIndex[i]
        ps1 = buildPS1(index, w, h)
        #print ps1
        bash = 'PS1="'+ps1+'"'
        #bash = 'PS1=`echo -e "' + ps1 + '"`'
        print index,bash
        subprocess.call(['tmux', 'select-pane','-t', str(i)])
        #subprocess.call(['tmux', 'send-keys', '-t', str(i), 'clear', 'Enter'])
        subprocess.call(['tmux', 'send-keys', '-t', str(i), bash, 'Enter'])
        #subprocess.call(['tmux', 'clear-history', '-t', str(i)])
        subprocess.call(['tmux', 'send-keys', '-t', str(i), 'clear', 'Enter'])

def tmuxattach():
    subprocess.call(['tmux', 'attach'])

def createPaneDicts(boxesw, boxesh):
    numpanes = int(boxesw) * int(boxesh)
    print "total panes: %s" % numpanes
    paneNumDict = {}
    boxes = tmuxarray(int(boxesw) + 2, int(boxesh))
    for i in boxes:
        #print i
        if i[0]==0 and i[1]==0:
            #print "(0, 0) found"
            paneNumDict[i] = int(0)
        if i[1]==0 and i[0]!=0:
            #print "first row"
            paneNumDict[i] = (numpanes - int(boxesw)) + i[0]
        else:
            paneNumDict[i] = ((i[0] + 1) * int(boxesh)) - (i[0] + i[1])
    paneNumDict[(0,0)] = 0
    return paneNumDict

def createReverseLookup(dict):
    numPaneToIndex = {}
    for k, v in dict.items():
        numPaneToIndex[v] = k
    return numPaneToIndex

def createDicts(boxesw, boxesh):
    iToPaneNum = createPaneDicts(boxesw, boxesh)
    paneNumToIndex = createReverseLookup(iToPaneNum)
    return iToPaneNum, paneNumToIndex

if __name__ == "__main__":
    iToPaneNum, paneNumToIndex = createDicts(sys.argv[1], sys.argv[2])
    #print paneNumToIndex[13]
    #pd = createPaneDicts(sys.argv[1], sys.argv[2])
    #print pd
    #with open('timbers.pickle', 'rb') as handle:
        #box = pickle.load(handle)
    sizex, sizey = get_terminal_size_tput()
    print  'width =', sizex, 'height =', sizey
    #w,h = get_pane_size(sys.argv[1],sys.argv[2])
    ##print w,h
    ##buildPS1((0,0), w, h)
    ##ps1 = buildPS1((7,0), w, h)
    ##print ps1
    panex, paney = get_pane_size(sys.argv[1], sys.argv[2])
    print 'panex =',panex, 'paney =', paney
    createTmux()
    ##calc_even_splits()
    splitHorizontal(sys.argv[1])
    splitVertical(sys.argv[2])
    fillpanes()
    tmuxattach()
