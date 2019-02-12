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
import math as math

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

    #calculate distance matrix (halves should be equal size)
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


def shift(u, size):
    u0 = math.floor(size / 2) + 1
    k = u - u0
    return k


def getMeshgridMap(map):
    xSize, ySize, zSize = map.shape
    x = np.linspace(1, xSize, xSize)
    y = np.linspace(1, ySize, ySize)
    z = np.linspace(1, zSize, zSize)
    u, v, w  = np.meshgrid(x,y,z)
    return u, v, w


def spiralFilter(map):

    u, v, w  = getMeshgridMap(map)

    xSize, ySize, zSize = map.shape
    h = shift(u, xSize) + 1j * shift(v, ySize) - shift(w, zSize)
    H = h / abs(h)
    H[np.isnan(H)] = 0
    return H


def localRestoration(map, mask, maxRes, threshold):
    import math as mt
    """
    maxRes between 1 and map_size / 2(Nyquist)
    threshold signficance in the comparision with noise.Default 0.9
    """
    xSize, ySize, zSize = map.shape


    M = map * 0;
    W = map * 0;
    S = 3.0;

    # We create necessary stuff for the bank of filters once:
    u, v, w = getMeshgridMap(map)

    # Temporal variables
    x = shift(u, xSize)
    y = shift(v, ySize)
    z = shift(w, zSize)

    def cart2Sph(x, y, z):
        r = sqrt(x*x + y*y + z*z)
        theta = np.arccos(z/r)*180/np.pi  #to degrees
        phi = atan2(y,x)*180/ pi
        return [r,theta,phi]




    [Theta Phi Radial] = cart2sph(x, y, z)

    # Gaussian DC filter with sigma=0.01
    Hr = 1 - exp(-(u. ^ 2 + v. ^ 2 + w. ^ 2) / (2 * 0.05 ^ 2));

    # We obtain the Spiral Filter once:
    Hs = spiralFilter(map)
     # We do one FFT of the map
    C = fftn(map);

    parfor
    i = 1:1:maxRes

    # Actual filter
    H = exp(-((Radial - i). ^ 2) / (2 * S ^ 2)); % Annular
    filter
    with radius=R and sigma=S
    H = Hr. * H;

    CH = C. * ifftshift(H);

    ch = ifftn(CH);
    CH = CH. * ifftshift(Hs);
    s = abs(conj(ifftn(CH)));

    % normalized
    igram
    cn = cos(atan2(s, ch));
    % modulation
    m = abs(ch + 1
    i * s);
    % m = imgaussfilt3(m, i, 'FilterSize', 2 * floor(i / 2) + 1);

    q = quantile(m(~mask), threshold);
    m = double(m >= q);

    M = M + (cn. * m);
    W = W + (m);

    end

    end




