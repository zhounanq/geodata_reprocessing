# -*- coding: utf-8 -*-

"""
Harmonic ANalysis of Time Series
Repository: https://github.com/gespinoza/hants

This python implementation was based on two previous implementations
available at the following links:
https://codereview.stackexchange.com/questions/71489/harmonic-analysis-of-time-series-applied-to-arrays
http://nl.mathworks.com/matlabcentral/fileexchange/38841-matlab-implementation-of-harmonic-analysis-of-time-series--hants-
"""
from __future__ import division
from copy import deepcopy
import numpy as np
import math
import matplotlib.pyplot as plt
import warnings


def hants_image(img_array3d,):
    pass


def hants(ni, nb, nf, y, ts, HiLo, low, high, fet, dod, delta):
    """
    This function applies the Harmonic ANalysis of Time Series (HANTS)
    algorithm originally developed by the Netherlands Aerospace Centre (NLR)
    (http://www.nlr.org/space/earth-observation/).

    Inputs:
    ni    = nr. of images (total number of actual samples of the time series)
    nb    = length of the base period, measured in virtual samples
            (days, dekads, months, etc.)
    nf    = number of frequencies to be considered above the zero frequency
    y     = array of input sample values (e.g. NDVI values)
    ts    = array of size ni of time sample indicators
            (indicates virtual sample number relative to the base period);
            numbers in array ts maybe greater than nb
            If no aux file is used (no time samples), we assume ts(i)= i,
            where i=1, ..., ni
    HiLo  = 2-character string indicating rejection of high or low outliers
            select from 'Hi', 'Lo' or 'None'
    low   = valid range minimum
    high  = valid range maximum (values outside the valid range are rejected
            right away)
    fet   = fit error tolerance (points deviating more than fet from curve
            fit are rejected)
    dod   = degree of overdeterminedness (iteration stops if number of
            points reaches the minimum required for curve fitting, plus
            dod). This is a safety measure
    delta = small positive number (e.g. 0.1) to suppress high amplitudes

    Outputs:
    amp   = returned array of amplitudes, first element is the average of
            the curve
    phi   = returned array of phases, first element is zero
    yr	= array holding reconstructed time series
    """
    # Arrays
    mat = np.zeros((min(2*nf+1, ni), ni))
    amp = np.zeros((nf + 1))
    phi = np.zeros((nf + 1))
    yr = np.zeros((ni, 1))

    # Filter. check which setting to set for outlier filtering
    sHiLo = 0
    if HiLo == 'Hi':
        sHiLo = -1
    elif HiLo == 'Lo':
        sHiLo = 1

    nr = min(2*nf+1, ni)
    noutmax = ni - nr - dod
    dg = 180.0 / math.pi
    mat[0, :] = 1.0

    ang = 2 * math.pi * np.arange(nb) / nb
    cs = np.cos(ang)
    sn = np.sin(ang)

    i = np.arange(1, nf+1)
    for j in np.arange(ni):
        index = np.mod(i*ts[j], nb)
        mat[2 * i-1, j] = cs.take(index)
        mat[2 * i, j] = sn.take(index)
    #for

    p = np.ones_like(y)
    bool_out = ((y < low) | (y > high))
    p[bool_out] = 0
    nout = np.sum(p == 0)

    if nout > noutmax:
        raise Exception('Not enough data points.')
    #if

    # prepare for while loop
    ready = np.zeros((y.shape[0]), dtype=bool) # all timeseries set to false
    nloop = 0
    nloopmax = ni

    while ((not ready.all()) & (nloop < nloopmax)):
        nloop += 1
        # multiply outliers with time series
        za = np.matmul(mat, p * y)

        # multiply mat with the multiplication of multiply diagonal of p with transpose of mat
        A = np.matmul(np.matmul(mat, np.diag(p)), np.transpose(mat))
        # add delta to suppress high amplitudes but not for [0,0]
        A = A + np.identity(nr)*delta
        A[0, 0] = A[0, 0] - delta
        # solve linear matrix equation and define reconstructed time series
        zr = np.linalg.solve(A, za)
        yr = np.matmul(np.transpose(mat), zr)

        # calculate error and sort err by index
        diffVec = sHiLo  * (yr - y)
        err = p * diffVec
        rankVec = np.argsort(err)

        # select maximum error and compute new ready status
        maxerr = diffVec[rankVec[-1]]
        ready = (maxerr <= fet) | (nout == noutmax)

        # if ready is still false
        if (not ready):
            i = ni - 1 # i is number of input images
            j = rankVec[i]
            while ((p[j]*diffVec[j] > 0.5*maxerr) & (nout < noutmax)):
                p[j] = 0
                nout += 1
                i -= 1
                if i == 0:
                    j = 0
                else:
                    j = 1
            #while
        #if
    #while

    ## compute the amplitudes and phases for reconstruction
    amp[0] = zr[0]
    phi[0] = 0.0

    # zr[ni] = 0.0 #zr = np.append(zr, np.zeros(ni-zr.size))

    i = np.arange(1, nr-1, 2)
    ifr = (i + 1) // 2
    ra = np.array(zr[i])
    rb = np.array(zr[i+1])

    amp[ifr] = np.sqrt(ra * ra + rb * rb)
    phase = np.arctan2(rb, ra) * dg
    phase[phase < 0] = phase[phase < 0] + 360
    phi[ifr] = phase

    return [yr, amp, phi]


