#!/usr/bin/env python3
"""
record.py - 麥克風錄音，取得 Ultimate Cloning 所需的參考音與逐字稿。

流程：
  1. 螢幕顯示一段固定文字（texts/sample_text.txt 或自訂）
  2. 使用者對著麥克風朗讀
  3. 存成 voices/<voice>/ref_voice.wav（16kHz 單聲道）
  4. 文字內容同時存成 voices/<voice>/prompt.txt（逐字稿）

用法：
  python record.py                          # 預設聲音「三師爸」+ 預設文字
  python record.py --voice 我的聲音         # 指定聲音名稱
  python record.py --text-file my_text.txt  # 自訂朗讀文字
  python record.py --seconds 30             # 錄 30 秒
"""

import os
import sys
import time
import wave
import argparse
import numpy as np

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000
RECORD_SECONDS = 20


def load_text(filepath=None):
    """載入要朗讀的文字。"""
    if filepath is None:
        filepath = os.path.join(REPO_DIR, 'texts', 'sample_text.txt')
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def record_audio(seconds=RECORD_SECONDS, sr=SAMPLE_RATE):
    """從系統麥克風錄音，回傳 numpy array。"""
    import sounddevice as sd

    print(f'\n即將錄音 {seconds} 秒，取樣率 {sr}Hz。')
    print('準備好後按 Enter 開始...')
    input()

    print('錄音中...（請開始朗讀上面的文字）')
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype=np.float32)
    for i in range(seconds, 0, -1):
        print(f'\r剩餘: {i:2d} 秒', end='', flush=True)
        time.sleep(1)
    print('\r錄音完成！          ')
    sd.wait()
    return audio.flatten()


def save_wav(audio, filepath, sr=SAMPLE_RATE):
    """存成 WAV 檔。"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    duration = len(audio) / sr
    print(f'已存檔: {filepath} ({duration:.1f}s, {sr}Hz)')


def main():
    parser = argparse.ArgumentParser(description='VoxCPM2 參考音錄製')
    parser.add_argument('--voice', '-v', default='三師爸',
                        help='聲音名稱，存到 voices/<name>/（預設: 三師爸）')
    parser.add_argument('--text-file', '-t',
                        help='朗讀文字檔（預設: texts/sample_text.txt）')
    parser.add_argument('--seconds', '-s', type=int, default=RECORD_SECONDS,
                        help=f'錄音秒數（預設: {RECORD_SECONDS}）')
    args = parser.parse_args()

    text = load_text(args.text_file)

    voice_dir = os.path.join(REPO_DIR, 'voices', args.voice)
    wav_path = os.path.join(voice_dir, 'ref_voice.wav')
    prompt_path = os.path.join(voice_dir, 'prompt.txt')

    print('=' * 60)
    print(f'  VoxCPM2 Voice Cloner - 參考音錄製 [{args.voice}]')
    print('=' * 60)
    print()
    print('請朗讀以下文字（這段文字會作為逐字稿，請盡量自然地念）：')
    print()
    print('-' * 60)
    print(text)
    print('-' * 60)
    print()
    print(f'字數: {len(text.replace(" ", "").replace(",", "").replace("。", ""))} 字')
    print(f'預計朗讀時間: 約 {len(text) // 5} 秒')

    audio = record_audio(args.seconds)
    save_wav(audio, wav_path)

    # 同時存逐字稿
    os.makedirs(voice_dir, exist_ok=True)
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'逐字稿已存: {prompt_path}')

    print()
    print(f'「{args.voice}」聲音錄製完成！')
    print(f'  音檔: {wav_path}')
    print(f'  逐字稿: {prompt_path}')
    print()
    print(f'下一步：python clone.py "你想說的文字" --voice {args.voice}')


if __name__ == '__main__':
    main()
