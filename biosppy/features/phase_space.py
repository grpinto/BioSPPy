# -*- coding: utf-8 -*-
"""
biosppy.features.phase_space
-------------------
This module provides methods to extract phase space features.
:copyright: (c) 2015-2018 by Instituto de Telecomunicacoes
:license: BSD 3-clause, see LICENSE for more details.
"""

# Imports
# 3rd party
import numpy as np
from scipy.signal import resample
from scipy.spatial.distance import pdist,squareform
import matplotlib.pylab as plt

# local
from .. import utils


def rec_plot(signal):
    """
    Compute recurrence plot (distance matrix).

    Parameters
    ----------
    signal : array
        Input signal.
    
    Returns
    -------
    rec_plot : ndarray 
        recplot matrix.

    """
    args, names = [], []
    sig_down = resample(signal, 224)
    d = pdist(sig_down[:,None])
    rec = squareform(d)

    args += [rec]
    names += ['rec_plot']
    
    args = np.nan_to_num(args)
    return utils.ReturnTuple(tuple(args), tuple(names))


def phase_space_features(signal=None):
    """
    Compute statistical metrics describing the signal.

    Parameters
    ----------
    signal : array
        Input signal.

    Returns
    -------
    rec_plot_rec_rate : float
        The percentage of recurrence points
    rec_plot_determ : float
        The percentage of recurrence points which form diagonal lines
    rec_plot_avg_diag_line_len : float
        average length of the diagonal lines
    rec_plot_lgst_diag_line_len : float
        length of the longest diagonal line
    rec_plot_entropy_diag_line : float
        Entropy of the probability distribution of the diagonal line lengths
    rec_plot_laminarity : float
        Percentage of recurrence points which form vertical lines
    rec_plot_trapping_tm : float
        average length of the vert lines
    rec_plot_lgst_vert_line_len : float
        length of the longest vert line
    rec_plot_entropy_vert_line : float
        Entropy of the probability distribution of the vert line lengths
    rec_plot_avg_white_vert_line_len : float
        average length of the white vert lines
    rec_plot_lgst_white_vert_line_len : float
        length of the longest white vert line
    rec_plot_entropy_white_vert_line : float
        Entropy of the probability distribution of the white vert line lengths
    rec_plot_det_rr_ratio : float
        ratio between determinism / recurrence rate
    rec_plt_lami_determ_ratio : float
        ratio between laminarity / determinism 

    References
    ----------
    - Ghaderyan, Peyvand, and Ataollah Abbasi. "An efficient automatic workload estimation method based on electrodermal activity using pattern classifier combinations." International Journal of Psychophysiology 110 (2016): 91-101.
    - recurrence plot: https://github.com/bmfreis/recurrence_python

    """

    # check input
    assert len(signal) > 0, 'Signal size < 1'
    
    # ensure numpy
    signal = np.array(signal)
    args, names = [], []

    rp = rec_plot(signal)["rec_plot"]
    threshold = 0.5
    len_rp = len(rp)
    for l in range(len_rp):
        for c in range(len_rp):
            rp[l, c] = 1 if rp[l, c] < threshold else 0
    len_rp = len(rp)
    diag_freq = np.zeros(len_rp+1)

    # upper diagnotal
    for k in range(1, len_rp-1, 1):
        d = np.diag(rp, k=k)
        d_l = 0
        for _, i in enumerate(d):
            if i:  # has a dot
                d_l += 1
                # if its end of line, finishes counting and adds to hist
                if _ == (len(d)-1):
                    diag_freq[d_l] += 1
            else:  # doesn't have a dot
                if d_l != 0:
                    diag_freq[d_l] += 1
                # if its not end of the line and d_l != 0, line ended
                d_l = 0
                diag_freq[d_l] += 1

    # lower diagonal
    for k in range(-1, -(len_rp-1), -1):
        d = np.diag(rp, k=k)
        d_l = 0
        for _, i in enumerate(d):
            if i:  # has a dot
                d_l += 1
                # if its end of line, finishes counting and adds to hist
                if _ == (len(d)-1):
                    diag_freq[d_l] += 1
            else:  # doesn't have a dot
                if d_l != 0:
                    diag_freq[d_l] += 1
                # if its not end of the line and d_l != 0, line ended
                d_l = 0
                diag_freq[d_l] += 1
        
    # vertical lines
    vert_freq = np.zeros(len_rp+1)
    for k in range(len_rp):
        d = rp[:, k]
        d_l = 0
        for _, i in enumerate(d):
            if i:  # has a dot
                d_l += 1
                # if its end of line, finishes counting and adds to hist
                if _ == (len(d)-1):
                    vert_freq[d_l] += 1
            else:  # doesn't have a dot
                if d_l != 0:
                    vert_freq[d_l] += 1
                # if its not end of the line and d_l != 0, line ended
                d_l = 0
                vert_freq[d_l] += 1

    # white vertical lines
    white_vert_freq = np.zeros(len_rp+1)
    for k in range(len_rp):
        d = rp[:, k]
        d_l = 0
        for _, i in enumerate(d):
            if i == 0:  # has a dot
                d_l += 1
                # if its end of line, finishes counting and adds to hist
                if _ == (len(d)-1):
                    white_vert_freq[d_l] += 1
            else:  # doesn't have a dot
                if d_l != 0:
                    white_vert_freq[d_l] += 1
                # if its not end of the line and d_l != 0, line ended
                d_l = 0
                white_vert_freq[d_l] += 1
    
    # recurrence rate
    try:
        rec_rate = 0
        for l in range(len_rp):
            rec_rate += np.sum(rp[l])
        rec_rate/=(len_rp**2)
    except Exception as e:
        print(e) 
        rec_rate = None
    args += [rec_rate]
    names += ['rec_plot_rec_rate']
    MIN = 2
    
    # determ 
    try:
        determ = np.sum([i*diag_freq[i] for i in range(MIN, len(diag_freq), 1)])/np.sum([i*diag_freq[i] for i in range(1, len(diag_freq), 1)])
    except Exception as e:
        print(e) 
        determ = None
    args += [determ]
    names += ['rec_plot_determ']
    
    # laminarity 
    try:
        laminarity = np.sum([i*vert_freq[i] for i in range(MIN, len(vert_freq), 1)])/np.sum([i*vert_freq[i] for i in range(len(vert_freq))])
    except Exception as e:
        print(e) 
        laminarity = None
    args += [laminarity]
    names += ['rec_plot_laminarity']
    
    # det_rr_ratio 
    try:
        det_rr_ratio = len_rp**2*(np.sum([i*diag_freq[i] for i in range(MIN, len(diag_freq), 1)])/(np.sum([i*diag_freq[i] for i in range(1, len(diag_freq), 1)]))**2)
    except Exception as e:
        print(e) 
        det_rr_ratio = None
    args += [det_rr_ratio]
    names += ['rec_plot_det_rr_ratio']
    
    # det_rr_ratio 
    try:
        rec_plt_lami_determ_ratio = laminarity/determ
    except Exception as e:
        print(e) 
        rec_plt_lami_determ_ratio = None
    args += [rec_plt_lami_determ_ratio]
    names += ['rec_plot_lami_determ_ratio']
    
    # avg_diag_line_len 
    try:
        avg_diag_line_len = np.sum([i*diag_freq[i] for i in range(MIN, len(diag_freq), 1)])/np.sum(diag_freq)
    except Exception as e:
        print(e) 
        avg_diag_line_len = None
    args += [avg_diag_line_len]
    names += ['rec_plot_avg_diag_line_len']
    
    # avg_vert_line_len 
    try:
        avg_vert_line_len = np.sum([i*vert_freq[i] for i in range(MIN, len(vert_freq), 1)])/np.sum(vert_freq)
    except Exception as e:
        print(e) 
        avg_vert_line_len = None
    args += [avg_vert_line_len]
    names += ['rec_plot_avg_vert_line_len']
    
    # avg_white_vert_line_len 
    try:
        avg_white_vert_line_len = np.sum([i*white_vert_freq[i] for i in range(MIN, len(white_vert_freq), 1)])/np.sum(white_vert_freq)
    except Exception as e:
        print(e) 
        avg_white_vert_line_len = None
    args += [avg_white_vert_line_len]
    names += ['rec_plot_avg_white_vert_line_len']
    
    # rec_plot_trapping_tm 
    try:
        rec_plot_trapping_tm = np.sum([i*vert_freq[i] for i in range(MIN, len(vert_freq), 1)])/np.sum(vert_freq)
    except Exception as e:
        print(e) 
        rec_plot_trapping_tm = None
    args += [rec_plot_trapping_tm]
    names += ['rec_plot_trapping_tm']
    
    # rec_plot_lgst_diag_line_len 
    try:
        i_ll = np.sign(diag_freq)
        rec_plot_lgst_diag_line_len = np.where(i_ll == 1)[0][-1]
    except Exception as e:
        print(e) 
        rec_plot_lgst_diag_line_len = 0
    args += [rec_plot_lgst_diag_line_len]
    names += ['rec_plot_lgst_diag_line_len']

    # rec_plot_lgst_vert_line_len 
    try:
        i_ll = np.sign(vert_freq)
        rec_plot_lgst_vert_line_len = np.where(i_ll == 1)[0][-1]
    except Exception as e:
        print(e) 
        rec_plot_lgst_vert_line_len = 0
    args += [rec_plot_lgst_vert_line_len]
    names += ['rec_plot_lgst_vert_line_len']

    # rec_plot_lgst_vert_line_len 
    try:
        i_ll = np.sign(white_vert_freq)
        rec_plot_lgst_white_vert_line_len = np.where(i_ll == 1)[0][-1]
    except Exception as e:
        print(e) 
        rec_plot_lgst_white_vert_line_len = 0
    args += [rec_plot_lgst_white_vert_line_len]
    names += ['rec_plot_lgst_white_vert_line_len']

    # rec_plot_entropy_diag_line 
    try:
        rec_plot_entropy_diag_line = - np.sum([diag_freq[i]*np.log(diag_freq[i]) for i in range(MIN, len(diag_freq), 1)])
    except Exception as e:
        print(e) 
        rec_plot_entropy_diag_line = 0
    args += [rec_plot_entropy_diag_line]
    names += ['rec_plot_entropy_diag_line']

    # rec_plot_entropy_vert_line 
    try:
        rec_plot_entropy_vert_line = - np.sum([vert_freq[i]*np.log(vert_freq[i]) for i in range(MIN, len(vert_freq), 1)])
    except Exception as e:
        print(e) 
        rec_plot_entropy_vert_line = 0
    args += [rec_plot_entropy_vert_line]
    names += ['rec_plot_entropy_vert_line']

    # rec_plot_entropy_white_vert_line 
    try:
        rec_plot_entropy_white_vert_line = - np.sum([white_vert_freq[i]*np.log(white_vert_freq[i]) for i in range(MIN, len(white_vert_freq), 1)])
    except Exception as e:
        print(e) 
        rec_plot_entropy_white_vert_line = 0
    args += [rec_plot_entropy_white_vert_line]
    names += ['rec_plot_entropy_white_vert_line']
    
    args = np.nan_to_num(args)
    return utils.ReturnTuple(tuple(args), tuple(names))
