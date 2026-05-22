from typing import Optional

def assign_speakers(transcript_segments:list[dict], diarization_segments:list[dict])->list[dict]:
    results=[]
    for t_segment in transcript_segments:
        speaker=_find_dominant_speaker(t_segment["start"], t_segment["end"], diarization_segments)
        results.append({
            "text": t_segment["text"],
            "start": t_segment["start"],
            "end": t_segment["end"],
            "speaker": speaker,
        })

    return results
    
def _find_dominant_speaker(
    t_start: float,
    t_end: float,
    speaker_segments: list[dict],
) -> int:
    """
    Find which speaker has the most overlap with [t_start, t_end].
    Falls back to speaker 0 if no overlap found.
    """
    overlap_by_speaker: dict[int, float] = {}

    for sseg in speaker_segments:
        # Calculate overlap between transcript segment and speaker segment
        overlap_start = max(t_start, sseg["start"])
        overlap_end = min(t_end, sseg["end"])
        overlap = max(0.0, overlap_end - overlap_start)

        if overlap > 0:
            spk = sseg["speaker"]
            overlap_by_speaker[spk] = overlap_by_speaker.get(spk, 0) + overlap

    if not overlap_by_speaker:
        return 0

    # Return speaker with most overlap
    return max(overlap_by_speaker, key=overlap_by_speaker.get)
