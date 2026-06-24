#!/usr/bin/env python3
"""
app.py - VoxCPM2 語音錄製工具
唯一的 UI：錄音 + 儲存。克隆與生成交由 AI Agent 處理。

用法：
  python app.py              # http://127.0.0.1:7860
"""

import os
import numpy as np
import gradio as gr

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000

CUSTOM_CSS = """
body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Microsoft JhengHei', sans-serif;
}

/* Light Mode Card Styling */
.step-box {
    background: #ffffff !important;
    color: #1e293b !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin: 16px 0 !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.step-box:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
}

/* Dark Mode Card Styling */
.dark .step-box {
    background: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
}
.dark .step-box:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2) !important;
}

/* Card titles and headings color override */
.step-box h2, .step-box p, .step-box li {
    color: inherit !important;
}
.step-box h2 {
    font-weight: 700 !important;
    margin-bottom: 12px !important;
}

/* Sample Text Box (yellow paper look) */
.sample-text-box {
    background: #fffbeb !important;
    color: #78350f !important;
    border: 1px solid #fef3c7 !important;
    padding: 20px !important;
    border-radius: 12px !important;
    font-size: 1.15em !important;
    line-height: 1.8 !important;
    margin: 12px 0 !important;
    font-weight: 500 !important;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02) !important;
}
.dark .sample-text-box {
    background: #1e1b4b !important;
    color: #c7d2fe !important;
    border: 1px solid #312e81 !important;
}

/* Hint and helper text color */
.hint-text {
    text-align: center !important;
    margin-top: 12px !important;
    font-size: 0.95em !important;
    color: #475569 !important;
    font-weight: 500 !important;
}
.dark .hint-text {
    color: #94a3b8 !important;
}

/* Main Title styling */
.main-title {
    font-size: 2.2em !important;
    margin-bottom: 8px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}
.dark .main-title {
    color: #f8fafc !important;
}
.main-subtitle {
    font-size: 1.1em !important;
    color: #475569 !important;
}
.dark .main-subtitle {
    color: #94a3b8 !important;
}

/* Footer styling */
.footer-text {
    text-align: center !important;
    margin-top: 32px !important;
    padding: 16px !important;
    font-size: 0.85em !important;
    color: #94a3b8 !important;
    border-top: 1px solid #e2e8f0 !important;
}
.dark .footer-text {
    color: #64748b !important;
    border-top: 1px solid #334155 !important;
}
.footer-text a {
    color: #3b82f6 !important;
    text-decoration: none !important;
}
.footer-text a:hover {
    text-decoration: underline !important;
}
.success-msg { color:#10b981; font-weight:bold; }
"""


def list_voices():
    vdir = os.path.join(REPO_DIR, "voices")
    if not os.path.exists(vdir):
        return []
    return sorted(
        d for d in os.listdir(vdir)
        if os.path.isdir(os.path.join(vdir, d))
        and os.path.exists(os.path.join(vdir, d, "ref_voice.wav"))
    )


def load_voice_details(voice_name):
    if not voice_name:
        return None, ""
    wav_path = os.path.join(REPO_DIR, "voices", voice_name, "ref_voice.wav")
    prompt_path = os.path.join(REPO_DIR, "voices", voice_name, "prompt.txt")
    
    audio_val = wav_path if os.path.exists(wav_path) else None
    
    prompt_val = ""
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_val = f.read().strip()
        except Exception:
            pass
            
    return audio_val, prompt_val


def load_sample_text():
    path = os.path.join(REPO_DIR, "texts", "sample_text.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def list_generated_files():
    out_dir = os.path.join(REPO_DIR, "output")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(out_dir) if f.endswith(".wav")],
        key=lambda x: os.path.getmtime(os.path.join(out_dir, x)),
        reverse=True
    )
    return files


def load_history_audio(filename):
    if not filename:
        return None
    file_path = os.path.join(REPO_DIR, "output", filename)
    if os.path.exists(file_path):
        return file_path
    return None


