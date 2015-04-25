#!/usr/bin/python

import operator
import subprocess
import os
import sys
from PIL import Image
from operator import itemgetter
import pickle
from colortrans import *

##TODO LIST##
#1587 x 994 -- exacttimbers.jpg
#resize the image at the beginning of operation

#----PYTHON WAY



#1600 width pixels / 23 boxes = 69 width pixels/box / 6 tmuxels = 11
#1000 height pixels / 14 boxes = 71 height pixels/ box / 3 = 23
#1587 pixels / 23 boxes = 69 / 6
#box = {}
#img = "/Users/aarntz/Documents/thesis/tmuximgtests/exacttimbers.jpg"
#img = "/Users/aarntz/Documents/thesis/tmuximgtests/timbers.jpg"
#img = "/Users/aarntz/Documents/thesis/tmuximgtests/Ducky_Head_Web_Low-Res.jpg"
img = "/Users/aarntz/Documents/thesis/tmuximgtests/vangogh.jpg"

def calculateResizeVals(numwpix, numhpix, numwboxes, numhboxes):
    wpixperbox = numwpix / numwboxes
    print wpixperbox
    hpixperbox = numhpix / numhboxes
    print hpixperbox


def loadPic(imagefile):
    img = Image.open(imagefile) #Can be many different formats.
    pix = img.load()
    return {'pixels':pix, 'size': img.size}

def buildBoxTmuxelDict(boxnum,sizes):
    #box = {boxnum: {}}
    box = {}
    startpixelx = (boxnum[0] * sizes[0])
    startpixely = (boxnum[1] * sizes[1])
    indexhelper = sizes[0] / sizes[2]

    #print "startpixelx: %s" % startpixelx
    #print "startpixely: %s" % startpixely
    blockarr = makeOneTmuxelBlockArray(startpixelx, startpixely, sizes)
    #print blockarr
    for i in blockarr:
        if blockarr.index(i) < 6:
            tmuxelindexx = blockarr.index(i)
        else:
            tmuxelindexx = blockarr.index(i) % indexhelper
        tmuxelindexy = blockarr.index(i) / indexhelper
        box[tmuxelindexx, tmuxelindexy] = getColorAverageForBlock(i,sizes[2], sizes[3])
    return box

def getColorAverageForBlock(pixelxy, w, h):
    arr = buildPixelArray(pixelxy[0], pixelxy[1], w, h)
    clr = convertPixArrayToColorArray(arr)
    avg = averageColorOfColorArray(clr)
    #print "The average color for block %s is: %s" % (pixelxy, avg)
    return avg

def averageColorOfColorArray(colorarray):
    container = (0,0,0)
    for i in colorarray:
        container = tuple(map(operator.add, container, i))
    #print "The sum of the RGBs is: %s" %  (container,)
    avg = tuple([x/len(colorarray) for x in container])
    #print "The average color for these pixels: %s" % (avg,)
    #print  len(colorarray)
    hexavg = '%02x%02x%02x' % avg
    colorstring = convertHextoExportString(hexavg)
    return colorstring

def convertPixArrayToColorArray(pixelarray):
    global pix
    container = []
    for i in pixelarray:
        container.append(pix[i[0], i[1]])
    return container

def buildPixelArray(startpixelx, startpixely, w, h):
    container = []
    endpixelx = startpixelx + (w-1)
    endpixely = startpixely + (h-1)
    for i in range(startpixelx, (endpixelx + 1)):
        for j in range(startpixely, (endpixely + 1)):
            container.append([i,j])
    return container

def calculatePixelNums(numboxesw, numboxesh, tmuxpixx, tmuxpixy):
    global size
    boxw = size[0] / numboxesw
    boxh = size[1] / numboxesh
    #print boxw, boxh
    pixx = boxw / tmuxpixx
    pixy = boxh / tmuxpixy
    #print pixx, pixy
    print [boxw,boxh,pixx,pixy]
    return [boxw,boxh,pixx,pixy]

def makeOneTmuxelBlockArray(startpixx, startpixy, pixsizearr):
    container = []
    for i in range(startpixx, startpixx + (pixsizearr[0]-pixsizearr[2]), pixsizearr[2]):
        for j in range(startpixy, startpixy + (pixsizearr[1]-pixsizearr[3]), pixsizearr[3]):
            container.append([i,j])
    print "Tmuxel Block Array: " + str(container)
    return sorted(container, key=itemgetter(1))

