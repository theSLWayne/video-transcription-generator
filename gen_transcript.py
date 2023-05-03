from functions import generate_transcript_from_audio
import argparse

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
    
