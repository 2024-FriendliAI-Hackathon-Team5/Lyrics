import gradio as gr
import librosa

def process_audio(file):
    # Load the audio file
    y, sr = librosa.load(file, sr=None)
    
    # Perform some audio processing (e.g., beat tracking)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo_value = float(tempo)
    
    # Return the tempo and the number of beats detected
    return f"Tempo: {tempo_value:.2f} BPM, Beats detected: {len(beats)}"

# Define the Gradio interface
interface = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath", label="Upload your audio file (MP3, M4A, etc.)"),
    outputs="text",
    title="Audio File Processor",
    description="Upload an MP3 or M4A file to analyze its tempo and beats."
)

# Launch the interface
interface.launch()
