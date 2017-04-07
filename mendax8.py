# Mendax
# Catalogue utility.
# Catalogues downloaded from Vizier.
version = '8'
# Changed to use single HIP file, not to bother with searching by luminosity.

import math
import time

# Longitudes running anticlockwise with 0 degrees towards the centre.
# Lack of distance figures for HD stars is a major problem for directed searches, but then the HIP ones aren't a close match to Elite anyway.

# Lists
# Files to read from.
##HIPfiles = ['hip abf.csv','hip gk.csv','hip mo.csv']
HIPfiles = ['hip v2.csv'] # New consolidated version of the HIP catalogue.
##HDfiles = ['hd cat.csv','hd ec2.csv'] # hd ec2 has duplicates stripped out of it.
HDfiles = ['hd v2.csv','hd ec2.csv'] # New version of the HD catalogue; the extension charts don't have Durchmusterung cross reference I think.
HRfiles = ['hr cat.csv']
BDfiles = ['bd cat.csv'] # Bonner Durchmusterung.  Not used at present, need a fast way to integrate them.
# Sorting by glon,glat and cross reference only small chunks?
# Luminosity classes.
supergiant_lumins = ['I','Ie']
brightgiant_lumins = ['II','IIe']
giant_lumins = ['III','IIIe']

allgiant_lumins = ['I','Ie','II','IIe','III','IIIe']

subgiant_lumins = ['IV','IVe']
dwarf_lumins = ['V','Ve']
subdwarf_lumins = ['VI','VIe']

allstar_lumins = ['I','Ie','II','IIe','III','IIIe','IV','IVe','V','Ve','VI','VIe','e','',':','p']

# Constants.
parsec = 3.26 # Lightyears.

class catstar():

    def __init__(self,parallax,hip,long,lat,vmag,hd,spectrum,hr,name):
        self.parallax = float(parallax)
        self.hip = int(hip)
        self.long = float(long)
        self.lat = float(lat)
        self.vmag = float(vmag)
        self.hd = int(hd)
        self.hr = int(hr)
        self.name = name
        self.bd = ''
        self.cd = ''
        self.cpd = ''
        
        self.spectrum = spectrum
        try:
            self.colour = self.spectrum[0]
            self.subdiv = int(self.spectrum[1])
            self.lumin = self.spectrum[2:]
            self.lumin = self.lumin.strip('.')
            self.lumin = self.lumin.strip(':')
        except:
            self.colour = ''
            self.subdiv = ''
            self.lumin = ''
            #print('failed to divide spectrum',self.spectrum)

        self.parallax_as = self.parallax / 1000

        if self.parallax_as != 0:
            self.distance = int(1 / abs(self.parallax_as))
        else:
            self.distance = 0

        self.distance_ly = self.distance * parsec
        self.plane_distance = abs(self.distance * math.cos(math.radians(self.lat)))
        self.vertical_distance = abs(self.distance * math.sin(math.radians(self.lat)))

    def report(self):
        print('Star spectrum is',self.spectrum,'p.lax:',self.parallax,'G.long:',self.long,'G.lat:',self.lat,
              'vmag:',self.vmag,'dist:',self.distance,'pc','HIP:',self.hip,'HD:',self.hd,'HR:',self.hr,'Name',self.name)

def HIPsearch(starlist,cbox):

    # This needs to understand the longitude properly.
    longmin,longmax,latmin,latmax = cbox

    results = []

    for star in starlist:
        if star.long >= longmin and star.long <= longmax and star.lat >= latmin and star.lat <= latmax:
            # Limit output to showing only those stars which have an entry in the HIP catalogue.
            if star.hip != 0:
                results.append(star)

    results.sort(key = lambda hat: hat.hd)
    results.sort(key = lambda hat: hat.hip)
    results.sort(key = lambda hat: hat.hr, reverse = True)

    return results

def readHIPfile(filename):

    newstarlist = []

    with open(filename, 'r') as opened:
        readtext = opened.read()

    lines = readtext.split('\n')

    for line in lines:
        split = line.split(',')

        try:
            if split[0] != '':
                parallax = split[0]
            else:
                parallax = 0
            hip = split[3]
            long = split[1]
            lat = split[2]
            vmag = split[4]
            
            if split[5] != '':
                hd = split[5]
            else:
                hd = '0'
            
            spectrum = split[6]

            newstar = catstar(parallax, hip, long, lat, vmag, hd, spectrum, 0, '')
            try:
                if split[7] != '':
                    corrected = split[7].replace('B','BD')
                    newstar.bd = corrected
            except:
                print('unable to assign bd name')
            try:
                if split[8] != '':
                    corrected = split[8].replace('C','CD')
                    newstar.cd = corrected
            except:
                print('unable to assign cd name')
            try:
                if split[9] != '':
                    corrected = split[9].replace('P','CPD')
                    newstar.cpd = corrected
            except:
                print('unable to assign cpd name')

            newstarlist.append(newstar)

        except:
            if line != '':
                print('Failed to parse:',line)

    return newstarlist

