"""
校正値の永続化ストア。

(device, mic_orientation, polar_pattern, audio_session_mode) の組ごとに
cal_db_spl_at_full_scale 等の値を JSON ファイルに保存し、convert_wav_to_npz
から自動再利用できるようにする。

iPhone 内蔵マイク + Measurement モード + 同じ data source / polar pattern で
撮るかぎり、cal_db_spl_at_full_scale はハードウェア定数なので毎回校正し
直す必要はない。一度測ってストアに入れておけば、以後の録音はその値を
そのまま使える。

保存先: <project_root>/calibration_store.json
        (機種固有なので .gitignore に登録)

JSON スキーマ:
{
  "<device>|<mic_orientation>|<polar_pattern>|<audio_session_mode>": {
    "device": "iPhone built-in mic",
    "mic_orientation": "Front",
    "polar_pattern": "Cardioid",
    "audio_session_mode": "Measurement",
    "cal_db_spl_at_full_scale": 124.80,
    "cal_ref_freq_hz": NaN,
    "cal_method": "NIOSH SLM 70.5 dB SPL @ 2026-05-09",
    "cal_date": "20260509"
  },
  ...
}
"""

import json
import math
import os
from datetime import datetime


_STORE_FILENAME = 'calibration_store.json'


def _store_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), _STORE_FILENAME)


def _make_key(device, mic_orientation, polar_pattern, audio_session_mode):
    return '|'.join(str(x) for x in
                    (device, mic_orientation, polar_pattern, audio_session_mode))


def _load_all():
    p = _store_path()
    if not os.path.exists(p):
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_all(d):
    p = _store_path()
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)


def _nan_to_null(x):
    """JSON 非対応の NaN を None に変換 (load 側は None を NaN に戻す)。"""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def _null_to_nan(x):
    return float('nan') if x is None else x


def save_default_cal(
    device,
    mic_orientation,
    polar_pattern,
    audio_session_mode,
    cal_db_spl_at_full_scale,
    cal_ref_freq_hz=float('nan'),
    cal_method='',
    cal_date=None,
):
    """(device, mic_orientation, polar_pattern, audio_session_mode) の組
    に紐づく校正値をストアに保存する (上書き)。

    Measurement モード以外を保存しようとすると ValueError。
    cal_date を None にすると今日の日付 (YYYYMMDD) を自動設定。
    """
    if audio_session_mode != 'Measurement':
        raise ValueError(
            'デフォルト校正値は Measurement モード限定: '
            'audio_session_mode={!r}'.format(audio_session_mode))
    if cal_date is None:
        cal_date = datetime.now().strftime('%Y%m%d')
    key = _make_key(device, mic_orientation, polar_pattern, audio_session_mode)
    d = _load_all()
    d[key] = {
        'device': device,
        'mic_orientation': mic_orientation,
        'polar_pattern': polar_pattern,
        'audio_session_mode': audio_session_mode,
        'cal_db_spl_at_full_scale': float(cal_db_spl_at_full_scale),
        'cal_ref_freq_hz': _nan_to_null(float(cal_ref_freq_hz)),
        'cal_method': str(cal_method),
        'cal_date': str(cal_date),
    }
    _save_all(d)
    return d[key]


def load_default_cal(device, mic_orientation, polar_pattern, audio_session_mode):
    """ストアから校正値を取り出す。無ければ None。"""
    key = _make_key(device, mic_orientation, polar_pattern, audio_session_mode)
    entry = _load_all().get(key)
    if entry is None:
        return None
    out = dict(entry)
    out['cal_ref_freq_hz'] = _null_to_nan(out.get('cal_ref_freq_hz'))
    return out


def list_default_cals():
    """登録済み校正値の一覧を辞書で返す。"""
    d = _load_all()
    for k in d:
        d[k]['cal_ref_freq_hz'] = _null_to_nan(d[k].get('cal_ref_freq_hz'))
    return d


def remove_default_cal(device, mic_orientation, polar_pattern, audio_session_mode):
    """ストアから校正値を削除する。存在しなければ False、削除したら True。"""
    key = _make_key(device, mic_orientation, polar_pattern, audio_session_mode)
    d = _load_all()
    if key not in d:
        return False
    del d[key]
    _save_all(d)
    return True
