import tkinter as tk
import sounddevice as sd
import numpy as np
import threading
import soundfile as sf
from scipy.signal import resample

class SoundRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Voice Cloner")
        self.root.geometry("300x200")

        # Label to display "Custom Voice Cloner"
        self.label = tk.Label(root, text="Custom Voice Cloner", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.is_recording = False
        self.record_button = tk.Button(root, text="Start Recording", command=self.toggle_record)
        self.record_button.pack(pady=10)

        # Add a button for noise reduction
        self.noise_reduction_button = tk.Button(root, text="Apply Noise Reduction", command=self.apply_noise_reduction)
        self.noise_reduction_button.pack(pady=10)

        # Noise reduction parameters
        self.noise_duration = 3  # Duration (in seconds) for noise profile estimation
        self.smoothing_factor = 0.8  # Smoothing factor for noise profile

        # Initialize noise profile
        self.noise_profile = None

    def toggle_record(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.start_recording()
        else:
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.stop_recording()

    def start_recording(self):
        self.audio_data = []
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()

    def _record_audio(self):
        samplerate = 44100  # You can change this to your desired sample rate
        duration = 10  # You can change this to your desired recording duration

        with sd.InputStream(callback=self._callback, channels=1, samplerate=samplerate):
            sd.sleep(int(duration * 1000))

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)

        if self.is_recording:
            self.audio_data.append(indata.copy())

            # Update the noise profile during the initial recording
            if len(self.audio_data) <= int(self.noise_duration * 44100):
                self.update_noise_profile(indata)

    def stop_recording(self):
        if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
            self.recording_thread.join()
        if hasattr(self, 'audio_data'):
            self.save_audio()

    def update_noise_profile(self, audio_chunk):
        if self.noise_profile is None:
            self.noise_profile = np.abs(audio_chunk)
        else:
            self.noise_profile = self.smoothing_factor * self.noise_profile + \
                                 (1 - self.smoothing_factor) * np.abs(audio_chunk)

    def apply_noise_cancellation(self, audio_data, target_sr):
        if self.noise_profile is not None:
            return audio_data  # You can add noise reduction processing here
        return audio_data

    def apply_noise_reduction(self):
        if hasattr(self, 'audio_data'):
            audio_array = np.concatenate(self.audio_data, axis=0)

            # Downsample the audio to reduce memory usage
            original_sr = 44100  # Original sample rate
            target_sr = 16000  # Target sample rate (you can adjust this)
            audio_array = resample(audio_array, int(len(audio_array) * target_sr / original_sr))

            audio_array = self.apply_noise_cancellation(audio_array, target_sr)  # Apply noise cancellation

            # Save the audio as a WAV file after noise reduction
            filename = "recorded_audio_with_noise_reduction.wav"
            sf.write(filename, audio_array, target_sr)
            print(f"Audio saved with noise reduction as {filename}")

    def save_audio(self):
        if len(self.audio_data) == 0:
            return

        audio_array = np.concatenate(self.audio_data, axis=0)
        filename = "recorded_audio.wav"

        # Save the audio as a WAV file
        sf.write(filename, audio_array, 44100)
        print(f"Audio saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundRecorder(root)
    root.mainloop()
