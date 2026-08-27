import configparser
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True, help="Gammu backup file.")
    parser.add_argument(
        "--contacts", type=Path, required=True, help="Your CSV file with contacts."
    )
    args = parser.parse_args()

    # Читаем резервную копию от Gammu как INI-файл.
    with open(args.backup, "r", encoding="utf-16") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    # Удаляем старые контакты.
    num_of_entries = len(config.sections()) - 2
    for i in range(1, num_of_entries + 1):
        config.remove_section(f"SIMPBK{i:03}")

    # Меняем дату на текущую и удаляем контрольную сумму.
    config["Backup"]["datetime"] = datetime.now().strftime("%Y%m%dT%H%M%S")
    config.remove_section("Checksum")

    # Записываем новые контакты в объект ConfigParser...
    with open(args.contacts, "r", encoding="utf-8") as f:
        for i, line in enumerate(f.readlines(), start=1):
            name, phone = map(str.strip, line.split(","))
            section = f"SIMPBK{i:03}"
            # ... в формате, пригодном для Gammu.
            config.add_section(section)
            config[section]["location"] = f"{i:03}"
            config[section]["entry00type"] = "NumberGeneral"
            config[section]["entry00text"] = f'"{phone}"'
            config[section]["entry01type"] = "Name"
            config[section]["entry01text"] = f'"{name}"'

    # Сохраняем объект ConfigParser в файл.
    with open(BASE_DIR / "new_contacts.txt", "w", encoding="utf-16") as f:
        config.write(f)


if __name__ == "__main__":
    main()
