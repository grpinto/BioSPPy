import numpy as np
from .. import utils
from . import time
import pywt


def get_DWT(signal, wavelet="db4", level=5):
    """Compute the signal discrete wavelet transform coefficients.
        Parameters
        ----------
        signal : array
            Input signal.
        wavelet: string
            Type of wavelet
        level: int
            Decomposition level

        Returns
        -------
        cA : list
            Approximation coefficient
        cD : list
            Detail coefficient

        References
        ----------
        https://pywavelets.readthedocs.io/en/latest/ref/dwt-discrete-wavelet-transform.html
    Ghaderyan, Peyvand, and Ataollah Abbasi. "An efficient automatic workload estimation method based on electrodermal activity using pattern classifier combinations." International Journal of Psychophysiology 110 (2016): 91-101

    """
    args, names = [], []
    cD = pywt.downcoef("d", signal, wavelet, level)
    cA = pywt.downcoef("a", signal, wavelet, level)

    args += [cA, cD]
    names += ["cA", "cD"]
    return utils.ReturnTuple(tuple(args), tuple(names))


def time_freq_features(signal, sampling_rate):
    """Compute statistical metrics describing the signal.
        Parameters
        ----------
        signal : array
            Input signal.
        
        sampling_rate: float
            Sampling rate.

        Returns
        -------
        DWT_cA_{temporal features} : list
            Temporal features over the signal discrete wavelet transform approximation coefficients.
        
        DWT_cA_{statistical features} : list
            Statistical features over the signal discrete wavelet transform approximation coefficients.

        DWT_cD_{temporal features} : list
            Temporal features over the signal discrete wavelet transform detail coefficients.
        
        DWT_cD_{statistical features} : list
            Statistical features over the signal discrete wavelet transform detail coefficients.

        DWT_cA_entropy : float
            Entropy of the signal discrete wavelet transform approximation coefficients.

        DWT_cD_entropy : float
            Entripy of the signal discrete wavelet transform detail coefficients.

        References
        ----------
    Ghaderyan, Peyvand, and Ataollah Abbasi. "An efficient automatic workload estimation method based on electrodermal activity using pattern classifier combinations." International Journal of Psychophysiology 110 (2016): 91-101.
    recurrence plot: https://github.com/bmfreis/recurrence_python
        """
    # check input
    assert len(signal) > 0, 'Signal size < 1'
    # ensure numpy
    signal = np.array(signal)
    args, names = [], []

    ## wavelets
    cA, cD = get_DWT(signal)

    # temporal
    _fts = time.time_features(cA, sampling_rate=sampling_rate)
    fts_name = [str("DWT_cA_" + i) for i in _fts.keys()]
    fts = list(_fts[:])

    args += fts
    names += fts_name

    # temporal
    _fts = time.time_features(cD, sampling_rate=sampling_rate)
    fts_name = [str("DWT_cD_" + i) for i in _fts.keys()]
    fts = list(_fts[:])

    args += fts
    names += fts_name

    return utils.ReturnTuple(tuple(args), tuple(names))
