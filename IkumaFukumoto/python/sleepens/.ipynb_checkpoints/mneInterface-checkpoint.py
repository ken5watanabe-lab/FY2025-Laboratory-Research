"""smrMAT I/O Interface"""

# Authors: Jeffrey Wang
# License: BSD 3 clause

import numpy as np
import mne
from sleepens.io import DataObject
from typing import Dict
from copy import deepcopy   
name = "mneRaw"
standard = ".fif files exported by MNE"
filetypes = [("FIF-files", "*.fif")]
type = "RAW"
tags = {'r'}



def read_data(filepath, channel):
    """
    Load MNE Raw file (.fif) and extract label data from a specific channel.

    Parameters
    ----------
    filepath : str
        Path to the .fif file (e.g., "subject_raw.fif").
    channel : str
        Channel name to extract (e.g., 'Stimulus' or 'Label').

    Returns
    -------
    dataobject : DataObject
        DataObject containing the label data and sampling resolution.
    """

    # Load MNE Raw file
    try:
        raw = _load(filepath)
    except Exception as e:
        raise FileNotFoundError(f"Could not read file '{filepath}': {e}")

    return _read_ch_from_raw(raw, channel)

def _read_ch_from_raw(raw, channel):
    """
    Helper function to extract data from a specific channel in an MNE Raw object.

    Parameters
    ----------
    raw : mne.io.Raw
        The MNE Raw object (already loaded).
    channel : str
        Channel name to extract (e.g., 'EEG', 'EMG1', 'EMG2').

    Returns
    -------
    dataobject : DataObject
        DataObject containing the channel data and sampling resolution.
    """

    # Check if channel exists 
    if channel not in raw.ch_names:
        raise FileNotFoundError(
            f"Channel '{channel}' not found. Available: {raw.ch_names}"
        )

    # Extract data
    # warning: It must be float64, 
    # otherwise the FFT will produce zero-valued results, 
    # causing the entropy calculation to fail with an error.
    idx = mne.pick_channels(raw.ch_names, include=[channel], ordered=False)
    data, _ = raw.get_data(picks=idx, return_times=True)
    signal = data.flatten().astype(np.float64)  # Convert to float64

    arr = np.asarray(signal)
    # must be exactly float64
    if arr.dtype != np.float64:
        raise ValueError(f"Data in channel '{channel}' must be float64, got {arr.dtype}.")

    # Sampling interval (1 / sampling frequency) 
    resolution = 1.0 / raw.info['sfreq']

    # Convert to DataObject 
    return DataObject(name=channel, data=signal, resolution=resolution)


def multi_channel_read_data(filepath, channels):
    """
    Load MNE Raw file (.fif) and extract data from multiple specified channels.

    Parameters
    ----------
    filepath : str
        Path to the .fif file (e.g., "subject_raw.fif").
    channels : list of str
        List of channel names to extract (e.g., ['EEG', 'EMG1', 'EMG2']).

    Returns
    -------
    dataobjects : list of DataObject
        List of DataObjects, each containing data from one of the specified channels.
    """

    # Load MNE Raw file
    try:
        raw = _load(filepath)
    except Exception as e:
        raise FileNotFoundError(f"Could not read file '{filepath}': {e}")

    dataobjects = []
    for channel in channels:
        dataobj = _read_ch_from_raw(raw, channel)
        dataobjects.append(dataobj)

    return tuple(dataobjects)

