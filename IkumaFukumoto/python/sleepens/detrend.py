import  joblib
from tqdm import trange
from pathlib import Path
import glob
import os
from sleepens.io import DataObject
from sleepens.protocols.sleepens4.params import params

from sklearn.utils.validation import assert_all_finite
import numpy as np

from sleepens.protocols import protocols
from sleepens.protocols.sleepens4 import SleepEnsemble4
from sleepens.io import DataObject
from sleepens.protocols.sleepens4.processor import _detrend as detrend

import mneInterface
import mne

# ===================================
# This code is included in python/sleepens/processor.py due to avoid running same functions in different files.
# In other words, this file won't be used as a pipeline.
# ===================================

version = "1.0.4"
params["reader"]["EEG_NAME"] = "S1-1"
params["reader"]["NECK_NAME"] = "EMG-1"
params["reader"]["MASS_NAME"] = "EMG-2"
verbose = 4



def read_data(file):
    data = mneInterface.multi_channel_read_data(
         file,
         [
            params['reader']['EEG_NAME'], 
            params['reader']['NECK_NAME'], 
            params['reader']['MASS_NAME']
        ]
    )
    return data

# ===== 保存本体: 刺激チャネルやアノテーションは作らない =====
def write_data(save_path, data):
    """
    save_path: 保存するパス（拡張子は .fif 固定）
    data: (eeg, neck, mass) のタプル。各要素は 1D 配列（もしくは .resolution を持つオブジェクト）
    """
    print("Writing results")


    # --- データ整形 ---
    eeg, neck, mass = data
    eeg = np.asarray(eeg.data, dtype=np.float32)
    neck = np.asarray(neck.data, dtype=np.float32)
    mass = np.asarray(mass.data, dtype=np.float32)

    sfreq = float(1.0 / data[0].resolution)  # Hz

    print("Sampling frequency:", sfreq)

    # --- MNE RawArray 作成（シンプルに3chだけ） ---
    X = np.vstack([eeg, neck, mass])  # (n_channels, n_times)
    ch_names = ["eeg", "neck", "mass"]
    ch_types = ["eeg", "emg", "emg"]
    info = mne.create_info(
        ch_names=ch_names, 
        sfreq=float(sfreq), 
        ch_types=ch_types # type: ignore
        )
    raw = mne.io.RawArray(X, info, verbose=False)

    # --- 保存 ---
    raw.save(save_path, overwrite=True, verbose=False)
    print(f"Saved: {save_path}")
    return save_path

def main():
    DATA_FOLDER = "/home/data/sleepStateExperiment_from_video"
    # select model(male and female)

    # select target file
    # for now, select one file.
    if True:
        filepaths = [
            "/home/data/sleepStateExperiment_from_video/mneRaw_band_notch/20250917-001-3.fif",
        ]
    else:
        filepaths = glob.glob(str(Path(DATA_FOLDER, "mneRaw", "*.fif")))
        filepaths = sorted(filepaths)


    # set output destination
    for filepath in filepaths:
        data = read_data(filepath)
        data = detrend(*data)

        # save
        save_path = Path(DATA_FOLDER, "mneRaw_detrend", Path(filepath).name)
        write_data(save_path, data)


if __name__ == "__main__":
	main()