def readHDfile(filename):

    newstarlist = []

    with open(filename, 'r') as opened:
        readtext = opened.read()

    lines = readtext.split('\n')

    for line in lines:
        split = line.split(',')

        try:
            long = split[0]
            lat = split[1]
            hd = split[2]
            try:
                vmag = float(split[3])
            except:
                vmag = 0
            spectrum = split[4]

            newstar = catstar(0, 0, long, lat, vmag, hd, spectrum, 0, '')
            try:
                if split[5] != '':
                    corrected = split[5]
                    if corrected[5] != ' ':
                        first = corrected[0:5]
                        second = corrected[5:].strip(' ')
                        corrected = first + ' ' + second
                    if 'BD' in corrected:
                        newstar.bd = corrected
                    elif 'CD' in corrected:
                        newstar.cd = corrected
                    elif 'CP' in corrected:
                        newstar.cpd = corrected
            except:
                alice = 'do nowt'

            newstarlist.append(newstar)


        except:
            if line != '':
                print('Failed to parse:',line)

    return newstarlist

def readHRfile(filename):

    newstarlist = []

    with open(filename, 'r') as opened:
        readtext = opened.read()

    lines = readtext.split('\n')

    for line in lines:

        split = line.split(',')

        try:
            hr = split[0]
            name = split[1] # Need to sort these out.
            hd = split[2]
            long = split[3]
            lat = split[4]
            vmag = split[5]
            spectrum = split[6]

            newstar = catstar(0, 0, long, lat, vmag, hd, spectrum, hr, name)

            newstarlist.append(newstar)

        except:
            if line != '':
                print('Failed to parse:',line)

    return newstarlist

def readBDfile(filename):

    newstarlist = []

    with open(filename, 'r') as opened:
        readtext = opened.read()

    lines = readtext.split('\n')

    for line in lines:

        split = line.split(',')

        try:
            long = split[0]
            lat = split[1]
            zone = split[2]
            degree = split[3]
            number = split[4]
            vmag = split[5]
            bdname = 'BD' + zone + degree + ' ' + number

            newstar = catstar(0, 0, long, lat, vmag, 0, '', 0, '')
            newstar.bd = bdname

            newstarlist.append(newstar)

        except:
            if line != '':
                print('Failed to parse:',line)

    return newstarlist

def writecsv(filename,starlist):

    print('Writing:',filename)
    with open(filename, 'w') as opened:
        opened.write('HIP,HD,HR,B/F name,BD,CD,CPD,spectrum,Colour,Subdiv,Lumin,vmag,Parallax,Distance(pc),Distance(ly),long,lat\n')
        for star in starlist:
            if star.hip != 0:
                opened.write(str(star.hip))
            else:
                opened.write('')
            opened.write(',')
            if star.hd != 0:
                opened.write(str(star.hd))
            else:
                opened.write('')
            opened.write(',')
            if star.hr != 0:
                opened.write(str(star.hr))
            else:
                opened.write('')
            opened.write(',')
            opened.write(str(star.name))
            opened.write(',')
            opened.write(str(star.bd))
            opened.write(',')
            opened.write(str(star.cd))
            opened.write(',')
            opened.write(str(star.cpd))
            opened.write(',')
            opened.write(str(star.spectrum))
            opened.write(',')
            opened.write(str(star.colour))
            opened.write(',')
            opened.write(str(star.subdiv))
            opened.write(',')
            opened.write(str(star.lumin))
            opened.write(',')
            opened.write(str(star.vmag))
            opened.write(',')
            opened.write(str(star.parallax))
            opened.write(',')
            opened.write(str(star.distance))
            opened.write(',')
            opened.write(str(int(star.distance_ly)))
            opened.write(',')
            opened.write(str(star.long))
            opened.write(',')
            opened.write(str(star.lat))
            opened.write('\n')

print('Mendax v' + version)
print('Catalogue star utility.')
print()

starlist = []

print('Loading HIP catalogue stars:')
print('----------------------------')
# Read in stars with HIP catalogue entries.
for HIPfile in HIPfiles:
    newstarlist = readHIPfile(HIPfile)
    for star in newstarlist:
        starlist.append(star)
    print('Found',len(newstarlist),'stars in',HIPfile)

