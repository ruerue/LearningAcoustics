"""
WAV <-> NPZ 変換とロード/解析ヘルパー

wavfile/*.wav を Python で扱いやすい .npz に変換する。
スキーマは将来の周波数解析・dB SPL 表示に拡張できる構成。

スキーマ v1.1 (キー一覧):
  samples                   : np.ndarray   生サンプル shape=(N,) or (N, ch)
  sample_dtype              : str          'int16' など
  samplerate                : int32        Hz
  channels                  : int32
  bit_depth                 : int32
  n_frames                  : int64
  duration_sec              : float64
  full_scale                : float64      int -> float 変換時の分母
  source                    : str          元 WAV ファイル名
  recorded_at               : str          'YYYYMMDD_HHMMSS' (ファイル名から自動抽出)
  label                     : str          ファイル名末尾のラベル
  device                    : str          'iPhone built-in mic' 等
  mic_orientation           : str          'Front' / 'Back' / 'Bottom' / ''
  polar_pattern             : str          'Stereo' / 'Cardioid' / 'Omnidirectional' / ''
  audio_session_mode        : str          (v1.1+) 'Measurement' (AGC off, SPL校正可) /
                                           'Default' (AGC on, SPL校正不可) / ''
  preamp_gain_db            : float64      外部ゲイン
  cal_db_spl_at_full_scale  : float64      フルスケール=何 dB SPL か (NaN=未校正)
  cal_ref_freq_hz           : float64      校正基準周波数 (NaN=未校正)
  cal_method                : str          校正方法のメモ
  cal_date                  : str          校正実施日
  preprocess                : str          前処理メモ
  notes                     : str          自由記述
  schema_version            : str          '1.1'

v1.0 → v1.1 互換: audio_session_mode キーを追加。v1.0 で書かれた .npz は
load_npz() で読むと audio_session_mode='' (不明) として扱う。
"""

import os
import re
import wave
import warnings
from datetime import datetime

import numpy as np


SCHEMA_VERSION = '1.1'


def _window(name, n):
    """numpy のみの窓関数ディスパッチ。"""
    if name == 'hann':
        return np.hanning(n).astype(np.float64)
    if name == 'hamming':
        return np.hamming(n).astype(np.float64)
    if name == 'blackman':
        return np.blackman(n).astype(np.float64)
    if name in ('rect', 'boxcar', 'rectangular'):
        return np.ones(n, dtype=np.float64)
    raise ValueError('未対応の window: {!r}'.format(name))


def _third_octave_bands(fmin=20.0, fmax=20000.0):
    """ISO 1/3 オクターブの中心周波数と帯域端を返す (1000 Hz 基準)。"""
    n_lo = int(np.floor(np.log2(fmin / 1000.0) * 3))
    n_hi = int(np.ceil(np.log2(fmax / 1000.0) * 3))
    centers = 1000.0 * 2.0 ** (np.arange(n_lo, n_hi + 1) / 3.0)
    edges_lo = centers / (2.0 ** (1.0 / 6.0))
    edges_hi = centers * (2.0 ** (1.0 / 6.0))
    return centers, edges_lo, edges_hi

_NAME_RE = re.compile(r'^(\d{8})_(\d{6})_(.+)\.wav$', re.IGNORECASE)


def _parse_name(fname):
    """WAV ファイル名から (recorded_at, label) を抽出する。"""
    m = _NAME_RE.match(fname)
    if m:
        return m.group(1) + '_' + m.group(2), m.group(3)
    return '', os.path.splitext(fname)[0]


def _wav_to_array(path):
    """WAV をヘッダ情報つきで numpy 配列にデコードする。"""
    w = wave.open(path, 'rb')
    nch = w.getnchannels()
    sw = w.getsampwidth()
    fr = w.getframerate()
    nf = w.getnframes()
    raw = w.readframes(nf)
    w.close()
    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sw)
    if dtype is None:
        raise ValueError('unsupported sample width: {} byte'.format(sw))
    arr = np.frombuffer(raw, dtype=dtype)
    if nch > 1:
        arr = arr.reshape(-1, nch)
    return arr, fr, nch, sw, nf


