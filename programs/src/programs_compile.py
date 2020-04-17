# **************************************************************************
# *
# * Authors:     Josue Gomez Blanco (josue.gomez-blanco@mcgill.ca)
# *              Javier Vargas Balbuena (javier.vargasbalbuena@mcgill.ca)
# *
# * Department of Anatomy and Cell Biology, McGill University
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import os
import glob

def getFlags():
    xmippHome = os.environ.get('XMIPP_CRYOMETHODS_HOME')
    xmippLib = os.path.join(xmippHome, 'lib')
    scipionHome = os.environ.get('SCIPION_HOME')
    scipionInclude = os.path.join(scipionHome, 'software', 'include')
    cryoMethHome = os.environ.get('CRYOMETHODS_HOME')
    cryoMethCore = os.path.join(cryoMethHome, 'programs', 'xmippCore')

    flags = ' -O -D_LINUX -L' + xmippLib + ' -I' + cryoMethCore
    flags += ' -lXmipp -lXmippCore -I' + scipionInclude + ' -std=c++11'
    return flags

def run():
    cryoMethHome = os.environ.get('CRYOMETHODS_HOME')
    srcPrograms = os.path.join(cryoMethHome, 'programs', 'src')
    binPrograms = os.path.join(cryoMethHome, 'programs', 'bin')
    progList = glob.glob(srcPrograms + '/*.cpp')
    for prog in progList:
        baseProg = os.path.basename(prog).split('.')[0]
        binProg = os.path.join(binPrograms, baseProg)
        command = "g++ -o " + binProg + " " + prog + getFlags()
        print(command)
        os.system(command)


if __name__ == '__main__':
    # compile
    run()