def buildTmuxelBoxArray(numboxesw, numboxesh):
    container = []
    for i in range(0, numboxesw):
        for j in range(0, numboxesh):
            container.append((i,j))
    #print "Tmuxel Box Array: " + str(container)
    return container

def buildWholeScreenDict(numboxesw, numboxesh, sizes):
    container = {}
    boxes = buildTmuxelBoxArray(numboxesw, numboxesh)
    #print "Boxes" + str(boxes)
    for i in boxes:
        container[i] = buildBoxTmuxelDict(i, sizes)
    #print "Box global: " + str(container)
    return container

def convertHextoExportString(hexcolor):
    if len(hexcolor) < 4 and int(hexcolor) < 256:
        rgb = short2rgb(hexcolor)
        colorstring = '\[\\033[38;5;%sm\]*' % hexcolor
        #sys.stdout.write('xterm color \033[38;5;%sm%s\033[0m -> RGB exact \033[38;5;%sm%s\033[0m' % (hexcolor, hexcolor, hexcolor, rgb))
        #sys.stdout.write("\033[0m\n")
    else:
        short, rgb = rgb2short(hexcolor)
        #print short, rgb
        #colorstring = '\\033[38;5;%sm*' % short
        colorstring ='\[\\033[38;5;%sm\]*' % short
        #print '\033[38;5;%sm' % short
        #sys.stdout.write('RGB %s -> xterm color approx \033[38;5;%sm*' % (hexcolor, short))
        #sys.stdout.write("\033[0m\n")
    return colorstring


pic = loadPic(img)
pix = pic['pixels']
size = pic['size']
sizes = calculatePixelNums(23, 14, 6, 3)
box = buildWholeScreenDict(23, 14, sizes)

if __name__ == '__main__':
    print sizes
    print "Picture Details: " + str(size)
    testbox = buildBoxTmuxelDict((0,0), sizes)
    print testbox
    #calculateResizeVals(size[0], size[1], 23, 14)
    #print box[(0,0)]
    #str = convertHextoExportString('43413e')
    #print str
    #box = buildWholeScreenDict(23, 14, sizes)
    #print box[(0,3)][(0,0)] + box[(0,3)][(5,0)]
    #with open('./timbers.pickle', 'wb') as handle:
        #pickle.dump(box, handle)

def avgColorOfPixels(*arg):
    print "avgColorOfPixels called with", len(arg), "arguments:", arg
    holder = (0,0,0)
    for i in range(len(arg)):
        holder = tuple(map(operator.add, holder, arg[i]))
    print "The sum of the RGBs is: %s" %  (holder,)

    avg = tuple([x/len(arg) for x in holder])
    print "The average color for these pixels: %s" % (avg,)
    return avg


#avgColorOfPixels((10,10,12),(5,5,7))


###Pseudo Code

#-----IMAGE MAGICK WAY

###Convert image into big tiles
def makeTiles(imagefile, w, h):
    img = imagefile.split('.')[0]
    subprocess.call(['convert', imagefile, "-crop", w+'x'+h, \
                    './tiles/' + img + '_%04d.jpg'])
    #removeTilesNotSized(w, h)


###Remove unwanted tiles
def removeTilesNotSized(w, h):
    checkstr = w+'x'+h
    print "checkstr: %s" % checkstr

    for img in os.listdir('./tiles'):
        p = subprocess.Popen(['identify', '-format', "%[fx:w]x%[fx:h]",\
                                 img], cwd='./tiles', stdout=subprocess.PIPE)

        check = p.communicate()[0]
        print "check: %s" % check
        if check != checkstr:
            print "removing tile..."
            rm =  subprocess.Popen(['rm', img], cwd='./tiles')
            rm.wait()

#def splitemup():
    #for tile in os.listdir('./'):
        #if tile.startswith('tile'):
            #makeTiles(tile, '11', '23')

#Convert to big tiles

#Convert to small tiles

#Analyze small tiles for average color value

#Build Prompt

#makeTiles('timbers.jpg', '69', '71')
#removeTilesNotSized('69', '71')

#makeTiles('timbers.jpg', '69', '71')
#removeTilesNotSized('69', '71')
#removeTilesNotSized('tiletimbers', '69', '71')

#splitemup()
#removeTilesNotSized('69', '71', '11', '23')

#for tile in os.listdir('./'):
    #makeTiles(
