"""
export_slides.py  ── STEP 1
============================
用系統 Python (有 win32com) 把 PPTX 匯出成 PNG 圖片。
執行：  python export_slides.py
"""

import os
import sys

PPTX_PATH  = r"c:\GOOGLE ANGET\AI 克隆聲音\Shihwei_Project_Summary.pptx"
SLIDES_DIR = r"c:\GOOGLE ANGET\AI 克隆聲音\output\slides_tmp"

def main():
    import win32com.client
    import pythoncom

    pythoncom.CoInitialize()
    pptx_abs = os.path.abspath(PPTX_PATH)
    out_abs  = os.path.abspath(SLIDES_DIR)
    os.makedirs(out_abs, exist_ok=True)

    print(f"[export_slides] 開啟 PPTX: {pptx_abs}")
    app = win32com.client.Dispatch("PowerPoint.Application")
    app.Visible = True

    prs = app.Presentations.Open(pptx_abs, ReadOnly=True, Untitled=False, WithWindow=False)
    total = prs.Slides.Count
    print(f"[export_slides] 共 {total} 張投影片")

    for i in range(1, total + 1):
        out_path = os.path.join(out_abs, f"slide_{i:03d}.png")
        prs.Slides(i).Export(out_path, "PNG", 1920, 1080)
        print(f"  [{i}/{total}] → {out_path}")

    prs.Close()
    app.Quit()
    pythoncom.CoUninitialize()
    print("[export_slides] 完成！")

if __name__ == "__main__":
    main()
