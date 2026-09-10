import subprocess


def convert_webm_to_wav(
    webm_path: str,
    wav_path: str
):
    """
    Convert WEBM audio file to WAV using FFmpeg.
    Raises exception if conversion fails.
    """

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            webm_path,
            wav_path
        ],
        check=True,
        capture_output=True,
        text=True
    )

    return wav_path