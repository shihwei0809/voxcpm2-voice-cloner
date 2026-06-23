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
    
    # 支援雲端硬碟備份庫查找
    if not os.path.exists(ref_wav):
        gdrive = get_gdrive_root()
        if gdrive:
            g_voice_dir = os.path.join(gdrive, "AI 克隆聲音", "voices", voice_name)
            g_ref = os.path.join(g_voice_dir, "ref_voice.wav")
            g_txt = os.path.join(g_voice_dir, "prompt.txt")
            if os.path.exists(g_ref):
                ref_wav = g_ref
                prompt_file = g_txt
                
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()
    return ref_wav, prompt_text


def get_gdrive_root():
    possible_roots = [
        r"G:\我的雲端硬碟\GOOGLE ANGET",
        r"G:\My Drive\GOOGLE ANGET"
    ]
    for root in possible_roots:
        if os.path.exists(root):
            return root
    return None

def main():
    print("載入 VoxCPM2 模型...")
    t0 = time.time()
    # 支援動態選擇 GPU / XPU / CPU
    import torch
    if torch.cuda.is_available():
        dev = "cuda"
    elif hasattr(torch, "xpu") and torch.xpu.is_available():
        dev = "xpu"
    else:
        dev = "cpu"
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, device=dev, optimize=False)
    print(f"模型載入完成，裝置: {dev}，耗時 {time.time()-t0:.1f}s\n")

    # 預載兩個聲音的參考資料
    voices = {}
    for name in ["三師爸", "三帥媽"]:
        # 雲端庫優先或 fallback 邏輯已由 load_voice 本身處理（若 voices 資料夾不存在則在 load_voice 中檢查）
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

    # 同步複製到 Google Drive 雲端硬碟共用資料夾
    gdrive = get_gdrive_root()
    if gdrive:
        try:
            gdrive_output_dir = os.path.join(gdrive, "AI 克隆聲音", "output")
            os.makedirs(gdrive_output_dir, exist_ok=True)
            import shutil
            dest_path = os.path.join(gdrive_output_dir, os.path.basename(output_path))
            shutil.copy2(output_path, dest_path)
            print(f"已同步備份至雲端硬碟: {dest_path}")
        except Exception as e:
            print(f"同步至雲端硬碟失敗: {e}")


if __name__ == "__main__":
    main()
