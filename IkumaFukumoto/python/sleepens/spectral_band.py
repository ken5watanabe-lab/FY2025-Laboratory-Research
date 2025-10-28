import mne
from pathlib import Path
from sleepens.process.secondary import spectral_band
from mneInterface import read_data
from sleepens.protocols.sleepens4.params import params
DATA_FOLDER = Path("/home/data/sleepStateExperiment_from_video")
filepath = Path(DATA_FOLDER, "mneRaw_detrend", "20250917-001HPC-1-3.fif")

data = read_data(filepath, "eeg")
eeg_bands = spectral_band(data, bands=params['BANDS'], merge=params['BAND_MERGE'])


save_path = Path(DATA_FOLDER, "mneRaw_spectral_band", Path(filepath).name)