# Make a list of those stars in the HIP catalogue which also have an entry in HD.
knownHD = []
for star in starlist:
    if star.hd != 0:
        knownHD.append(star.hd)
knownHD.sort(reverse = True)

print()
print('(Of these stars,',len(knownHD),'are also present in HD.)')
print()

print('Loading HD catalogue stars:')
print('---------------------------')
hdstarlist = []
# Read in stars with HD catalogue entries.
for HDfile in HDfiles:
    newstarlist = readHDfile(HDfile)
    print('Found',len(newstarlist),'stars in',HDfile)
    for star in newstarlist:
        hdstarlist.append(star)

# Strip out HD entries which are already covered.  Done this way for the sake of speed, otherwise it's treacle.
print()
print('Removing duplicate entries:')
print('---------------------------')
print('Started at',time.asctime())
for number in knownHD:
    try:
        hdstarlist.pop(number-1)
    except:
        alice = 'do nowt'
for star in hdstarlist:
    starlist.append(star)
print('Finished at',time.asctime())

print()
print('Loading HR catalogue stars:')
print('---------------------------')
hrstarlist = []
# Read in stars with HR catalogue entries; these are entirely covered by HD entries, but this gives us additional name data.
# For Bayer and Flamsteed designations.
for HRfile in HRfiles:
    newstarlist = readHRfile(HRfile)
    print('Found',len(newstarlist),'stars in',HRfile)
    for star in newstarlist:
        hrstarlist.append(star)
print()

# Done this way for the sake of speed.  Might be able to speed up the duplicate removal earlier in the same way.
hrstarlist.sort(key = lambda hat: hat.hd)
starlist.sort(key = lambda hat: hat.hd)
print('Integrating HR names into the main star list:')
print('---------------------------------------------')
starpos = 0
starlen = len(starlist)
for hrstar in hrstarlist:
    while starpos < starlen:
        if hrstar.hd == starlist[starpos].hd:
            starlist[starpos].hr = hrstar.hr
            starlist[starpos].name = hrstar.name
            break
        else:
            starpos += 1
print('Done integrating.')
print()

print('Found',len(starlist),'stars in total.')

starlist.sort(key = lambda star: star.distance)

##cbox = (0,360,-90,90) # Open coordinate box.
##mags = (-1,14) # Open magnitude box.
##distances = (100,100000) # Open distance box.
##supergiants = HIPsearch(starlist,supergiant_lumins,cbox,mags,distances)

# Heart nebula 134.8018, 0.9431 in modern coordinates.
# Soul nebula 137.6641, 1.1334
# This gives a direction for running a search.

# Jaques at 25.617?, -?

# Regor at 262.8

# Note on distances
# Because there's no distance calculation for the HD stars (and a lot of the HIP ones are... off) using trig. may be helpful
# to establish a cutoff boundary.
# For a 1300ly high (i.e. 2600ly total height, the plane sectors) box, an inner edge of 1000ly is at 50 degrees
# 2000ly, 33 degrees, 3000ly, 24 degrees, 4000ly, 18 degrees, 5000ly, 15 degrees, 6000ly, 13 degrees and so on.
# This will of course still include closer stars than the cutoff but may reduce clutter.

print()
cbox = (260.8,264.8,-90,0)
starsearch = HIPsearch(starlist,cbox)
a,b,c,d = str(cbox[0]),str(cbox[1]),str(cbox[2]),str(cbox[3])
print('Search parameters:')
print()
print('Galactic longitudes:',a,'to',b)
print('Galactic latitudes:',c,'to',d)
print()
found = len(starsearch)
print('There are',found,'stars in the direction of the search.')
print()
starsearch.sort(key = lambda hat: hat.long)
starsearch.sort(key = lambda hat: hat.hr)
filename = 'Cats ' + a + ',' + b + ',' + c + ',' + d + '.csv'
writecsv(filename,starsearch)

### Create series of narrow slices.
### Run this plot and you can see the density peaks for the spiral arm!
### (although why there's also one for 180 degrees I'm less sure - the Hyades and Pleiades clusters maybe?)
### ...plus we're close to the inner edge of the arm.  Cool.
##print()
##start_angle = 0
##slice_width = 5
##
##while start_angle < 360:
##    end_angle = start_angle + slice_width
##    cbox = (start_angle,end_angle,-50,50)
##    starslice = HIPsearch(starlist,cbox)
##    print(len(starslice),'total catalogue stars in',start_angle,'to',end_angle)
##    filename = 'slice' + str(start_angle) + '-' + str(end_angle) + '.csv'
####    writecsv(filename,starslice)
##    start_angle += slice_width
