from functions import generate_transcript_from_audio
import argparse
import os

def init_args():
    """
    
    Initialize arguments

    Args:
        None

    Returns:
        Parsed arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-vp', '--video_path', type=str,
                        help='Path to video file that should be transcripted',
                        required=False)
    parser.add_argument('-ap', '--audio_path', type=str,
                        help='Path to audio file that should be transcripted',
                        required=False)
    parser.add_argument('-sa', '--save_audio', type=strToBool,
                        help="Whether to save the extracted audio file or not (y/n)")
    
def strToBool(value: str) -> bool:
    """
    
    Convert argument string to boolean

    Args:
        String value

    Returns:
        String value as a boolean value

    Raises:
        argparse.ArgumentTypeError when unsupported values are encountered
    """

    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(
            "Unsupported value found for --save_audio"
        )
    
def validate_args(args):
    """
    
    Validate arguments

    Args:
        args: Arguments

    Returns:
        None
    """

    # Check for either a video file path or an audio file path
    assert (args.video_path or args.audio_path), "Need to provide a value for either --video_path or --audio_path"

    if args.video_path:
        # Check for validity of the video path
        assert os.path.exists(args.video_path), "Provided video path does not exist."
        # Make sure the file is a "MP4" file
        assert os.path.basename(args.video_path).split('.')[-1] == "mp4", "The path is not an accepted video file."

    if args.audio_path:
        # check the validity of the audio path
        assert os.path.exists(args.audio_path), "Provided audio_path does not exist."
        # Make sure the file is a "WAV" file
        assert os.path.basename(args.audio_path).split('.')[-1] == "wav", "The path is not an accepted audio file."

