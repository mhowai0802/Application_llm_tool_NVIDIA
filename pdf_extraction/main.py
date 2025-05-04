import config
from extractor import batch_extract
from writer import write_json
from mongo_loader import load_to_mongo


def main():
    list_section = []
    batch = batch_extract(config.REPORTS_DIR, list_section)
    write_json(config.JSON_OUTPUT, batch)
    print(f"Wrote JSON → {config.JSON_OUTPUT}")
    load_to_mongo(batch)

if __name__ == "__main__":
    main()