def read_labels(raw, channel, map={}):
    """
    Extract label data from an mne.io.Raw object.

    Parameters
    ----------
    raw : mne.io.Raw
        The MNE Raw object (already loaded).
    channel : str
        The channel name to extract (e.g., 'Stimulus' or 'Label').
    map : dict, optional
        Mapping of label values to new integer codes (e.g., {2:1, 3:0}).

    Returns
    -------
    dataobject : DataObject
        A DataObject containing the label data from the specified channel.
    """

    # Check if channel exists
    if channel not in raw.ch_names:
        raise FileNotFoundError(
            f"Channel '{channel}' not found. Available: {raw.ch_names}"
        )

    # Extract data from the specified channel
    data, times = raw.get_data(picks=[channel], return_times=True)
    labels = data.flatten()  # Flatten to 1D

    # Map values 
    if map:
        labels = np.vectorize(lambda x: map.get(x, x))(labels)

    # Convert to integers
    labels = labels.astype(int)

    # Sampling interval (1 / sfreq)
    resolution = 1.0 / raw.info['sfreq']

    return DataObject(name=channel, data=labels, resolution=resolution)

def write(
        filepath: str,
        labels: DataObject,
        map: Dict = {},
        epoch_size: int = 5,
    ):
    """
    Save only labels to an MNE Raw FIF file (no waveform channels).
    - Write integer codes to a single Stim channel.
    - Write human-readable strings to MNE Annotations.
    - The resulting Raw contains only one channel ('STI 014').

    Parameters
    ----------
    filepath : str
        Output file path ending with '.fif' (e.g., 'output/result.fif').
    labels : DataObject
        Per-epoch labels. Expects:
          - labels.data: list of int (one code per epoch)
          - labels.resolution: timebase in seconds (float), must be > 0
            Sampling frequency is derived as: sfreq = 1.0 / labels.resolution
    map : Dict
        Mapping from integer label -> display value.
        For Stim, an integer is required; for Annotations, a string is stored.
        Example: {0: 'AW', 1: 'QW', 2: 'NR', 3: 'R'}
    epoch_size : int
        Duration in seconds for each epoch (used to place events/annotations).

    Raises
    ------
    ValueError
        If labels.resolution is missing or non-positive.
    """

    # Determine sampling frequency (sfreq) 
    res = getattr(labels, "resolution", None)
    if res is None or res <= 0:
        raise ValueError("Either sfreq or labels.resolution (positive) must be provided")
    sfreq = 1.0 / float(res)

    # Determine time axis length 
    n_epochs = int(len(labels.data))
    samples_per_epoch = int(round(epoch_size * sfreq))
    if samples_per_epoch <= 0:
        # Ensure at least one sample per epoch
        samples_per_epoch = 1
    n_times = n_epochs * samples_per_epoch

    # Stim channel (integer event codes)
    data = np.zeros((2, n_times), dtype=np.float64)
    stim = data[0]
    state = data[1]

    for i, code in enumerate(labels.data):
        start = i * samples_per_epoch
        end = min((i + 1) * samples_per_epoch, n_times)
        stim[start] = code  # Fill the entire epoch with the code
        state[start:end] = code  # Fill the entire epoch with the code

    stim_info = mne.create_info(
        ch_names=['event', 'state'], 
        sfreq=float(sfreq), 
        ch_types=['stim', "misc"]  # type: ignore
        ) 
    raw = mne.io.RawArray([stim, state], stim_info, verbose=False)

    # Annotations (human-readable labels) 
    onsets = np.arange(n_epochs, dtype=float) * float(epoch_size)
    durations = np.full(n_epochs, float(epoch_size), dtype=float)
    descriptions = [str(map.get(code, code)) for code in labels.data]
    raw.set_annotations(mne.Annotations(onset=onsets, duration=durations, description=descriptions))

    # Save
    print(f"Writing labels to {filepath}")
    raw.save(filepath, overwrite=True, verbose=False)


def _load(filepath):
    """
    Attempt to load the .fif file as an MNE Raw object.

    Parameters
    ----------
    filepath : str
        Path to the .fif file.

    Returns
    -------
    raw_file : mne.io.Raw
        The MNE Raw object containing the loaded data.
    """
    try:
        # load as float64
        raw_file = mne.io.read_raw_fif(filepath, preload=True, verbose=False)
    except Exception:
        raise FileNotFoundError("No such file or directory: " + filepath)

    return raw_file