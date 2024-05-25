import gradio as gr
from numpy import maximum, minimum


def process_english(title, lyric):
    return switch_interface(title, lyric)

def process_korean(title, lyric):
    return switch_interface(title, lyric)

def switch_interface(title, lyric):
    numbered_lyric = ""
    count = 0
    lines = lyric.split('\n')
    numbered_lines = []
    for line in lines:
        if len(line) > 0:
            count += 1
            numbered_lyric += f"{count}. {line}\n"
            numbered_lines.append(line)

    global stored_lyrics
    stored_lyrics = numbered_lines

    return (gr.update(visible=False), # audio_input1
            gr.update(visible=False), # audio_input2
            gr.update(visible=False), # title_input
            gr.update(visible=False), # lyrics_input
            gr.update(visible=False), # submit_english_btn
            gr.update(visible=False), # submit_korean_btn
            gr.update(visible=True, value=f"<p style='font-size:160%;'>{title}</p>"), # hidden_title
            gr.update(visible=True, value=f"<p style='white-space: pre-wrap;'>{numbered_lyric}</p>"), # hidden_lyric
            gr.update(visible=True, value=0, maximum=count, minimum=0, step=1), # selected_line
            gr.update(visible=True, value="Choice a line you want to revise"), # selected_lyric
            gr.update(visible=True), # feedback_text
            gr.update(visible=True), # feedback_btn
            gr.update(visible=True)) # new_btn


def update_selected_lyric(selected_line):
    if 1 <= selected_line <= len(stored_lyrics):
        return gr.update(value=f"Selected line ({selected_line}): {stored_lyrics[selected_line-1]}")
    else:
        return gr.update(value="Choose a line you want to revise using the slider!")

def reset_interface():
    return (gr.update(visible=True), # audio_input1
            gr.update(visible=True), # audio_input2
            gr.update(value="", visible=True), # title_input
            gr.update(value="", visible=True), # lyrics_input
            gr.update(visible=True), # submit_english_btn
            gr.update(visible=True), # submit_korean_btn
            gr.update(visible=False), # hidden_title
            gr.update(visible=False), # hidden_lyric
            gr.update(value=0, visible=False), # selected_line
            gr.update(value="", visible=False), # selected_lyric
            gr.update(visible=False), # feedback_text
            gr.update(visible=False), # feedback_btn
            gr.update(visible=False)) # new_btn

# Gradio 인터페이스 설정
with gr.Blocks() as demo:
    with gr.Row():
        audio_input1 = gr.Audio(label="Original Audio", visible=True)
        audio_input2 = gr.Audio(label="Voice Sample (Optional)", visible=True)
    with gr.Row():
        title_input = gr.Textbox(label="Song Title", visible=True)
        lyrics_input = gr.Textbox(label="Song Lyrics", visible=True)

    submit_english_btn = gr.Button("Make English Lyrics")
    submit_korean_btn = gr.Button("Make Korean Lyrics")

    hidden_title= gr.HTML(visible=False)
    hidden_lyric= gr.HTML(visible=False)
    selected_line= gr.Slider(visible=False, interactive=True)
    selected_lyric= gr.HTML(visible=False)
    feedback_text = gr.Textbox(label="Feedback", visible=False, interactive=True)
    feedback_btn = gr.Button("Feedback", visible=False, interactive=True)
    new_btn = gr.Button("Make New", visible=False)

    submit_english_btn.click(
        process_english, 
        [title_input, lyrics_input], 
        [audio_input1, audio_input2, title_input, lyrics_input, submit_english_btn, submit_korean_btn, hidden_title, hidden_lyric, selected_line, selected_lyric, feedback_text, feedback_btn, new_btn]
    )

    submit_korean_btn.click(
        process_korean, 
        [title_input, lyrics_input], 
        [audio_input1, audio_input2, title_input, lyrics_input, submit_english_btn, submit_korean_btn, hidden_title, hidden_lyric, selected_line, selected_lyric, feedback_text, feedback_btn, new_btn]
    )

    selected_line.change(
        update_selected_lyric, 
        [selected_line], 
        [selected_lyric]
    )

    new_btn.click(
        reset_interface, 
        [], 
        [audio_input1, audio_input2, title_input, lyrics_input, submit_english_btn, submit_korean_btn, hidden_title, hidden_lyric, selected_line, selected_lyric, feedback_text, feedback_btn, new_btn]
    )

demo.launch()