def get_presentation_iframe():
    path = os.path.join(REPO_DIR, "summary_presentation.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html_content = f.read()
            html_content = html_content.replace('src="output/', 'src="file=output/')
            import html
            escaped_html = html.escape(html_content)
            return f'<iframe srcdoc="{escaped_html}" style="width:100%; height:720px; border:none; border-radius:16px;"></iframe>'
    return "<div style='padding:20px; text-align:center; color:#ef4444;'>⚠️ 找不到簡報播放器檔案 (summary_presentation.html)。</div>"


def on_save(audio_mic, audio_upload, voice_name):
    audio_data = audio_mic or audio_upload
    if audio_data is None:
        return "⚠️ 請先按「開始錄音」錄下你的聲音。"
    if not voice_name or not voice_name.strip():
        return "⚠️ 請為你的聲音取一個名字。"

    name = voice_name.strip()
    try:
        sr, audio = audio_data
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != SAMPLE_RATE:
            import resampy
            audio = resampy.resample(audio, sr, SAMPLE_RATE)
        peak = np.abs(audio).max()
        if peak > 0 and peak < 0.01:
            return "⚠️ 錄到的音量太小，請靠近麥克風再錄一次。"
        if peak > 0:
            audio = audio / peak * 0.95

        vdir = os.path.join(REPO_DIR, "voices", name)
        os.makedirs(vdir, exist_ok=True)
        import soundfile as sf
        sf.write(os.path.join(vdir, "ref_voice.wav"), audio.astype(np.float32), SAMPLE_RATE)
        with open(os.path.join(vdir, "prompt.txt"), "w", encoding="utf-8") as f:
            f.write(load_sample_text())

        duration = len(audio) / SAMPLE_RATE
        existing = list_voices()
        voice_list = "、".join(existing)
        return (
            f"✅ 聲音「{name}」錄製成功！（{duration:.0f} 秒）\n\n"
            f"目前已錄製的聲音：{voice_list}\n\n"
            f"👉 接下來，你可以對 AI 說：\n"
            f"「 用 {name} 的聲音說一段話 」"
        )
    except Exception as e:
        return f"❌ 儲存失敗：{e}"


def build_ui():
    sample_text = load_sample_text()

    with gr.Blocks(title="VoxCPM2 語音與簡報工具") as app:
        gr.HTML("""
        <div style="text-align:center; margin-bottom:24px;">
          <h1 class="main-title">🎙️ VoxCPM2 語音與簡報工具</h1>
          <p class="main-subtitle">在此錄製您的參考聲音、管理音庫，並以互動式網報同步播放您的專案簡報與克隆配音。</p>
        </div>
        """)

        with gr.Tabs():
            with gr.Tab("🎙️ 聲音錄製與庫管理"):
                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## ✏️ 為聲音取名字")
                    voice_name_input = gr.Textbox(
                        label="",
                        placeholder="例如：王老師、林主任...",
                        show_label=False,
                    )

                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 📖 請念這段文字")
                    gr.HTML(
                        f'<div class="sample-text-box">{sample_text}</div>'
                    )

                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 🎤 錄音並儲存")
                    audio_mic = gr.Audio(label="", type="numpy", sources=["microphone"], show_label=False)

                    gr.HTML('<div class="hint-text">👆 錄完後按這裡儲存 👇</div>')

                    with gr.Row():
                        save_btn = gr.Button("⬇️ 儲存聲音", variant="primary", size="lg")

                    with gr.Accordion("或上傳已錄好的音檔", open=False):
                        audio_upload = gr.Audio(label="", type="numpy", sources=["upload"], show_label=False)

                save_msg = gr.Textbox(label="", show_label=False, lines=5, interactive=False)

            with gr.Tab("📊 互動式簡報播放"):
                gr.HTML(get_presentation_iframe())

        with gr.Column(elem_classes="step-box"):
            gr.Markdown("## 🎙️ 已錄製的參考聲音 (本機聲音庫)")
            
            voice_choices = list_voices()
            voice_val = voice_choices[0] if voice_choices else None
            voice_audio, voice_prompt = load_voice_details(voice_val)
            
            with gr.Row():
                voice_dropdown = gr.Dropdown(
                    label="選擇聲音名稱",
                    choices=voice_choices,
                    value=voice_val,
                    interactive=True,
                    scale=4,
                    show_label=False
                )
                refresh_voices_btn = gr.Button("🔄 重新整理", variant="secondary", scale=1)
                
            with gr.Row():
                voice_audio_player = gr.Audio(
                    label="播放參考音",
                    value=voice_audio,
                    type="filepath",
                    interactive=False,
                    scale=2
                )
                voice_prompt_display = gr.Textbox(
                    label="朗讀文字 (Prompt)",
                    value=voice_prompt,
                    interactive=False,
                    scale=3,
                    lines=3
                )

        def on_voice_change(name):
            return load_voice_details(name)
            
        voice_dropdown.change(
            fn=on_voice_change,
            inputs=[voice_dropdown],
            outputs=[voice_audio_player, voice_prompt_display]
        )
        
        def on_refresh_voices():
            choices = list_voices()
            val = choices[0] if choices else None
            audio, prompt = load_voice_details(val)
            return gr.Dropdown(choices=choices, value=val), audio, prompt

        refresh_voices_btn.click(
            fn=on_refresh_voices,
            outputs=[voice_dropdown, voice_audio_player, voice_prompt_display]
        )

        save_btn.click(
            fn=on_save,
            inputs=[audio_mic, audio_upload, voice_name_input],
            outputs=[save_msg],
        ).then(
            fn=on_refresh_voices,
            outputs=[voice_dropdown, voice_audio_player, voice_prompt_display]
        )

        with gr.Column(elem_classes="step-box"):
            gr.Markdown("## 🎵 已生成的複製語音紀錄 (AI 生成庫)")
            
            initial_files = list_generated_files()
            initial_val = initial_files[0] if initial_files else None
            initial_audio = load_history_audio(initial_val)
            
            with gr.Row():
                history_dropdown = gr.Dropdown(
                    label="選擇音檔",
                    choices=initial_files,
                    value=initial_val,
                    interactive=True,
                    scale=4,
                    show_label=False
                )
                refresh_btn = gr.Button("🔄 重新整理", variant="secondary", scale=1)
                
            history_audio = gr.Audio(
                label="播放音檔",
                value=initial_audio,
                type="filepath",
                interactive=False
            )

        def on_dropdown_change(filename):
            return load_history_audio(filename)
            
        history_dropdown.change(
            fn=on_dropdown_change,
            inputs=[history_dropdown],
            outputs=[history_audio]
        )
        
        def on_refresh():
            files = list_generated_files()
            val = files[0] if files else None
            audio_path = load_history_audio(val)
            return gr.Dropdown(choices=files, value=val), audio_path

        refresh_btn.click(
            fn=on_refresh,
            outputs=[history_dropdown, history_audio]
        )

        gr.HTML("""
        <div class="footer-text">
        VoxCPM2（Apache-2.0 可商用） |
        <a href="https://github.com/mathruffian-dot/voxcpm2-voice-cloner" target="_blank">GitHub</a>
        </div>
        """)

    return app


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", "-p", type=int, default=7860)
    args = p.parse_args()
    build_ui().launch(server_name="0.0.0.0", server_port=args.port, css=CUSTOM_CSS, theme=gr.themes.Soft())
