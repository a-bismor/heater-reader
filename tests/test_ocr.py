from heater_reader.ocr import parse_reading


def test_parse_reading_extracts_temps_and_mode():
    text = "C.O. 45/55 C.W.U. 42/50 PRACA"
    reading = parse_reading(text)

    assert reading.boiler_current == 45
    assert reading.boiler_set == 55
    assert reading.radiator_current == 42
    assert reading.radiator_set == 50
    assert reading.mode == "PRACA"
