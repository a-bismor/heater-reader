from heater_reader.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.config == "config.yml"