def convert_wav_to_npz(
    wav_path,
    out_path,
    device='iPhone built-in mic',
    mic_orientation='',
    polar_pattern='',
    audio_session_mode='',
    preamp_gain_db=0.0,
    cal_db_spl_at_full_scale=float('nan'),
    cal_ref_freq_hz=float('nan'),
    cal_method='',
    cal_date='',
    preprocess='',
    notes='',
):
    """単一の WAV を .npz に変換する。

    保存内容のスキーマはモジュールの docstring を参照。
    校正関連フィールドは省略時 NaN/空文字で初期化される。

    audio_session_mode は SPL 校正値の信頼性に直結する。
    'Measurement' (AGC off) で撮った録音だけが SPL 校正に意味がある。
    record_mono_calibrated 経由なら 'Measurement' を渡すこと。
    """
    arr, fr, nch, sw, nf = _wav_to_array(wav_path)
    fname = os.path.basename(wav_path)
    ts, label = _parse_name(fname)
    full_scale = float(np.iinfo(arr.dtype).max) + 1.0
    np.savez_compressed(
        out_path,
        samples=arr,
        sample_dtype=str(arr.dtype),
        samplerate=np.int32(fr),
        channels=np.int32(nch),
        bit_depth=np.int32(sw * 8),
        n_frames=np.int64(nf),
        duration_sec=np.float64(nf / fr),
        full_scale=np.float64(full_scale),
        source=fname,
        recorded_at=ts,
        label=label,
        device=device,
        mic_orientation=mic_orientation,
        polar_pattern=polar_pattern,
        audio_session_mode=audio_session_mode,
        preamp_gain_db=np.float64(preamp_gain_db),
        cal_db_spl_at_full_scale=np.float64(cal_db_spl_at_full_scale),
        cal_ref_freq_hz=np.float64(cal_ref_freq_hz),
        cal_method=cal_method,
        cal_date=cal_date,
        preprocess=preprocess,
        notes=notes,
        schema_version=SCHEMA_VERSION,
    )
    return out_path


def convert_dir(src_dir, out_dir, verbose=True, **meta):
    """src_dir の *.wav すべてを out_dir に .npz として書き出す。

    Args:
        src_dir: WAV を探すディレクトリ
        out_dir: 出力ディレクトリ (なければ作成)
        verbose: 進捗を print するか
        **meta:  convert_wav_to_npz に渡す追加メタデータ

    Returns:
        作成された .npz パスのリスト
    """
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(src_dir)
    os.makedirs(out_dir, exist_ok=True)
    wavs = sorted([f for f in os.listdir(src_dir) if f.lower().endswith('.wav')])
    out_paths = []
    for i, name in enumerate(wavs, 1):
        src = os.path.join(src_dir, name)
        dst = os.path.join(out_dir, os.path.splitext(name)[0] + '.npz')
        convert_wav_to_npz(src, dst, **meta)
        out_paths.append(dst)
        if verbose:
            sz_in = os.path.getsize(src)
            sz_out = os.path.getsize(dst)
            ratio = sz_out / sz_in * 100 if sz_in else 0.0
            print('[{}/{}] {} -> {} ({:,} -> {:,} bytes, {:.1f}%)'.format(
                i, len(wavs), name, os.path.basename(dst), sz_in, sz_out, ratio))
    return out_paths


