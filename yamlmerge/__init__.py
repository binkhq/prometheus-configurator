from pathlib import Path

import yaml

from yamlmerge.settings import settings


def merge(into: dict, values: dict) -> dict:
    config = into.copy()
    for k, v in values.items():
        if k not in config:
            config[k] = v
        else:
            existing = config[k]
            if isinstance(existing, dict):
                config[k] = merge(existing, v)
            elif isinstance(existing, list):
                config[k].extend(v)
            else:
                config[k] = v
    return config


def main() -> None:
    config = {}
    for file in Path(settings.source_directory).glob("*.yaml"):
        with file.open("r") as f:
            new_config = yaml.load(f, yaml.CLoader)
        config = merge(config, new_config)
    with open(settings.destination_file, "w") as f:
        yaml.dump(config, f, yaml.CDumper)


if __name__ == "__main__":
    main()
