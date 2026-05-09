"""Tools package for audio recording and processing"""

from .recording import (
    record_audio,
    record_audio_simple,
    record_with_label,
    record_stereo,
    record_stereo_with_label,
    record_mono_calibrated,
    record_mono_calibrated_with_label,
)
from .wav_dataset import (
    SCHEMA_VERSION,
    WavRecord,
    convert_wav_to_npz,
    convert_dir,
    load_npz,
    update_calibration,
    calibrate_from_reference,
    a_weighting_db,
    c_weighting_db,
)
from .calibration_store import (
    save_default_cal,
    load_default_cal,
    list_default_cals,
    remove_default_cal,
)

__all__ = [
    'record_audio',
    'record_audio_simple',
    'record_with_label',
    'record_stereo',
    'record_stereo_with_label',
    'record_mono_calibrated',
    'record_mono_calibrated_with_label',
    'SCHEMA_VERSION',
    'WavRecord',
    'convert_wav_to_npz',
    'convert_dir',
    'load_npz',
    'update_calibration',
    'calibrate_from_reference',
    'a_weighting_db',
    'c_weighting_db',
    'save_default_cal',
    'load_default_cal',
    'list_default_cals',
    'remove_default_cal',
]
