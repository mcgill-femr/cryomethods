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


def transfFourierMap(map):
    return np.fft.fftshift(np.fft.fftn(map))


def transfFromFourier(map):
    return np.fft.ifftn(np.fft.ifftshift(map))


def getMatrixDistance(size):
    ctr = (size+1)/2
    mat = np.ogrid[1-ctr:size-ctr+1, 1-ctr:size-ctr+1, 1-ctr:size-ctr+1]
    dist = np.sqrt(mat[1]**2 + mat[1]**2 + mat[1]**2)
    return dist


def getAbsShell(shell):
    absShell = abs(shell)
    return np.nonzero(absShell)

def getQuantileShell(shell, q=0.55):
    return np.quantile(shell, q)

def getCorrectedShell(shell, qShell, weight):
    absShell = abs(shell)
    np.seterr(divide='ignore', invalid='ignore')
    normalization = np.true_divide(shell,absShell)
    correctedValues = qShell * weight + absShell * (1 - weight)
    corrShell = normalization * correctedValues
    corrShell[np.isnan(corrShell)] = 0
    return corrShell


def correctAnisotropy(mapNp, weight, q, minFreq, maxFreq):
    # minFreq and maxFreq are in pixels

    # mapNorm = (mapNp - np.mean(mapNp))
    # mapNorm = np.division(mapNorm, np.std(mapNorm))

    mapFt = transfFourierMap(mapNp)

    #calculate distance matrix
    size = mapNp.shape[0]
    dist = getMatrixDistance(size)

    mask = (dist <= size)*1

    # make sure it gets at least 1 voxel
    eps = 1e-4
    initDist = 0.5 + eps
    finalMapFt = np.zeros(mapFt.shape)
    for i in range(1, size+1):
        rInt = (dist < initDist)*1
        rOut = (dist < initDist+i)*1
        ring = np.subtract(rOut, rInt)
        if i >= minFreq and i <= maxFreq:
            shell = mapFt * ring
            absShell = getAbsShell(shell)
            qShell = getQuantileShell(absShell, q)
            corrShell = getCorrectedShell(shell, qShell, weight)
        else:
            corrShell = mapFt * ring

        finalMapFt = finalMapFt + corrShell

    finalMap = transfFromFourier(finalMapFt).real

    return finalMap, finalMapFt


# def correctAnisotropyHalves(mapNp1, mapNp2, weight, q, minFreq, maxFreq):
#
#     mapFt1 = getFourierTransform(mapNp1)
#     mapFt2 = getFourierTransform(mapNp2)
#
#     #calculate distance matrix (halves should be equal size)
#     size = mapNp1.shape[0]
#     dist = getMatrixDistance(size)
#
#     # make sure it gets at least 1 voxel
#     eps = 1e-4
#     initDist = 0.5 + eps
#
#     rInt = dist < initDist
#     for i in range(1, maxFreq+1):
#         rOut = dist < initDist + i
#         if i > minFreq:
#             ring = rOut - rInt
#             shell1 = mapFt1*ring
#             shell2 = mapFt1 * ring
#
#             meanShell1 = getMeanShell(shell1, q)
#             meanShell2 = getMeanShell(shell2, q)
#             meanShell = 0.5*meanShell1 + 0.5*meanShell2
#
#             corrShell1 = getCorrectedShell(shell1, meanShell, weight)
#             corrShell2 = getCorrectedShell(shell2, meanShell, weight)
#
#             mapFt1 = (mapFt1 * (~ring)) + corrShell1
#             mapFt2 = (mapFt2 * (~ring)) + corrShell2
#
#         rInt = rOut
#
#     finalMap1 = getFinalMap(mapFt1)
#     finalMap2 = getFinalMap(mapFt2)
#
#     return finalMap1, finalMap2
