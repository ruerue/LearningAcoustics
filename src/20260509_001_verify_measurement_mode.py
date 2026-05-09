"""
AVAudioSessionModeMeasurement と Stereo polar pattern の両立可否を実機検証する。

背景:
  iPhone 内蔵マイク録音で SPL 校正を成立させるには AGC 無効化のため
  Measurement モードが必要。一方で Stereo 録音には polar pattern Stereo が
  必要。これらが共存できるかが公式 doc で曖昧なため、Pythonista 上で
  実際に AVAudioSession を構成して状態を確認する。

確認内容:
  Case A : default mode + Stereo polar pattern (現行の挙動・比較ベースライン)
  Case B : Measurement mode + Stereo polar pattern (理想ケース)
  Case C : Measurement mode のみ (polar pattern 未指定で何が選ばれるか)

各ケースで以下を印字:
  - session.category() / session.mode()
  - session.inputNumberOfChannels()
  - session.sampleRate()
  - session.inputGain() / isInputGainSettable()  (AGC ヒント)
  - selectedDataSource.dataSourceName() / orientation()
  - selectedDataSource.selectedPolarPattern() / supportedPolarPatterns()

判定:
  Case B で ch=2 かつ polarPattern selected が 'Stereo' なら両立可。
  そうでなければ SPL 校正用は mono 録音に切り替える二段構えとなる。

副作用なし: 録音は行わない。setActive(False) で必ず解放する。

実行:
  python3 src/20260509_001_verify_measurement_mode.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_session():
    import objc_util
    objc_util.load_framework('AVFoundation')
    AVAudioSession = objc_util.ObjCClass('AVAudioSession')
    return AVAudioSession.sharedInstance()


def _find_builtin_mic(session):
    inputs = session.availableInputs()
    if inputs is None:
        return None
    for i in range(len(inputs)):
        port = inputs[i]
        if str(port.portType()) == 'MicrophoneBuiltIn':
            return port
    return None


def _find_stereo_data_source(port, prefer_orientation='Front'):
    """Stereo を supportedPolarPatterns に含む data source を探す。"""
    sources = port.dataSources()
    if sources is None:
        return None
    preferred = None
    fallback = None
    for i in range(len(sources)):
        ds = sources[i]
        patterns = ds.supportedPolarPatterns()
        if not patterns:
            continue
        has_stereo = any('Stereo' in str(patterns[j]) for j in range(len(patterns)))
        if has_stereo:
            if fallback is None:
                fallback = ds
            if prefer_orientation in str(ds.orientation()):
                preferred = ds
    return preferred or fallback


def _report(label, session):
    print('--- {} : 確定状態 ---'.format(label))
    try:
        print('  category   : {}'.format(session.category()))
        print('  mode       : {}'.format(session.mode()))
        print('  ch         : {}'.format(session.inputNumberOfChannels()))
        print('  sampleRate : {}'.format(session.sampleRate()))
    except Exception as e:
        print('  [NG] session 基本属性取得失敗: {}'.format(e))
    try:
        ig = session.inputGain()
        gs = session.isInputGainSettable()
        print('  inputGain  : {:.4f} (settable={})'.format(float(ig), bool(gs)))
    except Exception as e:
        print('  inputGain  : 取得失敗 ({})'.format(e))
    pin = session.preferredInput()
    if pin is None:
        print('  preferredInput : None')
        return
    print('  preferredInput portType : {}'.format(pin.portType()))
    sds = None
    try:
        sds = pin.selectedDataSource()
    except Exception as e:
        print('  selectedDataSource : 取得失敗 ({})'.format(e))
    if sds is None:
        print('  selectedDataSource : None')
        return
    print('  dataSource : {} / orientation={}'.format(
        sds.dataSourceName(), sds.orientation()))
    try:
        sel_pp = sds.selectedPolarPattern()
    except Exception:
        sel_pp = None
    sup = sds.supportedPolarPatterns()
    sup_list = [str(sup[k]) for k in range(len(sup))] if sup else []
    print('  polarPattern selected={} supported={}'.format(sel_pp, sup_list))


def _try_config(label, session, mode, set_polar='Stereo', orientation='Front'):
    print('')
    print('=' * 60)
    print(label)
    print('=' * 60)
    session.setActive_error_(False, None)
    r = session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)
    print('  setCategory PlayAndRecord -> {}'.format(r))
    if mode is not None:
        r = session.setMode_error_(mode, None)
        print('  setMode {} -> {}'.format(mode, r))
    port = _find_builtin_mic(session)
    if port is None:
        print('  [NG] 内蔵マイクが取れない')
        return
    session.setPreferredInput_error_(port, None)
    ds = _find_stereo_data_source(port, prefer_orientation=orientation)
    if ds is None:
        print('  [NG] Stereo 対応 data source 無し')
    else:
        port.setPreferredDataSource_error_(ds, None)
        if set_polar:
            r = ds.setPreferredPolarPattern_error_(set_polar, None)
            print('  setPreferredPolarPattern {} -> {}'.format(set_polar, r))
    r = session.setActive_error_(True, None)
    print('  setActive(True) -> {}'.format(r))
    r = session.setPreferredInputNumberOfChannels_error_(2, None)
    print('  setPreferredInputNumberOfChannels(2) -> {}'.format(r))
    _report(label, session)


def main():
    session = _load_session()
    print('AVAudioSession instance OK')
    inputs = session.availableInputs()
    print('availableInputs count = {}'.format(len(inputs) if inputs else 0))
    _try_config(
        'Case A : default mode + Stereo polar pattern (baseline)',
        session, mode=None, set_polar='Stereo')
    _try_config(
        'Case B : Measurement mode + Stereo polar pattern (ideal)',
        session, mode='AVAudioSessionModeMeasurement', set_polar='Stereo')
    _try_config(
        'Case C : Measurement mode only (polar pattern 未指定)',
        session, mode='AVAudioSessionModeMeasurement', set_polar=None)
    session.setActive_error_(False, None)
    print('')
    print('=== 検証完了 ===')
    print('判定:')
    print('  Case B で ch=2 かつ polarPattern selected=Stereo')
    print('    -> Measurement と Stereo は両立可。1行追加で完了。')
    print('  Case B で ch=1 もしくは polarPattern selected!=Stereo')
    print('    -> 両立不可。SPL 校正用は mono 録音 API を別途用意する。')


if __name__ == '__main__':
    main()
