"""
make_video.py  ── STEP 2
=========================
用 venv Python (有 moviepy) 把投影片圖片 + 音頻合成 MP4。
執行：  .venv\Scripts\python.exe make_video.py
"""

import os
import glob
import shutil

SLIDES_DIR = r"c:\GOOGLE ANGET\AI 克隆聲音\output\slides_tmp"
AUDIO_PATH = r"c:\GOOGLE ANGET\AI 克隆聲音\output\Shihwei_Project_Summary_小偉.wav"
OUTPUT_MP4 = r"c:\GOOGLE ANGET\AI 克隆聲音\output\Shihwei_Project_Summary_小偉.mp4"

# 每張投影片時間點（秒），None = 平均分配
# 若要手動指定：SLIDE_TIMES = [8, 14, 14, 14, 10]
SLIDE_TIMES = None


def get_audio_duration(path: str) -> float:
    import wave
    with wave.open(path, 'rb') as wf:
        return wf.getnframes() / wf.getframerate()


def main():
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

    slide_paths = sorted(glob.glob(os.path.join(SLIDES_DIR, "slide_*.png")))
    if not slide_paths:
        raise FileNotFoundError(f"找不到投影片圖片，請先執行 export_slides.py\n路徑：{SLIDES_DIR}")

    total_dur = get_audio_duration(AUDIO_PATH)
    n = len(slide_paths)
    print(f"[make_video] 投影片數={n}，音頻長度={total_dur:.1f}s")

    if SLIDE_TIMES is None:
        times = [total_dur / n] * n
    else:
        times = list(SLIDE_TIMES)
        times[-1] = max(total_dur - sum(times[:-1]), 1.0)

    for i, (p, t) in enumerate(zip(slide_paths, times), 1):
        print(f"  Slide {i}: {t:.1f}s  {os.path.basename(p)}")

    print("[make_video] 合成影片中...")
    clips = [ImageClip(p).with_duration(t) for p, t in zip(slide_paths, times)]
    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(AUDIO_PATH)

    final_dur = min(video.duration, audio.duration)
    video = video.subclipped(0, final_dur)
    audio = audio.subclipped(0, final_dur)

    final = video.with_audio(audio)
    os.makedirs(os.path.dirname(OUTPUT_MP4), exist_ok=True)
    final.write_videofile(
        OUTPUT_MP4,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        threads=4,
        logger="bar",
    )
    print(f"\n✅ 影片輸出完成：{OUTPUT_MP4}")

    # 清除暫存
    shutil.rmtree(SLIDES_DIR, ignore_errors=True)
    print("🧹 暫存投影片圖片已清除。")


if __name__ == "__main__":
    main()