class WavRecord(object):
    """.npz から読み込んだ録音データのコンテナ。"""

    def __init__(self, path, npz):
        self.path = path
        self.samples = np.asarray(npz['samples'])
        self.samplerate = int(npz['samplerate'])
        self.channels = int(npz['channels'])
        self.bit_depth = int(npz['bit_depth'])
        self.n_frames = int(npz['n_frames'])
        self.duration_sec = float(npz['duration_sec'])
        self.full_scale = float(npz['full_scale'])
        self.source = str(npz['source'])
        self.recorded_at = str(npz['recorded_at'])
        self.label = str(npz['label'])
        self.device = str(npz['device'])
        self.mic_orientation = str(npz['mic_orientation'])
        self.polar_pattern = str(npz['polar_pattern'])
        # v1.0 互換: audio_session_mode は v1.1 で追加されたキー
        if 'audio_session_mode' in npz.files:
            self.audio_session_mode = str(npz['audio_session_mode'])
        else:
            self.audio_session_mode = ''
        self.preamp_gain_db = float(npz['preamp_gain_db'])
        self.cal_db_spl_at_full_scale = float(npz['cal_db_spl_at_full_scale'])
        self.cal_ref_freq_hz = float(npz['cal_ref_freq_hz'])
        self.cal_method = str(npz['cal_method'])
        self.cal_date = str(npz['cal_date'])
        self.preprocess = str(npz['preprocess'])
        self.notes = str(npz['notes'])
        self.schema_version = str(npz['schema_version'])

    @property
    def is_calibrated(self):
        return not np.isnan(self.cal_db_spl_at_full_scale)

    @property
    def is_calibration_trustworthy(self):
        """校正値が信頼できる条件: 校正済み AND Measurement モードで撮影。

        Default モード (AGC 有効) で撮ったファイルに校正値を入れても、
        入力レベルが変われば AGC のゲインが動くので絶対 SPL は信用できない。
        """
        return self.is_calibrated and self.audio_session_mode == 'Measurement'

    def to_float(self, dtype=np.float32):
        """サンプルを -1.0 ~ +1.0 の float に正規化して返す。"""
        return self.samples.astype(dtype) / self.full_scale

    def channel(self, idx):
        """指定チャンネルの 1 次元配列を返す。mono は idx=0 のみ。"""
        if self.samples.ndim == 1:
            if idx != 0:
                raise IndexError('mono recording: only channel 0 exists')
            return self.samples
        return self.samples[:, idx]

    def time_axis(self):
        """サンプル数に対応する時刻配列 (秒) を返す。"""
        return np.arange(self.n_frames) / self.samplerate

    def rms(self, channel=None):
        """RMS を返す (float, 正規化後の線形値)。channel=None で全chの平均。"""
        f = self.to_float(np.float64)
        if channel is not None and f.ndim == 2:
            f = f[:, channel]
        return float(np.sqrt(np.mean(f ** 2)))

    def dbfs(self, channel=None):
        """フルスケール基準の RMS dBFS。"""
        r = self.rms(channel=channel)
        return 20.0 * np.log10(r + 1e-20)

    def db_spl(self, channel=None):
        """校正されていれば dB SPL を返す。未校正なら NaN。

        SPL = 20*log10(rms_float) + cal_db_spl_at_full_scale - preamp_gain_db

        校正値が入っていても audio_session_mode が 'Measurement' でない場合
        は AGC で絶対レベルが信用できないため warning を出す。値そのものは
        相対比較等の用途で必要になりうるので計算は行う。
        """
        if not self.is_calibrated:
            return float('nan')
        if self.audio_session_mode != 'Measurement':
            warnings.warn(
                'audio_session_mode={!r}: AGC が有効な可能性があり SPL の'
                '絶対値は信用できません (相対比較目的で使用してください)'
                .format(self.audio_session_mode),
                stacklevel=2,
            )
        return self.dbfs(channel=channel) + self.cal_db_spl_at_full_scale - self.preamp_gain_db

    def _channel_data(self, channel):
        """指定チャンネルを 1D float64 で返す内部ヘルパ。"""
        x = self.to_float(np.float64)
        if x.ndim == 2:
            x = x[:, channel]
        return x

    def psd(self, channel=0, nperseg=8192, overlap=0.5, window='hann'):
        """Welch 法による片側 PSD を返す (numpy のみ実装)。

        Args:
            channel:  解析対象チャンネル (mono なら 0)
            nperseg:  セグメント長 (信号より長ければ自動で短縮)
            overlap:  セグメント間オーバーラップ率 (0.0 - <1.0)
            window:   'hann' / 'hamming' / 'blackman' / 'rect'

        Returns:
            (f, psd): f は Hz の 1D 配列、
                     psd は (FS-unit)^2/Hz の 1D 配列 (片側補正済)
        """
        x = self._channel_data(channel)
        fs = self.samplerate
        n = int(min(nperseg, len(x)))
        if n < 8:
            raise ValueError('信号が短すぎる (n={})'.format(n))
        w = _window(window, n)
        step = max(1, int(n * (1.0 - overlap)))
        n_seg = 1 + (len(x) - n) // step
        if n_seg < 1:
            raise ValueError('信号が短すぎる (segments=0)')
        norm = fs * float(np.sum(w ** 2))
        psd_acc = np.zeros(n // 2 + 1, dtype=np.float64)
        for i in range(n_seg):
            s = i * step
            seg = x[s:s + n] * w
            X = np.fft.rfft(seg)
            p = (np.abs(X) ** 2) / norm
            p[1:-1] *= 2.0
            psd_acc += p
        psd_acc /= n_seg
        f = np.fft.rfftfreq(n, d=1.0 / fs)
        return f, psd_acc

    def psd_db_per_hz(self, channel=0, nperseg=8192, overlap=0.5, window='hann'):
        """PSD を dB に直したもの。

        校正済 → dB SPL / sqrt(Hz)
        未校正 → dBFS / sqrt(Hz)
        校正済かつ Measurement モードでない場合は warning を出す。
        """
        f, psd_lin = self.psd(channel=channel, nperseg=nperseg,
                              overlap=overlap, window=window)
        db = 10.0 * np.log10(psd_lin + 1e-30)
        if self.is_calibrated:
            db = db + self.cal_db_spl_at_full_scale - self.preamp_gain_db
            if self.audio_session_mode != 'Measurement':
                warnings.warn(
                    'audio_session_mode={!r}: SPL 絶対値は信用できません'
                    .format(self.audio_session_mode),
                    stacklevel=2,
                )
        return f, db

    def band_spl_third_octave(
        self, channel=0, fmin=20.0, fmax=20000.0,
        nperseg=8192, overlap=0.5, window='hann',
    ):
        """1/3 オクターブ帯域 SPL (校正済) もしくは dBFS (未校正)。

        Returns:
            (centers, db): 中心周波数 (Hz) と帯域 dB の 1D 配列。
                           Nyquist より上の帯域は除外される。
        """
        f, psd_lin = self.psd(channel=channel, nperseg=nperseg,
                              overlap=overlap, window=window)
        centers, lo, hi = _third_octave_bands(fmin, fmax)
        df = float(f[1] - f[0])
        cal_off = (self.cal_db_spl_at_full_scale - self.preamp_gain_db
                   if self.is_calibrated else 0.0)
        out_c = []
        out_db = []
        for c, fl, fh in zip(centers, lo, hi):
            if fh > f[-1]:
                break
            mask = (f >= fl) & (f < fh)
            if not np.any(mask):
                continue
            ms = float(np.sum(psd_lin[mask]) * df)
            out_c.append(c)
            out_db.append(10.0 * np.log10(ms + 1e-30) + cal_off)
        if self.is_calibrated and self.audio_session_mode != 'Measurement':
            warnings.warn(
                'audio_session_mode={!r}: SPL 絶対値は信用できません'
                .format(self.audio_session_mode),
                stacklevel=2,
            )
        return np.array(out_c), np.array(out_db)

    def __repr__(self):
        return (
            'WavRecord(source={!r}, recorded_at={!r}, label={!r}, '
            'samplerate={}, channels={}, n_frames={}, calibrated={})'
        ).format(
            self.source, self.recorded_at, self.label,
            self.samplerate, self.channels, self.n_frames, self.is_calibrated,
        )


def load_npz(path):
    """変換済み .npz を WavRecord として読み込む。"""
    with np.load(path, allow_pickle=False) as npz:
        return WavRecord(path, npz)


def update_calibration(
    npz_path,
    cal_db_spl_at_full_scale=None,
    cal_ref_freq_hz=None,
    cal_method=None,
    cal_date=None,
    preamp_gain_db=None,
    audio_session_mode=None,
):
    """既存の .npz に校正情報を後から書き込む (上書き保存)。

    None を渡したフィールドは既存値を維持する。
    cal_date を None にして cal_db_spl_at_full_scale を更新した場合は
    本日の日付 (YYYYMMDD) を自動で記録する。

    audio_session_mode は録音時のセッションモードを後追いで記録する用。
    record_mono_calibrated 経由で撮ったが convert 時に渡し忘れた場合は
    'Measurement' を後付けすると db_spl() が信用できるようになる。
    """
    rec = load_npz(npz_path)
    if cal_db_spl_at_full_scale is not None:
        rec.cal_db_spl_at_full_scale = float(cal_db_spl_at_full_scale)
        if cal_date is None:
            cal_date = datetime.now().strftime('%Y%m%d')
    if cal_ref_freq_hz is not None:
        rec.cal_ref_freq_hz = float(cal_ref_freq_hz)
    if cal_method is not None:
        rec.cal_method = str(cal_method)
    if cal_date is not None:
        rec.cal_date = str(cal_date)
    if preamp_gain_db is not None:
        rec.preamp_gain_db = float(preamp_gain_db)
    if audio_session_mode is not None:
        rec.audio_session_mode = str(audio_session_mode)
    np.savez_compressed(
        npz_path,
        samples=rec.samples,
        sample_dtype=str(rec.samples.dtype),
        samplerate=np.int32(rec.samplerate),
        channels=np.int32(rec.channels),
        bit_depth=np.int32(rec.bit_depth),
        n_frames=np.int64(rec.n_frames),
        duration_sec=np.float64(rec.duration_sec),
        full_scale=np.float64(rec.full_scale),
        source=rec.source,
        recorded_at=rec.recorded_at,
        label=rec.label,
        device=rec.device,
        mic_orientation=rec.mic_orientation,
        polar_pattern=rec.polar_pattern,
        audio_session_mode=rec.audio_session_mode,
        preamp_gain_db=np.float64(rec.preamp_gain_db),
        cal_db_spl_at_full_scale=np.float64(rec.cal_db_spl_at_full_scale),
        cal_ref_freq_hz=np.float64(rec.cal_ref_freq_hz),
        cal_method=rec.cal_method,
        cal_date=rec.cal_date,
        preprocess=rec.preprocess,
        notes=rec.notes,
        schema_version=SCHEMA_VERSION,
    )
    return npz_path


def calibrate_from_reference(
    npz_path,
    reference_db_spl,
    channel=0,
    cal_ref_freq_hz=float('nan'),
    cal_method=None,
    cal_date=None,
    apply_to=(),
    window_sec=None,
):
    """SPL メータ等の参照読み値から cal_db_spl_at_full_scale を算出して
    npz に書き込む。同条件で撮った他の npz にも一括で同じ校正値を流用可能。

    校正式:
        SPL = dBFS + cal_db_spl_at_full_scale - preamp_gain_db
        => cal_db_spl_at_full_scale = reference_db_spl - dBFS + preamp_gain_db

    Args:
        npz_path:         校正用録音 (定常騒音を撮ったもの) の .npz パス
        reference_db_spl: 参照デバイスでの SPL 読み値 (dB SPL, Leq 推奨)
        channel:          解析対象チャンネル (mono なら 0)
        cal_ref_freq_hz:  1kHz 純音校正なら 1000.0、広帯域なら NaN
        cal_method:       校正方法のメモ。None で自動生成
        cal_date:         校正日 (None で今日, YYYYMMDD)
        apply_to:         同条件で撮った他の npz パスのリスト
                          audio_session_mode が一致しないと ValueError
        window_sec:       (start, end) 秒で中央切り出して RMS 計算
                          (立ち上がり/立ち下がりを除外したい場合に)

    Returns:
        計算された cal_db_spl_at_full_scale (float)

    Raises:
        ValueError: apply_to 内の npz の audio_session_mode が参照と異なる場合
    """
    rec = load_npz(npz_path)
    if rec.audio_session_mode != 'Measurement':
        warnings.warn(
            '校正用録音の audio_session_mode={!r}: 推奨は Measurement。'
            'Default モードでは AGC/処理の影響で校正値の物理的意味が弱まる。'
            .format(rec.audio_session_mode),
            stacklevel=2,
        )
    if window_sec is None:
        dbfs = rec.dbfs(channel=channel)
    else:
        x = rec.to_float(np.float64)
        if x.ndim == 2:
            x = x[:, channel]
        s = max(0, int(window_sec[0] * rec.samplerate))
        e = min(len(x), int(window_sec[1] * rec.samplerate))
        if e <= s:
            raise ValueError('window_sec={} が無効'.format(window_sec))
        seg = x[s:e]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        dbfs = 20.0 * np.log10(rms + 1e-20)
    if dbfs < -55.0:
        warnings.warn(
            '校正用録音の dBFS={:.1f} は低すぎる可能性 (ノイズフロア相当)。'
            'スピーカ音量を上げて再録音を推奨。'.format(dbfs),
            stacklevel=2,
        )
    cal = float(reference_db_spl) - dbfs + rec.preamp_gain_db
    if cal_method is None:
        cal_method = 'SLM transfer (ref={:.2f} dB SPL'.format(reference_db_spl)
        if not np.isnan(cal_ref_freq_hz):
            cal_method += ' @ {:.0f} Hz'.format(cal_ref_freq_hz)
        cal_method += ')'
    update_calibration(
        npz_path,
        cal_db_spl_at_full_scale=cal,
        cal_ref_freq_hz=cal_ref_freq_hz,
        cal_method=cal_method,
        cal_date=cal_date,
    )
    for p in apply_to:
        other = load_npz(p)
        if other.audio_session_mode != rec.audio_session_mode:
            raise ValueError(
                'apply_to 不一致: {!r} の audio_session_mode={!r} は '
                '参照 {!r} の {!r} と異なる。校正値は流用できない。'
                .format(p, other.audio_session_mode,
                        npz_path, rec.audio_session_mode))
        update_calibration(
            p,
            cal_db_spl_at_full_scale=cal,
            cal_ref_freq_hz=cal_ref_freq_hz,
            cal_method='copied from {} ({})'.format(
                os.path.basename(npz_path), cal_method),
            cal_date=cal_date,
        )
    return cal
