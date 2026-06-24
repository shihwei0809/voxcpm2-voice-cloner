#!/usr/bin/env python3
"""
對話生成 — 三師爸與三帥媽的閒聊
模型只載入一次，逐句切換聲音生成，最後拼接成完整對話。
"""
from voxcpm import VoxCPM
import soundfile as sf
import numpy as np
import time
import os

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# 對話腳本：(說話者, 文字)
dialogue = [
    ("三帥媽", "嘿，你今天怎麼這麼晚才回來？"),
    ("三師爸", "喔，剛剛在弄一個 AI 語音的東西，搞到忘記時間了。"),
    ("三帥媽", "AI 語音？就是那個可以模仿別人聲音的嗎？"),
    ("三師爸", "對啊，叫 VoxCPM2，開源的，還可以商用。"),
    ("三帥媽", "聽起來很厲害耶，那它有辦法模仿我的聲音嗎？"),
    ("三師爸", "已經模仿了啊，你現在聽到的就是你的聲音。"),
    ("三帥媽", "哇，真的假的！那我以後是不是不用自己錄音了？"),
    ("三師爸", "哈，理論上是啦，但還是真人講的比較有感情啦。"),
]

def load_voice(voice_name):
    """讀取指定聲音的參考音與逐字稿。"""
    voice_dir = os.path.join(REPO_DIR, "voices", voice_name)
    ref_wav = os.path.join(voice_dir, "ref_voice.wav")
    prompt_file = os.path.join(voice_dir, "prompt.txt")
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()
    return ref_wav, prompt_text

def main():
    print("載入 VoxCPM2 模型...")
    t0 = time.time()
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, device="xpu", optimize=False)
    print(f"模型載入完成，耗時 {time.time()-t0:.1f}s\n")

    # 預載兩個聲音的參考資料
    voices = {}
    for name in ["三師爸", "三帥媽"]:
        voices[name] = load_voice(name)
        print(f"  已載入聲音: {name}")

    print(f"\n開始生成對話（{len(dialogue)} 句）...\n")

    clips = []
    for i, (speaker, text) in enumerate(dialogue, 1):
        ref_wav, prompt_text = voices[speaker]
        print(f"[{i}/{len(dialogue)}] {speaker}: {text}")

        t1 = time.time()
        wav = model.generate(
            text=text,
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            reference_wav_path=ref_wav,
            cfg_value=1.5,
            inference_timesteps=10,
        )
        elapsed = time.time() - t1
        duration = len(wav) / model.tts_model.sample_rate
        print(f"        -> {duration:.1f}s ({elapsed:.1f}s)")

        # 句子之間加 0.4 秒停頓
        pause = np.zeros(int(0.4 * model.tts_model.sample_rate), dtype=wav.dtype)
        clips.append(wav)
        clips.append(pause)

    # 拼接所有片段
    full_audio = np.concatenate(clips)
    total_duration = len(full_audio) / model.tts_model.sample_rate
    output_path = os.path.join(REPO_DIR, "output", "dialogue_三師爸_三帥媽.wav")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, full_audio, model.tts_model.sample_rate)

    print(f"\n對話生成完成！")
    print(f"  總長度: {total_duration:.1f}s")
    print(f"  檔案: {output_path}")

if __name__ == "__main__":
    main()
