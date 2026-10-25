"""
Audio processing functions:
Loading Audio Data 
Cleaning and prepping for extraction
"""
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
# Global paramater
req_sampling_rate = 16000

# error message
class AudioProcessingError(ValueError):
    """Raised when an audio file cannot enter the feature pipeline."""


# Audio Loading
def load_audio(filepath: str | Path) -> tuple[int, np.ndarray]:
    path = Path(filepath)

    if not path.is_file():
        raise AudioProcessingError(f"audio file does not exist: {path}")

    if path.suffix.lower() != ".wav":
        raise AudioProcessingError(f"expected a WAV file: {path}")

    try:
        sample_rate, audio = wavfile.read(path)
    except (OSError, ValueError) as error:
        raise AudioProcessingError(
            f"could not read WAV file: {path}"
        ) from error

    return sample_rate, audio

# Audio Check Functions
"""
Audio is received by files, not captured.
Functions will check those audio files for program eligibility
"""

def convert_to_mono(audio: np.ndarray) -> np.ndarray:
    """Converting to mono channel to achieve standardize test"""
    audio = np.asarray(audio)

    if audio.ndim == 1:
        # Already mono
        return audio

    if audio.ndim == 2:
        # Average all channels for each sample
        return np.mean(audio, axis=1)

    raise AudioProcessingError(
        f"expected mono or multi-channel audio, got shape {audio.shape}"
    )

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Using floating Point of 64 bit for standardize test"""
    audio = np.asarray(audio)

    if audio.size == 0:
        raise AudioProcessingError("audio must not be empty")

    if not np.issubdtype(audio.dtype, np.number):
        raise AudioProcessingError(
            f"audio must contain numeric samples, got {audio.dtype}"
        )

    if not np.all(np.isfinite(audio)):
        raise AudioProcessingError(
            "audio contains NaN or infinite values"
        )

    if np.issubdtype(audio.dtype, np.unsignedinteger):
        info = np.iinfo(audio.dtype)
        audio = audio.astype(np.float64)
        audio = (audio - info.max / 2) / (info.max / 2)

    elif np.issubdtype(audio.dtype, np.signedinteger):
        info = np.iinfo(audio.dtype)
        scale = max(abs(info.min), info.max)
        audio = audio.astype(np.float64) / scale

    elif np.issubdtype(audio.dtype, np.floating):
        audio = audio.astype(np.float64)

    else:
        raise AudioProcessingError(
            f"unsupported audio dtype: {audio.dtype}"
        )

    if not np.all(np.isfinite(audio)):
        raise AudioProcessingError(
            "normalized audio contains NaN or infinite values"
        )

    return audio

def resample_audio(
    audio: np.ndarray,
    original_sample_rate: int,
    target_sample_rate: int = req_sampling_rate,
) -> tuple[np.ndarray, int]:
    """resample to 16k bit for standardize test"""
    audio = np.asarray(audio)

    if audio.ndim != 1:
        raise AudioProcessingError(
            "resample_audio expects one-dimensional mono audio"
        )

    if audio.size == 0:
        raise AudioProcessingError("audio must not be empty")

    if original_sample_rate <= 0:
        raise AudioProcessingError(
            "original sample rate must be positive"
        )

    if target_sample_rate <= 0:
        raise AudioProcessingError(
            "target sample rate must be positive"
        )

    if original_sample_rate == target_sample_rate:
        return audio.copy(), target_sample_rate

    common_factor = np.gcd(
        original_sample_rate,
        target_sample_rate,
    )

    up = target_sample_rate // common_factor
    down = original_sample_rate // common_factor

    resampled_audio = resample_poly(audio, up, down)

    return resampled_audio.astype(np.float64), target_sample_rate

def remove_silence(
    audio: np.ndarray,
    sample_rate: int,
    threshold: float = 0.01,
    frame_duration_seconds: float = 0.025,
    hop_duration_seconds: float = 0.010,
) -> np.ndarray:
    """Trim low-energy frames from the beginning and end of mono audio."""

    audio = np.asarray(audio)

    if audio.ndim != 1:
        raise AudioProcessingError(
            "remove_silence expects one-dimensional mono audio"
        )

    if audio.size == 0:
        raise AudioProcessingError("audio must not be empty")

    if sample_rate <= 0:
        raise AudioProcessingError(
            "sample rate must be positive"
        )

    if threshold < 0:
        raise AudioProcessingError(
            "silence threshold must not be negative"
        )

    if frame_duration_seconds <= 0:
        raise AudioProcessingError(
            "frame duration must be positive"
        )

    if hop_duration_seconds <= 0:
        raise AudioProcessingError(
            "hop duration must be positive"
        )

    if not np.issubdtype(audio.dtype, np.number):
        raise AudioProcessingError(
            f"audio must contain numeric samples, got {audio.dtype}"
        )

    if not np.all(np.isfinite(audio)):
        raise AudioProcessingError(
            "audio contains NaN or infinite values"
        )

    frame_length = max(
        1,
        round(frame_duration_seconds * sample_rate),
    )
    hop_length = max(
        1,
        round(hop_duration_seconds * sample_rate),
    )

    active_starts: list[int] = []
    active_ends: list[int] = []

    for start in range(0, audio.size, hop_length):
        end = min(start + frame_length, audio.size)
        frame = audio[start:end]

        if frame.size == 0:
            continue

        rms = np.sqrt(np.mean(np.square(frame)))

        if rms > threshold:
            active_starts.append(start)
            active_ends.append(end)

    if not active_starts:
        raise AudioProcessingError(
            "audio contains no frames above the silence threshold"
        )

    first_active_sample = active_starts[0]
    last_active_sample = active_ends[-1]

    trimmed_audio = audio[first_active_sample:last_active_sample]

    if trimmed_audio.size == 0:
        raise AudioProcessingError(
            "silence removal produced empty audio"
        )

    return trimmed_audio.copy()

def validate_audio(
    audio: np.ndarray,
    sample_rate: int,
    expected_sample_rate: int = req_sampling_rate,
    minimum_duration_seconds: float = 0.1,
) -> None:
    """Validate audio after loading and preprocessing."""

    audio = np.asarray(audio)

    if audio.ndim != 1:
        raise AudioProcessingError(
            f"audio must be mono and one-dimensional, got shape {audio.shape}"
        )

    if audio.size == 0:
        raise AudioProcessingError("audio must not be empty")

    if not np.issubdtype(audio.dtype, np.number):
        raise AudioProcessingError(
            f"audio must contain numeric samples, got {audio.dtype}"
        )

    if not np.all(np.isfinite(audio)):
        raise AudioProcessingError(
            "audio contains NaN or infinite values"
        )

    if sample_rate <= 0:
        raise AudioProcessingError(
            f"sample rate must be positive, got {sample_rate}"
        )

    if expected_sample_rate <= 0:
        raise AudioProcessingError(
            "expected sample rate must be positive"
        )

    if sample_rate != expected_sample_rate:
        raise AudioProcessingError(
            f"expected {expected_sample_rate} Hz, got {sample_rate} Hz"
        )

    if minimum_duration_seconds <= 0:
        raise AudioProcessingError(
            "minimum duration must be positive"
        )

    duration_seconds = audio.size / sample_rate

    if duration_seconds < minimum_duration_seconds:
        raise AudioProcessingError(
            f"audio is too short: {duration_seconds:.3f} seconds; "
            f"minimum is {minimum_duration_seconds:.3f} seconds"
        )


# Audio Preperation
def prepare_audio(
    audiofile: str | Path,
    expected_sample_rate: int = req_sampling_rate,
    apply_silence_removal: bool = False,
) -> tuple[np.ndarray, int]:
    """Prepare audio for feature extraction."""
    sample_rate, audio = load_audio(audiofile)

    audio = normalize_audio(audio)
    audio = convert_to_mono(audio)

    audio, sample_rate = resample_audio(
        audio,
        original_sample_rate=sample_rate,
        target_sample_rate=expected_sample_rate,
    )

    validate_audio(
        audio,
        sample_rate,
        expected_sample_rate=expected_sample_rate,
    )

    if apply_silence_removal:
        audio = remove_silence(audio, sample_rate)
        validate_audio(
            audio,
            sample_rate,
            expected_sample_rate=expected_sample_rate,
        )

    return audio, sample_rate



    