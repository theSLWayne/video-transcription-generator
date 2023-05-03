"""
Script including functions used for transcript generation
"""

import os
from typing import Union
from pathlib import Path

import moviepy.editor as mp
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from resemblyzer import VoiceEncoder
from resemblyzer.audio import preprocess_wav, sampling_rate
from spectralcluster import SpectralClusterer
from scipy.io.wavfile import write, read
import numpy as np
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration

TMP_AUDIO_PATH = "preprocessed.wav"

def extract_audio(
    path: str, audio_path: str, save: bool = False
) -> Union[AudioFileClip, str]:
    """

    Extracts the audio from a given video file.

    Args:
        path: Path of the video file. Must be a valid path
        audio_path: Path to save the audio file. Must be a valid path
        save: Whether to save the audio or not. Optional. Defaulted to False

    Returns: 
        Extracted audio if save=False, else path of the saved audio file as a string
    """

    # Checking paths
    assert os.path.exists(path), f"Invalid video path: {path}"
    assert os.path.exists(audio_path), f"Invalid output path: {audio_path}"

    # Loading video file and extracting audio from it
    video = mp.VideoFileClip(filename=path)
    audio = video.audio

    # Saving the audio file
    if save:
        audio_fname = os.path.join(
            audio_path, f"{os.path.basename(path).split('.')[-2]}.wav"
        )
        audio.write_audiofile(audio_fname)
        return audio_fname
    else:
        return audio
    
def preprocess(audio_file_path: str) -> np.ndarray:
    """

    Preprocess the audio - removes background noise and remove non-speaking segments in the audio

    Args:
        audio_file_path: File path of the audio file

    Returns:
        Preprocessed audio as a numpy ndarray
    """

    # Load the audio and preprocess
    wav_fpath = Path(audio_file_path)
    wav = preprocess_wav(wav_fpath)

    # Write the preprocessed audio file to disk
    write(TMP_AUDIO_PATH, sampling_rate, wav)

    return wav