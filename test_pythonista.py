import os, re, wave
import numpy as np

SRC_DIR = os.path.join(os.getcwd(), 'wavfile')
OUT_DIR = os.path.join(os.getcwd(), 'dataset')
SCHEMA_VERSION = '1.0'
_NAME_RE = re.compile(r'^(\d{8})_(\d{6})_(.+)\.wav$', re.IGNORECASE)

def parse_name(fname):
    m = _NAME_RE.match(fname)
    if m:
        return m.group(1) + '_' + m.group(2), m.group(3)
    return '', os.path.splitext(fname)[0]

def wav_to_array(path):
    w = wave.open(path, 'rb')
    nch = w.getnchannels(); sw = w.getsampwidth(); fr = w.getframerate(); nf = w.getnframes()
    raw = w.readframes(nf); w.close()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw)
    if dtype is None:
        raise ValueError('unsupported sample width: ' + str(sw))
    arr = np.frombuffer(raw, dtype=dtype)
    if nch > 1:
        arr = arr.reshape(-1, nch)
    return arr, fr, nch, sw, nf

def convert_one(wav_path, out_path):
    arr, fr, nch, sw, nf = wav_to_array(wav_path)
    fname = os.path.basename(wav_path)
    ts, label = parse_name(fname)
    np.savez_compressed(
        out_path,
        # --- 音声データ本体 ---
        samples=arr,
        sample_dtype=str(arr.dtype),
        # --- 基本フォーマット (FFT/スペクトログラムに必要) ---
        samplerate=np.int32(fr),
        channels=np.int32(nch),
        bit_depth=np.int32(sw * 8),
        n_frames=np.int64(nf),
        duration_sec=np.float64(nf / fr),
        # --- 数値スケーリング (int16 -> float 変換用) ---
        full_scale=np.float64(np.iinfo(arr.dtype).max + 1),
        # --- 録音メタ (ファイル名から自動抽出) ---
        source=fname,
        recorded_at=ts,
        label=label,
        # --- デバイス / マイク (後で書き換えできる空欄) ---
        device='iPhone built-in mic',
        mic_orientation='',
        polar_pattern='',
        # --- 信号系 / SPL 校正用 (空のままでOK、校正したら埋める) ---
        preamp_gain_db=np.float64(0.0),
        cal_db_spl_at_full_scale=np.float64(np.nan),
        cal_ref_freq_hz=np.float64(np.nan),
        cal_method='',
        cal_date='',
        # --- フィルタ / 前処理メモ ---
        preprocess='',
        notes='',
        # --- バージョニング ---
        schema_version=SCHEMA_VERSION,
    )

print('SRC:', SRC_DIR)
print('OUT:', OUT_DIR)
if not os.path.isdir(SRC_DIR):
    print('[NG] wavfile/ が存在しません')
    raise SystemExit
os.makedirs(OUT_DIR, exist_ok=True)
wav_list = sorted([f for f in os.listdir(SRC_DIR) if f.lower().endswith('.wav')])
print('対象 WAV:', len(wav_list), '件')
print('-' * 60)
for i, name in enumerate(wav_list, 1):
    src = os.path.join(SRC_DIR, name)
    dst = os.path.join(OUT_DIR, os.path.splitext(name)[0] + '.npz')
    try:
        convert_one(src, dst)
        sz_in = os.path.getsize(src); sz_out = os.path.getsize(dst)
        ratio = sz_out / sz_in * 100
        print('[{}/{}] {}'.format(i, len(wav_list), name))
        print('    -> {}  ({:,} -> {:,} bytes, {:.1f}%)'.format(os.path.basename(dst), sz_in, sz_out, ratio))
    except Exception as e:
        print('[NG] {}: {}: {}'.format(name, type(e).__name__, e))

print('-' * 60)
print('=== 試し読み (最初の1件) ===')
if wav_list:
    first = os.path.join(OUT_DIR, os.path.splitext(wav_list[0])[0] + '.npz')
    npz = np.load(first, allow_pickle=False)
    print('keys:', sorted(npz.files))
    s = npz['samples']
    print('samples shape :', s.shape, 'dtype:', s.dtype)
    print('samplerate    :', int(npz['samplerate']))
    print('channels      :', int(npz['channels']))
    print('bit_depth     :', int(npz['bit_depth']))
    print('n_frames      :', int(npz['n_frames']))
    print('duration_sec  :', float(npz['duration_sec']))
    print('full_scale    :', float(npz['full_scale']))
    print('source        :', str(npz['source']))
    print('recorded_at   :', str(npz['recorded_at']))
    print('label         :', str(npz['label']))
    print('device        :', str(npz['device']))
    print('cal_db_spl_FS :', float(npz['cal_db_spl_at_full_scale']))
    print('schema_version:', str(npz['schema_version']))
    # float 化サンプル & 簡易 RMS
    sf = s.astype(np.float32) / float(npz['full_scale'])
    rms = float(np.sqrt(np.mean(sf.astype(np.float64) ** 2)))
    print('float32 -> RMS (linear):', rms)
    print('             dBFS      :', 20 * np.log10(rms + 1e-20))
    npz.close()
print('=== 完了 ===')
