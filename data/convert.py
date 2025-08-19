# convert_tsv_to_json.py
import json

with open("D:/Github/repertoire/Tibetan/20542-22238.txt", "r", encoding="utf-8") as f:
    lines = [line.strip().split("\t") for line in f if line.strip()]
    mapping_data = []
    for line in lines:
        if len(line) >= 4:
            entry = {
                "index": int(line[0]),
                "pua": line[1],
                "cp": int(line[2], 16),
                "sequence": line[3],
                "tran": line[4] if len(line) > 4 else "",
            }
            mapping_data.append(entry)

with open("mapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping_data, f, ensure_ascii=False, indent=2)