def hants_reconstruct(amp, phi, nbase):
    """Compute reconstructed series.

    amp: array of amplitudes, first element is the average of the curve
    phi: (\\varphi<tab>) array of phases, first element is zero
    nbase: length of the base period, measured in virtual samples (days, decades, months, etc.)

    Outputs:
    yr: reconstructed array of sample values
    """
    nf = amp.size
    yr = np.zeros(nbase)

    a_coef = amp * np.cos(phi*math.pi/180)
    b_coef = amp * np.sin(phi*math.pi/180)
    for i in range(nf):
        tt = np.arange(0,nbase) * i * 2 * math.pi / nbase
        yr += a_coef[i] * np.cos(tt) + b_coef[i] * np.sin(tt)

    return yr


def main():
    print("### hants.main() ###########################################")

    # Run HANTS for a single point

    # sample 1
    # nb = 36
    # nf = 3
    # low = 0.0
    # high = 255
    # fet = 5.0
    # dod = 1
    # delta = 0.1
    #
    # src_array = [5.0, 2.0, 5.0, 10.0, 12.0, 18.0, 20.0, 23.0, 27.0,
    #              30.0, 40.0, 60.0, 66.0, 70.0, 90.0, 120.0, 160.0, 190.0,
    #              105.0, 210.0, 104.0, 200.0, 90.0, 170.0, 50.0, 120.0, 80.0,
    #              60.0, 50.0, 40.0, 30.0, 28.0, 24.0, 20.0, 15.0, 10.0]
    #
    # ts = np.arange(0, 36)
    # ni = len(src_array)

    # sample 2
    nb = 365
    nf = 3
    low = -1
    high = 1
    fet = 0.05
    delta = 0.1
    dod = 1

    src_array = [0.055952, 0.037081, 0.062657, 0.120110, 0.178219, 0.244443, 0.213190, 0.494648,
                 0.328767, 0.561776, 0.380300, 0.641233, 0.532486, 0.827757, 0.654052, 0.816695,
                 0.611424, 0.661557, 0.398067, 0.339881, 0.113957, 0.086790, 0.058600]

    ts = np.arange(1, 365, 16)
    ni = len(src_array)

    # HANTS
    y = np.array(src_array)
    [hants_values, amp, phi] = hants(ni, nb, nf, y, ts, 'None', low, high, fet, dod, delta)
    [hants_values_Hi, amp_Hi, phi_Hi] = hants(ni, nb, nf, y, ts, 'Hi', low, high, fet, dod, delta)
    [hants_values_Lo, amp_Lo, phi_Lo] = hants(ni, nb, nf, y, ts, 'Lo', low, high, fet, dod, delta)

    # Reconstruction
    y_reconstruction = hants_reconstruct(amp, phi, nb)

    # Plot
    top = 1.15*max(np.nanmax(src_array), np.nanmax(hants_values))
    bottom = 1.15*min(np.nanmin(src_array), np.nanmin(hants_values))
    ylim = [bottom, top]

    plt.plot(ts, hants_values_Lo, 'bo-', label='HANTS - Lo')
    plt.plot(ts, hants_values_Hi, 'go-', label='HANTS - Hi')
    plt.plot(ts, hants_values, 'r*-', label='HANTS - None')
    plt.plot(ts, src_array, 'k.--', label='Original data')
    plt.plot(np.arange(nb), y_reconstruction, 'y:', label='Re data')

    plt.ylim(ylim[0], ylim[1])
    plt.legend(loc=4)
    plt.xlabel('time')
    plt.ylabel('values')
    # plt.gcf().autofmt_xdate()
    # plt.axes().set_aspect(0.5*(ts[-1] - ts[0])/(ylim[1] - ylim[0]))

    plt.show()


####################################################################
if __name__ == "__main__":
    main()
