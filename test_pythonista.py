# テスト Step 4: 正しい順番でステレオ設定
# Pythonista に貼り付けて実行してください

import objc_util
objc_util.load_framework('AVFoundation')

print("=== ステレオ設定(正しい順番)テスト ===\n")

AVAudioSession = objc_util.ObjCClass('AVAudioSession')
session = AVAudioSession.sharedInstance()

# 1. まずセッションを非アクティブ化してカテゴリ設定
session.setActive_error_(False, None)
session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)

# 2. 利用可能な入力ポートを取得
available_inputs = session.availableInputs()
builtin_port = None
for i in range(len(available_inputs)):
    port = available_inputs[i]
    if str(port.portType()) == 'MicrophoneBuiltIn':
        builtin_port = port
        break

if builtin_port is None:
    print("[NG] 内蔵マイクが見つかりません")
    raise SystemExit

# 3. セッションの優先入力ポートに内蔵マイクを設定
result = session.setPreferredInput_error_(builtin_port, None)
print(f"優先入力ポート設定: {result}")

# 4. データソースからステレオ対応のものを探す(前面を優先)
data_sources = builtin_port.dataSources()
stereo_ds = None
for i in range(len(data_sources)):
    ds = data_sources[i]
    patterns = ds.supportedPolarPatterns()
    if patterns:
        for j in range(len(patterns)):
            if 'Stereo' in str(patterns[j]):
                stereo_ds = ds
                print(f"ステレオ対応データソース: {ds.dataSourceName()} ({ds.orientation()})")
                break
    if stereo_ds:
        break

if stereo_ds is None:
    print("[NG] ステレオ対応データソースが見つかりません")
    raise SystemExit

# 5. ポートの優先データソースに設定
result = builtin_port.setPreferredDataSource_error_(stereo_ds, None)
print(f"優先データソース設定: {result}")

# 6. データソースにステレオポーラーパターンを設定
# 実際の定数値を確認するため両方試す
for pattern_str in ['AVAudioSessionPolarPatternStereo', 'Stereo']:
    result = stereo_ds.setPreferredPolarPattern_error_(pattern_str, None)
    print(f"ポーラーパターン設定 '{pattern_str}': {result}")
    if result:
        print("  → この文字列が正しい定数値です")
        break

# 7. セッションを再アクティブ化
result = session.setActive_error_(True, None)
print(f"セッション再有効化: {result}")

# 8. チャンネル数を確認
print(f"\n--- 設定後の状態 ---")
print(f"入力チャンネル数    : {session.inputNumberOfChannels()}")
print(f"最大入力チャンネル数: {session.maximumInputNumberOfChannels()}")
print(f"現在のポーラーパターン: {stereo_ds.selectedPolarPattern()}")
print(f"希望ポーラーパターン  : {stereo_ds.preferredPolarPattern()}")

# ステレオ要求
result = session.setPreferredInputNumberOfChannels_error_(2, None)
print(f"2ch 要求: {result}")
print(f"最終チャンネル数: {session.inputNumberOfChannels()}")

print("\n=== テスト完了 ===")
