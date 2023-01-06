# -*- coding: utf-8 -*-
"""
biosppy.features.ceptral
-------------------
This module provides methods to extract cepstral features.
:copyright: (c) 2015-2018 by Instituto de Telecomunicacoes
:license: BSD 3-clause, see LICENSE for more details.
"""

# Imports
# 3rd party
import numpy as np
from scipy import fft

# local
from .. import utils
from . import time
from ..signals import tools as st


def freq_to_mel(hertz):
    """ 
    Converts mel-frequencies to heartz frequencies.
    
    Parameters
    ----------
    hertz : array
        hertz frequencies.
 
    Returns
    ----------
    mel frequencies : array
        mel frequencies.
    
    References
    ----------
    - Shashidhar G. Koolagudi, Deepika Rastogi, K. Sreenivasa Rao, Identification of Language using Mel-Frequency Cepstral Coefficients (MFCC), Procedia Engineering, Volume 38, 2012, Pages 3391-3398, ISSN 1877-7058
    
    """   

    return 1125 * np.log(1 + hertz / 700)


def mel_to_freq(mel):
    """ 
    Converts mel-frequencies to heartz frequencies.
    
    Parameters
    ----------
    mel : array
        mel frequencies.
 
    Returns
    ----------
    hertz frequencies : array
        hertz frequencies.

    References
    ----------
    - Shashidhar G. Koolagudi, Deepika Rastogi, K. Sreenivasa Rao, Identification of Language using Mel-Frequency Cepstral Coefficients (MFCC), Procedia Engineering, Volume 38, 2012, Pages 3391-3398, ISSN 1877-7058

    """
    return 700 * (np.exp(mel / 1125) - 1)


def mfcc(signal, window_size=100, sampling_rate=100, num_filters=10):
    """
    Computes the mel-frequency cepstral coefficients.
    
    Parameters
    ----------
    signal : array
        Input signal.
    sampling_rate: float
        Data sampling rate.
    window_size : int
       DFT window size. 
    num_filters : int
       Number of filters.

    Returns
    -------
    mfcc : list
        Signal mel-frequency cepstral coefficients.

    References
    ----------
    - https://github.com/brihijoshi/vanilla-stft-mfcc/blob/master/notebook.ipynb
    - https://www.kaggle.com/code/ilyamich/mfcc-implementation-and-tutorial
    - https://github.com/fraunhoferportugal/tsfel/blob/4e078301cfbf09f9364c758f72f5fe378f3229c8/tsfel/feature_extraction/features.py
    - https://www.youtube.com/watch?v=9GHCiiDLHQ4&list=PL-wATfeyAMNqIee7cH3q1bh4QJFAaeNv0&index=17
    - https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
   
   """
   # check inputs
    if signal is None:
        raise TypeError("Please specify an input signal.")

    freqs, power = st.power_spectrum(signal, sampling_rate=sampling_rate, decibel=False)
    
    # filter bank
    low_f = 0
    high_f = freqs[-1]

    ## convert to mels
    low_f_mel = freq_to_mel(low_f)
    high_f_mel = freq_to_mel(high_f)

    # lineary spaced array between the two MEL frequencies
    lin_mel = np.linspace(low_f_mel, high_f_mel, num=num_filters+2)
    
    # convert the array to the frequency space
    lin_hz = np.array([mel_to_freq(d) for d in lin_mel])
    
    # normalize the array to the FFT size and choose the associated FFT values
    filter_bins_hz = np.floor((window_size + 1) / sampling_rate * lin_hz).astype(int)

    # filterbank
    filter_banks = [] 
    # iterate bins
    for b in range(len(filter_bins_hz)-2):
        _f = [0]*(filter_bins_hz[b])
        _f += np.linspace(0, 1, filter_bins_hz[b + 1] - filter_bins_hz[b]).tolist()
        _f += np.linspace(1, 0, filter_bins_hz[b + 2] - filter_bins_hz[b + 1]).tolist()
        _f += [0]*(len(freqs)- filter_bins_hz[b + 2])

        filter_banks += [_f]
    filter_banks = np.array(filter_banks, dtype=object)

    enorm = 2.0 / (lin_hz[2:num_filters+2] - lin_hz[:num_filters])
    filter_banks *= enorm[:, np.newaxis]

    signal_power = np.abs(power)**2*(1/len(power))
    
    filter_banks = np.dot(filter_banks, signal_power.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    filter_banks = 20 * np.log10(filter_banks)  # dB

    mel_coeff = fft.dct(filter_banks)[1:]  # Keep 2-13

    mel_coeff -= (np.mean(mel_coeff, axis=0) + 1e-8)  # norm
    # sinusoidal liftering1 to the MFCCs to de-emphasize higher MFCCs
    n = np.arange(len(mel_coeff))
    cep_lifter = 22
    lift = 1 + (cep_lifter / 2) * np.sin(np.pi * n / cep_lifter)
    mel_coeff *= lift  

    args = [mel_coeff]
    names = ["mfcc"]
    
    args = np.nan_to_num(args)
    return utils.ReturnTuple(tuple(args), tuple(names))
    

def cepstral_features(signal=None, sampling_rate=100):
    """
    Compute quefrency metrics describing the signal.
   
    Parameters
    ----------
    signal : array
        Input signal.
    sampling_rate: float
        Data sampling rate.

    Returns
    -------
    mfcc_{time_features} : list
        Time features computer over the signal mel-frequency cepstral coefficients.

    References
    ----------
    - https://github.com/brihijoshi/vanilla-stft-mfcc/blob/master/notebook.ipynb
    - https://www.kaggle.com/code/ilyamich/mfcc-implementation-and-tutorial
    - https://github.com/fraunhoferportugal/tsfel/blob/4e078301cfbf09f9364c758f72f5fe378f3229c8/tsfel/feature_extraction/features.py
    - https://www.youtube.com/watch?v=9GHCiiDLHQ4&list=PL-wATfeyAMNqIee7cH3q1bh4QJFAaeNv0&index=17
    - https://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
    
    """
  
    # check input
    assert len(signal) > 0, 'Signal size < 1'

    # ensure numpy
    signal = np.array(signal)
    args, names = [], []
    
    mel_coeff = mfcc(signal, sampling_rate)["mfcc"]
    
    # temporal
    _fts = time.time_features(mel_coeff, sampling_rate)
    fts_name = [str("mfcc_" + i) for i in _fts.keys()]
    fts = list(_fts[:])

    args += fts
    names += fts_name

    args = np.nan_to_num(args)
    return utils.ReturnTuple(tuple(args), tuple(names))
