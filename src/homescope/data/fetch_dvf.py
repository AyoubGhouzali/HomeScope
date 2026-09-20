from pathlib import Path
import requests
import yaml

CONFIG_PATH = Path("configs/sources.yaml")
RAW_DIR = Path("data/raw")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def download_file(url: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    output_path.write_bytes(response.content)


def main():
    config = load_config()["dvf"]

    department = config["department"]
    url_template = config["url_template"]

    for year in config["years"]:
        url = url_template.format(
            year=year,
            department=department,
        )

        output_path = RAW_DIR / f"dvf_{department}_{year}.csv.gz"

        print(f"Downloading: {url}")
        download_file(url, output_path)
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()