from .models import SLVSHMatch, Trick
from .loader import load_slvsh_matches
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def decompose(text: str) -> list[str]:
    text = text.removesuffix('.').removesuffix(',')
    return [t.strip() for t in text.split('.')]

def aggregate(
    slvsh_match: SLVSHMatch,
) -> list[Trick]:
    logger.info(f"Aggregating tricks for {slvsh_match.title}")

    if slvsh_match.texts is None:
        return []

    tricks = []
    texts = slvsh_match.texts
    i = 0
    while i < len(texts):
        text = texts[i]
        if text.text:
            i_start = i
            start = text.timestamp
            while i < len(texts) and texts[i].text:
                i += 1
            i_end = i
            end = texts[i_end - 1].timestamp

            candidates = texts[i_start:i_end]
            # Take a majority of candidates
            if len(candidates) > 0:
                # Count occurrences of each text while preserving order
                text_counts = {}
                for c in candidates:
                    text_counts[c.text] = text_counts.get(c.text, 0) + 1
                
                # Find max count
                max_count = max(text_counts.values())
                
                # Get first text with max count
                majority = next(text for text, count in text_counts.items() if count == max_count)
                if majority != "WINNER":
                    tricks.append(Trick(
                        components=decompose(majority),
                        start=start,
                        end=end,
                        source=slvsh_match
                    ))
        i += 1

    # Filter out tricks that are too short (< 3 seconds)
    tricks = [t for t in tricks if t.end - t.start > 3.0]

    # Merge tricks that are too close to each other
    merged_tricks = []
    for i, trick in enumerate(tricks):
        if i == 0:
            merged_tricks.append(trick)
            continue
        
        prev_trick = merged_tricks[-1]
        time_diff = trick.start - prev_trick.end

        similarity = SequenceMatcher(None, '.'.join(prev_trick.components), '.'.join(trick.components)).ratio()
        
        if time_diff < 2 and similarity > 0.9:
            # Merge the tricks
            merged_tricks[-1] = Trick(
                components=prev_trick.components,
                start=prev_trick.start,
                end=trick.end,
                source=prev_trick.source
            )
        else:
            merged_tricks.append(trick)

    tricks = merged_tricks

    return tricks


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    m = load_slvsh_matches(k=1)[0]
    tricks = aggregate(m)
    print("--------------------- result ---------------------")
    for trick in tricks:
        print(f"{trick.start:0.1f} - {trick.end:0.1f}: {trick.components}")
