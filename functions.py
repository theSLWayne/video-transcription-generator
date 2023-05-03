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


def create_labelling(labels, wav_splits):
    """

    Labelling speakers. Identifies what speaker spoke at which time using cluster embeddings

    Args:
        labels: Labels of each speach segment which defines what speaker spoke at that specific segment
        wav_splits: Splits taken from voice encoder model

    Returns:
        Labels of speaker, start time(s), end time(s) of each segment
    """

    times = [((s.start + s.stop) / 2) / sampling_rate for s in wav_splits]
    labelling = []
    start_time = 0

    for i, time in enumerate(times):
        if i > 0 and labels[i] != labels[i - 1]:
            temp = [str(labels[i - 1]), start_time, time]
            labelling.append(tuple(temp))
            start_time = time
        if i == len(times) - 1:
            temp = [str(labels[i]), start_time, time]
            labelling.append(tuple(temp))

    return labelling


def speaker_clustering(audio):
    """

    Clustering speakers to identify which speaker spoke at specific times in the audio clip
    """

    # Instantiate the VoiceEncoder model and take predictions for embeddings
    encoder = VoiceEncoder("cpu")
    _, cont_embeds, wav_splits = encoder.embed_utterance(
        audio, return_partials=True, rate=16
    )

    # Cluster similar embeddings together using SpectralClusterer
    clusterer = SpectralClusterer(min_clusters=2, max_clusters=100)

    # Generate labels
    labels = clusterer.predict(cont_embeds)

    # Map speaker labels with clip start and end times
    labelling = create_labelling(labels, wav_splits)

    return labelling


def generate_transcript_from_audio(path: str, remove_audio_file: bool = False) -> list:
    """

    Generator function - this will be the access point

    Args:
        path: Path of the audio file. Must be a valid path.
        remove_audio_file: Whether to delete the audio file
                mentioned by 'path' after transcript generation

    Returns:
        Transcripts as a list of strings
    """

    # Preprocess audio
    audio = preprocess(audio_file_path=path)

    # Speaker cluster details
    speaker_clusters = speaker_clustering(audio)

    print(
        f"{len(speaker_clusters)} different speech segments by {len(list(set([i[0] for i in speaker_clusters])))} speakers were detected."
    )

    transcriptions = []

    # Generate transcriptions for each speech segment
    for speaker, st, et in speaker_clusters:
        # Extract sublcip from complete audio file
        ffmpeg_extract_subclip(TMP_AUDIO_PATH, st, et, targetname="segment.wav")

        # Read the audio segment
        rate, segment_audio = read("segment.wav")

        # Instantiate speech-to-text model
        model = Speech2TextForConditionalGeneration.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        )

        # Instantiate speech-to-text preprocessor
        processor = Speech2TextProcessor.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        )

        # Preprocess audio for the model
        inputs = processor(segment_audio, sampling_rate=rate, return_tensors="pt")
        generated_ids = model.generate(
            inputs["input_features"], attention_mask=inputs["attention_mask"]
        )

        # Take predictions from speech-to-text model
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)

        transcriptions.append(f"Speaker {speaker}: {transcription[0]}\n")

    # Write transcripts to file
    with open("transcript.txt", "w") as f:
        f.writelines(transcriptions)

    print("Generated Transcript was successfully saved at 'transcript.txt'.")

    # Delete created temporary files
    os.remove(TMP_AUDIO_PATH)
    os.remove("segment.wav")
    if remove_audio_file:
        os.remove(path)

    return transcriptions
