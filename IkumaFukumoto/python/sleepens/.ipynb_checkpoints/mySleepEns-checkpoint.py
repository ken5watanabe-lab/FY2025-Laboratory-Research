import joblib
from tqdm import trange
from pathlib import Path
import glob
import os
from sleepens.io import DataObject
from sleepens.protocols.sleepens4.params import params

from sklearn.utils.validation import assert_all_finite

from sleepens.protocols import protocols
from sleepens.protocols.sleepens4 import SleepEnsemble4
from sleepens.io import DataObject

import mneInterface
from processor import process as processor

version = "1.0.4"

# Override SleepEnsemble4.process to save some data during processing
SleepEnsemble4.process = lambda self, data, labels, name: processor(data, labels, name, self.params['process'], verbose=self.verbose)
model = SleepEnsemble4(params=params)
verbose = 4


def read_data(in_int, filepath, labels=False):
    global model
    print("Reading file", filepath)
    if labels:
        labels = in_int.read_labels(filepath, model.params['reader']['SCORE_NAME'],
                                    map=model.params['reader']['SCORE_MAP'])
    else:
        labels = None
    name = Path(filepath).stem
    data = in_int.multi_channel_read_data(
        filepath,
        [
            model.params['reader']['EEG_NAME'],
            model.params['reader']['NECK_NAME'],
            model.params['reader']['MASS_NAME']
        ]
    )
    ds = model.process(data, labels, name)

    return ds, data, labels


def write_data(out_int, destination, name, data, p=None):
    global model
    filepath = f"{destination}/{name}-predictions{out_int.filetypes[0][1][1:]}"
    print("Writing results")

    if p is None:
        print("No predictions used, no need to write raw data again")
        return
    result = DataObject(
        name="P", data=p, resolution=data[0].resolution / data[0].divide
    )
    out_int.write(
        filepath, result, map=model.params['process']['SCORE_MAP'],
        epoch_size=model.params['process']['EPOCH_SIZE'])


def load(file_path):
    global model
    print("-" * 30)
    print("Load Model")
    print("Current model:", model.name)
    print("-" * 30)
    protocol = protocols[0]

    print("Selected", protocol.__name__, "protocol")
    model = protocol(verbose=model.verbose)
    print("Selected", Path(file_path).stem)

    model.classifier = joblib.load(file_path)
    model.name = Path(file_path).stem
    print("Loaded", model.name)


def classify(filepaths, destination):
    global model
    print("-" * 30)
    print("Sleep Ensemble Classification")
    print("Current model:", model.name)
    print("-" * 30)
    in_int = mneInterface
    out_int = mneInterface
    print("Identified", len(filepaths), "files to classify")
    jobs = range(len(filepaths))
    for i in jobs:
        print("Classifying", filepaths[i])
        if os.path.exists(f"/home/data/sleepStateExperiment_from_video/spectral_band/{Path(filepaths[i]).stem}_eeg_bands.npz"):
            continue
        ds, data, labels = read_data(in_int, filepaths[i], labels=False)
        p, y_hat = model.predict([ds.data])
        write_data(out_int, destination, ds.name, data, p[0])
    print("Completed classification jobs!")


def main(eeg_type, emg_reverse=False):
    DATA_FOLDER = "/home/data/sleepStateExperiment_from_video"
    # select model(male and female)
    model_path = "/home/jupyter/sleepState_from_video/python/sleepens/joblib/SleepEnsemble4_1.0.1_mf-py3.7.8-win32-64bit.joblib"  # TODO: change file name

    # select target file
    # for now, select one file.
    if True:
        filepaths = [
            # reverse の場合はband_notch_reverse フォルダの方を指定する!!!!
            "/home/data/sleepStateExperiment_from_video/analysis_tmp/band_notch" + ("_reverse/R" if emg_reverse else "/") + "20250917-001{}-0.fif".format(eeg_type),
            "/home/data/sleepStateExperiment_from_video/analysis_tmp/band_notch" + ("_reverse/R" if emg_reverse else "/") + "20250917-001{}-1.fif".format(eeg_type),
            "/home/data/sleepStateExperiment_from_video/analysis_tmp/band_notch" + ("_reverse/R" if emg_reverse else "/") + "20250917-001{}-2.fif".format(eeg_type),
            "/home/data/sleepStateExperiment_from_video/analysis_tmp/band_notch" + ("_reverse/R" if emg_reverse else "/") + "20250917-001{}-3.fif".format(eeg_type),
        ]
    else:
        filepaths = glob.glob(str(Path(DATA_FOLDER, "mneRaw_band_notch", "*.fif")))
        filepaths = sorted(filepaths)
    # print(filepaths)
    # set output destination
    destination = Path(DATA_FOLDER, "sleepEnsOutput")

    # print(destination)
    load(model_path)
    classify(filepaths, destination)


if __name__ == "__main__":
    if True:
        eeg_type_list = ["HPC-1", "HPC-2", "S1-1", "S1-2", "Skull-1", "Skull-2"]
        emg_reverse = True
        for eeg_type in eeg_type_list:
            print(f"Processing for EEG type: {eeg_type}")
            params["reader"]["EEG_NAME"] = eeg_type
            params["reader"]["NECK_NAME"] = "EMG-1" if not emg_reverse else "EMG-2"
            params["reader"]["MASS_NAME"] = "EMG-2" if not emg_reverse else "EMG-1"
            main(eeg_type=eeg_type, emg_reverse=emg_reverse)
    else:
        eeg_type = "HPC-1"
        emg_reverse = True
        params["reader"]["EEG_NAME"] = eeg_type
        params["reader"]["NECK_NAME"] = "EMG-1" if not emg_reverse else "EMG-2"
        params["reader"]["MASS_NAME"] = "EMG-2" if not emg_reverse else "EMG-1"
        main(eeg_type=eeg_type)
