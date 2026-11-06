"""Định dạng sự kiện dòng CSV; giữ nguyên chuỗi số để không làm tròn dữ liệu."""

import csv
import hashlib
import io
import json
from pathlib import Path
import re


MAX_ROWS = 1000
MAX_BYTES = 10 * 1024 * 1024


def read_csv_events(path, feature_names):
    content = path.read_bytes()
    if not content or len(content) > MAX_BYTES:
        raise ValueError("CSV trống hoặc vượt 10 MiB.")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)) or set(headers) - {"label"} != set(feature_names):
        raise ValueError("CSV phải có đủ tên đặc trưng, không trùng cột; label là tùy chọn.")
    rows = list(reader)
    if not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("CSV phải có từ 1 đến 1.000 dòng.")
    digest = hashlib.sha256(content).hexdigest()
    events = []
    for index, row in enumerate(rows):
        if None in row or any(row.get(name) is None for name in feature_names):
            raise ValueError("Dòng CSV không đủ cột hoặc có cột dư.")
        # label không được đưa vào Kafka, model hoặc Gemini.
        events.append({"version": 1, "file_sha256": digest, "filename": path.name,
                       "row_index": index, "row_count": len(rows),
                       "features": {name: row[name] for name in feature_names}})
    return events


def validate_event(event, feature_names):
    if not isinstance(event, dict) or set(event) != {
        "version", "file_sha256", "filename", "row_index", "row_count", "features"
    }:
        raise ValueError("Sự kiện Kafka không đúng schema.")
    if type(event["version"]) is not int or event["version"] != 1:
        raise ValueError("Phiên bản sự kiện không được hỗ trợ.")
    if not isinstance(event["file_sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", event["file_sha256"]):
        raise ValueError("Checksum sự kiện không hợp lệ.")
    name = event["filename"]
    if not isinstance(name, str) or len(name) > 200 or name != Path(name).name or not name.endswith(".csv"):
        raise ValueError("Tên CSV không hợp lệ.")
    count, index = event["row_count"], event["row_index"]
    if type(count) is not int or not 1 <= count <= MAX_ROWS or type(index) is not int or not 0 <= index < count:
        raise ValueError("Chỉ số dòng/số dòng sự kiện không hợp lệ.")
    values = event["features"]
    if not isinstance(values, dict) or set(values) != set(feature_names):
        raise ValueError("Sự kiện thiếu/thừa đặc trưng; label không được dùng làm đầu vào.")
    if any(not isinstance(v, str) or len(v) > 100 for v in values.values()):
        raise ValueError("Giá trị đặc trưng phải là chuỗi số ngắn hoặc ô trống.")
    for value in values.values():
        if value and value.lower() not in ["nan", "na", "null"]:
            try:
                number = float(value)
            except ValueError:
                raise ValueError("Đặc trưng không phải số.") from None
            if number == float("inf") or number == float("-inf"):
                raise ValueError("Đặc trưng không được là vô cực.")
    return event


def encode(event):
    return json.dumps(event, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()
