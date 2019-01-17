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
# *  e-mail address 'javier.vargasbalbuena@mcgill.ca'
# *
# **************************************************************************
import numpy as np

def getFourierTransform(map):
    return np.fft.fftshift(np.fft.fftn(map))


def getMatrixDistance(size):
    ctr = (size+1)/2
    mat = np.ogrid[1-ctr:size-ctr+1, 1-ctr:size-ctr+1, 1-ctr:size-ctr+1]
    dist = np.sqrt(mat[1]**2 + mat[1]**2 + mat[1]**2)
    return dist


def getAbsShell(shell):
    return abs(shell)


def getMeanShell(shell, q=0.55):
    absShell = getAbsShell()
    nZeroShell = absShell[np.nonzero(absShell)]
    return np.quantile(nZeroShell, q)


def getCorrectedShell(shell, meanShell, weight):
    absShell = getAbsShell(shell)
    normalization = shell / absShell
    correctedValues = meanShell * weight + absShell * (1 - weight)
    corrShell = normalization * correctedValues
    corrShell[np.isnan(corrShell)] = 0
    return corrShell


def getFinalMap(map):
    return np.fft.ifftn(np.fft.ifftshift(map))


def correctAnisotropy(mapNp, weight, q, minFreq, maxFreq):

    # mapNorm = (mapNp - np.mean(mapNp))
    # mapNorm = np.division(mapNorm, np.std(mapNorm))

    mapFt = getFourierTransform(mapNp)

    #calculate distance matrix
    size = mapNp.shape[0]
    dist = getMatrixDistance(size)

    # make sure it gets at least 1 voxel
    eps = 1e-4
    initDist = 0.5 + eps

    rInt = dist < initDist
    for i in range(1, maxFreq+1):
        rOut = dist < initDist + i
        if i > minFreq:
            ring = rOut - rInt
            shell = mapFt*ring
            meanShell = getMeanShell(shell, q)
            corrShell = getCorrectedShell(shell, meanShell, weight)
            mapFt = (mapFt * (~ring)) + corrShell
        rInt = rOut

    finalMap = getFinalMap(mapFt)

    return finalMap


def correctAnisotropyHalves(mapNp1, mapNp2, weight, q, minFreq, maxFreq):

    mapFt1 = getFourierTransform(mapNp1)
    mapFt2 = getFourierTransform(mapNp2)

    #calculate distance matrix (halves must be equal size)
    size = mapNp1.shape[0]
    dist = getMatrixDistance(size)

    # make sure it gets at least 1 voxel
    eps = 1e-4
    initDist = 0.5 + eps

    rInt = dist < initDist
    for i in range(1, maxFreq+1):
        rOut = dist < initDist + i
        if i > minFreq:
            ring = rOut - rInt
            shell1 = mapFt1*ring
            shell2 = mapFt1 * ring

            meanShell1 = getMeanShell(shell1, q)
            meanShell2 = getMeanShell(shell2, q)
            meanShell = 0.5*meanShell1 + 0.5*meanShell2

            corrShell1 = getCorrectedShell(shell1, meanShell, weight)
            corrShell2 = getCorrectedShell(shell2, meanShell, weight)

            mapFt1 = (mapFt1 * (~ring)) + corrShell1
            mapFt2 = (mapFt2 * (~ring)) + corrShell2

        rInt = rOut

    finalMap1 = getFinalMap(mapFt1)
    finalMap2 = getFinalMap(mapFt2)

    return finalMap1, finalMap2
