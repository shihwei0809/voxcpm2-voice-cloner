"""
embed_audio.py
將 WAV 音頻 base64 嵌入 summary_presentation.html，
讓 HTML 不依賴外部路徑，任何瀏覽器直接開就能播。
"""
import base64, re, os

HTML_PATH  = r"c:\GOOGLE ANGET\AI 克隆聲音\summary_presentation.html"
AUDIO_PATH = r"c:\GOOGLE ANGET\AI 克隆聲音\output\Shihwei_Project_Summary_小偉.wav"
OUT_PATH   = r"c:\GOOGLE ANGET\AI 克隆聲音\summary_presentation_embedded.html"

print(f"讀取音頻：{AUDIO_PATH}")
with open(AUDIO_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

data_uri = f"data:audio/wav;base64,{b64}"

print(f"讀取 HTML：{HTML_PATH}")
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 替換 audio src
original = 'output/Shihwei_Project_Summary_小偉.wav'
if original not in html:
    # fallback: any wav src
    html = re.sub(r'src="[^"]*\.wav"', f'src="{data_uri}"', html)
else:
    html = html.replace(original, data_uri)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
print(f"輸出完成：{OUT_PATH}  ({size_mb:.1f} MB)")
print("直接用瀏覽器開啟此檔案，音頻即可播放，無需伺服器。")
