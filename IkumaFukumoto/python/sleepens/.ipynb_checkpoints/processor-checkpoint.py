import numpy as np

from sleepens.process import secondary as sec
from sleepens.io import Dataset
from sleepens.protocols.sleepens4.processor import _detrend, _fft, _rms, _prct, _ep_var, _entropy, _merge, _create_ds

# ==============<added>====================
from pathlib import Path
import mne
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Union, Optional

from sleepens.io._dataset import Dataset
from sklearn.utils.validation import assert_all_finite
def save_fft_npz(result: List[Dataset],
                 params: Dict[str, Any],
                 epoch_size: int,
                 out_path: Union[str, Path],
                 ch_names: Optional[List[str]] = None,
                 extra_meta: Optional[Dict[str, Any]] = None,
                 freqs_override: Optional[np.ndarray] = None):
    """
    FFT結果を .npz で保存（圧縮）。メタ情報は JSON を同梱。
    """
    assert type(result) is list and len(result) > 0, "result must be a non-empty list"
    for r in result:
        assert isinstance(r, (Dataset)), f"Unsupported FFT result type: {type(r)}"
    
    freqs = result[0].features
    specs = [np.asarray(ds.data) for ds in result]
    spec = np.concatenate(specs, axis=0)

    
    if freqs is None and freqs_override is not None:
        freqs = np.asarray(freqs_override)

    meta = {
        "epoch_size": int(epoch_size),
        "params": params,
        "ch_names": ch_names,
        **(extra_meta or {})
    }
    meta_json = json.dumps(meta, ensure_ascii=False)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        spec=spec,    
        freqs=freqs if freqs is not None else np.array([]),
        meta=np.frombuffer(meta_json.encode("utf-8"), dtype=np.uint8)
    )

def load_fft_npz(path: Union[str, Path]):
    """
    .npz を読み戻す（メタは dict に復元）。
    """
    with np.load(path, allow_pickle=False) as npz:
        spec = npz["spec"]
        freqs = npz["freqs"]
        freqs = None if freqs.size == 0 else freqs
        meta_json = npz["meta"].tobytes().decode("utf-8")
    return {"spec": spec, "freqs": freqs, "meta": json.loads(meta_json)}

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

    # --- MNE RawArray 作成 ---
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
# ==============</added>====================

def process(data, labels, name, params, verbose=0):
    eeg, neck, mass = data
    if verbose > 0 : print("Extracting Features")
    if verbose > 1 : print("Detrending Data")
    eeg, neck, mass = _detrend(eeg, neck, mass)
    if verbose > 1 : print("Conducting FFT Analysis")
    eeg_fft = _fft(params['EEG_FFT'], params['EPOCH_SIZE'], eeg)[0]
    neck_fft, mass_fft = _fft(params['EMG_FFT'], params['EPOCH_SIZE'], neck, mass)
    # ===============<added>===============
    # save detrended data
    DATA_FOLDER = "/home/data/sleepStateExperiment_from_video"

    save_path = Path(DATA_FOLDER, "mneRaw_detrend", name + ".fif")
    write_data(save_path, data)

    # save FFT results
    save_path = Path(DATA_FOLDER, "fft", name + "_eeg.npz")
    save_fft_npz(
        [eeg_fft],
        params=params['EEG_FFT'],
        epoch_size=params['EPOCH_SIZE'],
        out_path=save_path,
        ch_names=["eeg"],
        extra_meta={"source": name}
    )
    save_path = Path(DATA_FOLDER, "fft", name + "_neck.npz")
    save_fft_npz(
        [neck_fft],
        params=params['EMG_FFT'],
        epoch_size=params['EPOCH_SIZE'],
        out_path=save_path,
        ch_names=["neck"],
        extra_meta={"source": name}
    )
    save_path = Path(DATA_FOLDER, "fft", name + "_mass.npz")
    save_fft_npz(
        [mass_fft],
        params=params['EMG_FFT'],
        epoch_size=params['EPOCH_SIZE'],
        out_path=save_path,
        ch_names=["mass"],
        extra_meta={"source": name}
    )

    # TODO: spectral_bandを保存する？計算量次第かなーの気持ちだが。
    # 試さないことにはわからないので、いったん保留。


    #===============</added>===============
    if verbose > 1 : print("Calculating RMS")
    eeg_rms, neck_rms, mass_rms = _rms(params['EPOCH_SIZE'], eeg, neck, mass)
    if verbose > 1 : print("Calculating Percentile Mean")
    neck_prct, mass_prct = _prct(params['EPOCH_SIZE'], params['PRCTILE'], neck, mass)
    if verbose > 1 : print("Calculating Epoched Variance")
    neck_twitch, mass_twitch = _ep_var(params['EPOCHED_VAR'], params['EPOCH_SIZE'], neck, mass)
    if verbose > 1 : print("Calculating Spectral Entropy")
    eeg_entropy, neck_entropy, mass_entropy = _entropy(eeg_fft, neck_fft, mass_fft)
    if verbose > 1 : print("Calculating Frequency Bands")
    eeg_bands = sec.spectral_band(eeg_fft, bands=params['BANDS'], merge=params['BAND_MERGE'])

    # ==============<added>===============
    save_path = Path(DATA_FOLDER, "spectral_band", name + "_eeg_bands.npz")
    save_fft_npz(
        [eeg_bands],
        params={"bands": params['BANDS'], "merge": params['BAND_MERGE']},
        epoch_size=params['EPOCH_SIZE'],
        out_path=save_path,
        ch_names=[f"band_{i}" for i in range(eeg_bands.data.shape[1])],
        extra_meta={"source": name}
    )

    # ==============</added>===============
    if verbose > 1 : print("Calculating Frequency Ratios")
    ratios = sec.ratio(eeg_bands, ratios=params['RATIOS'])
    if verbose > 1 : print("Merging")
    emg_rms = _merge(mass_rms, neck_rms, feature='EMG RMS',
                                method=params['EMG_RMS_MERGE'])
    emg_prct = _merge(mass_prct, neck_prct, feature='EMG PRCT',
                                method=params['EMG_PRCT_MERGE'])
    emg_twitch = _merge(mass_twitch, neck_twitch, feature='EMG TWITCH',
                                method=params['EMG_TWITCH_MERGE'])
    emg_entropy = _merge(mass_entropy, neck_entropy, feature='EMG ENTROPY',
                                method=params['EMG_ENTROPY_MERGE'])
    features = [eeg_bands, ratios, eeg_rms, emg_rms, emg_prct,
                    eeg_entropy, emg_entropy, emg_twitch]
    if verbose > 1 : print("Creating Dataset")
    ds = _create_ds(features, overlap=False)
    if verbose > 1 : print("Transforming Data")
    ds = sec.transform(ds, ops=params['TRANSFORM'])
    ds.data -= np.mean(ds.data, axis=0)
    if labels is not None:
        if verbose > 1 : print("Adding Labels")
        labels = Dataset(label_names=['LABELS'], labels=labels.data[:-1].reshape(-1,1))
        ds = ds.concatenate(labels)
    ds.name = name
    ds.clean()

    return ds
