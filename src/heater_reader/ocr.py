from dataclasses import dataclass
import re


@dataclass
class ReadingText:
    boiler_current: int | None
    boiler_set: int | None
    radiator_current: int | None
    radiator_set: int | None
    mode: str


_TEMP_PAIR = re.compile(r"(\d{1,3})\s*/\s*(\d{1,3})")


def parse_reading(text: str) -> ReadingText:
    pairs = _TEMP_PAIR.findall(text)
    boiler_current = boiler_set = radiator_current = radiator_set = None
    if len(pairs) >= 2:
        boiler_current, boiler_set = map(int, pairs[0])
        radiator_current, radiator_set = map(int, pairs[1])

    mode = "UNKNOWN"
    if "PRACA" in text:
        mode = "PRACA"
    elif "PODTRZYMANIE" in text:
        mode = "PODTRZYMANIE"

    return ReadingText(
        boiler_current=boiler_current,
        boiler_set=boiler_set,
        radiator_current=radiator_current,
        radiator_set=radiator_set,
        mode=mode,
    )
