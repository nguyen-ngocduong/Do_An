"""Các kiểm tra bằng chứng/tiếng Việt được tách từ notebook integration.

Giữ nguyên quy tắc của run nguồn; kiểm tra này không thay thế human review.
"""

import re
import unicodedata

from BE.config import CLASS_NAMES, MODEL_ID

TOP_FEATURES = 5


def summarize_evidence(item, small_gap_pp=5.0):
    # Các yếu tố nổi bật chỉ xét trong top 5 SHAP của lớp được dự đoán.
    ranked_classes = sorted(item["probabilities"], key=item["probabilities"].get, reverse=True)
    first_class, second_class = ranked_classes[:2]
    gap_pp = 100 * (item["probabilities"][first_class] - item["probabilities"][second_class])
    positive = [feature for feature in item["top_features"] if feature["shap_value"] > 0]
    negative = [feature for feature in item["top_features"] if feature["shap_value"] < 0]
    strongest_positive = max(positive, key=lambda feature: feature["shap_value"]) if positive else None
    strongest_negative = min(negative, key=lambda feature: feature["shap_value"]) if negative else None
    return {
        "lop_thu_hai": second_class,
        "xac_suat_lop_thu_hai": item["probabilities"][second_class],
        "chenh_lech_diem_phan_tram": gap_pp,
        "khoang_cach_nho": gap_pp <= small_gap_pp,
        "xac_suat_dau_chua_vuot_mot_nua": item["predicted_probability"] <= 0.5,
        "ho_tro_manh_nhat": strongest_positive["feature"] if strongest_positive else None,
        "phan_doi_manh_nhat": strongest_negative["feature"] if strongest_negative else None,
        "pham_vi_shap": "Chỉ top 5 của lớp dự đoán; không phải SHAP của lớp đứng thứ hai.",
        "quy_tac_khoang_cach": f"Khoảng cách không quá {small_gap_pp} điểm phần trăm chỉ là quy tắc trình bày, không phải ngưỡng phát hiện hay hiệu chỉnh xác suất.",
    }

def validate_vietnamese(text, item, field, min_accented_word_ratio=0.25):
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Thiếu văn bản ở {field}.")
    # Bỏ tên kỹ thuật trước khi đếm từ có dấu; đây chỉ là quy tắc sàng lọc.
    normalized = unicodedata.normalize("NFC", text).casefold()
    excluded_names = [MODEL_ID] + CLASS_NAMES + [feature["feature"] for feature in item["top_features"]]
    for name in sorted(excluded_names, key=len, reverse=True):
        normalized = re.sub(r"(?<!\w)" + re.escape(name.casefold()) + r"(?!\w)", " ", normalized)
    words = re.findall(r"[^\W\d_]+", normalized, flags=re.UNICODE)
    if len(words) < 6:
        raise ValueError(f"{field}: diễn giải quá ngắn, chưa đủ thông tin.")
    accented_count = 0
    for word in words:
        decomposed = unicodedata.normalize("NFD", word)
        if "đ" in word or any(unicodedata.combining(character) for character in decomposed):
            accented_count += 1
    if accented_count / len(words) < min_accented_word_ratio:
        raise ValueError(f"{field}: tỷ lệ từ có dấu thấp, cần kiểm tra tiếng Việt.")
    # Chuẩn hóa để phát hiện cùng một câu được dùng lại sau khi thay tên cột.
    return " ".join(words)

DIRECTION_VI = {"increase": "tang", "decrease": "giam", "no_change": "khong_doi"}

def normalize_source_name(text):
    # Cho phép nhận diện tên nguồn bị mất dấu để đưa sang lượt sửa văn bản.
    decomposed = unicodedata.normalize("NFD", text.casefold()).replace("đ", "d")
    return " ".join("".join(char for char in decomposed if not unicodedata.combining(char)).split())

def validate_evidence(result, item, schema, check_guide):
    if not isinstance(result, dict) or set(result) != set(schema["required"]):
        raise ValueError("JSON thiếu hoặc thừa trường bắt buộc.")
    if result["lop_du_doan"] != item["predicted_class"]:
        raise ValueError("Gemini đổi lớp dự đoán.")
    evidence = summarize_evidence(item)
    comparison = result["so_sanh_hai_lop"]
    if not isinstance(comparison, dict) or set(comparison) != {"lop_thu_hai", "khoang_cach_nho", "dien_giai"}:
        raise ValueError("Sai cấu trúc so sánh hai lớp.")
    if comparison["lop_thu_hai"] != evidence["lop_thu_hai"]:
        raise ValueError("Gemini đổi lớp đứng thứ hai.")
    if type(comparison["khoang_cach_nho"]) is not bool or comparison["khoang_cach_nho"] != evidence["khoang_cach_nho"]:
        raise ValueError("Gemini đổi cờ khoảng cách nhỏ.")
    summary = result["tong_hop_shap"]
    if not isinstance(summary, dict) or set(summary) != {"ho_tro_manh_nhat", "phan_doi_manh_nhat", "dien_giai"}:
        raise ValueError("Sai cấu trúc tổng hợp SHAP.")
    for key in ["ho_tro_manh_nhat", "phan_doi_manh_nhat"]:
        if summary[key] != evidence[key]:
            raise ValueError(f"Sai yếu tố {key} trong top 5.")
    features = result["giai_thich_dac_trung"]
    if not isinstance(features, list) or len(features) != TOP_FEATURES:
        raise ValueError("Chưa đủ năm đặc trưng.")
    for actual, expected in zip(features, item["top_features"]):
        if not isinstance(actual, dict) or set(actual) != {"ten_dac_trung", "huong_tac_dong", "dien_giai"}:
            raise ValueError("Sai cấu trúc đặc trưng.")
        if actual["ten_dac_trung"] != expected["feature"] or actual["huong_tac_dong"] != DIRECTION_VI[expected["direction"]]:
            raise ValueError("Gemini đổi tên/thứ tự hoặc hướng SHAP.")
    suggestions = result["de_xuat_kiem_tra"]
    if not isinstance(suggestions, list) or len(suggestions) != 2:
        raise ValueError("Cần đúng hai bước kiểm tra.")
    expected_sources = {normalize_source_name(guide["nguon_du_lieu"]) for guide in check_guide[item["predicted_class"]]}
    actual_sources = []
    for suggestion in suggestions:
        if not isinstance(suggestion, dict) or set(suggestion) != {"nguon_du_lieu", "noi_dung_can_kiem_tra", "muc_dich"}:
            raise ValueError("Sai cấu trúc gợi ý kiểm tra.")
        if not isinstance(suggestion["nguon_du_lieu"], str):
            raise ValueError("Tên nguồn kiểm tra phải là văn bản.")
        actual_sources.append(normalize_source_name(suggestion["nguon_du_lieu"]))
    if set(actual_sources) != expected_sources:
        raise ValueError("Nguồn kiểm tra không khớp hướng dẫn đã cung cấp.")
    if not isinstance(result["gioi_han"], list) or not 2 <= len(result["gioi_han"]) <= 3:
        raise ValueError("Cần hai đến ba giới hạn.")
    text_fields = [result["tom_tat"], comparison["dien_giai"], summary["dien_giai"]]
    text_fields.extend(feature["dien_giai"] for feature in features)
    for suggestion in suggestions:
        text_fields.extend([suggestion["noi_dung_can_kiem_tra"], suggestion["muc_dich"]])
    text_fields.extend(result["gioi_han"])
    if not all(isinstance(text, str) for text in text_fields):
        raise ValueError("Các trường diễn giải phải là văn bản trước khi xuất báo cáo.")


def validate_text(result, item, check_guide):
    validate_vietnamese(result["tom_tat"], item, "tom_tat")
    validate_vietnamese(result["so_sanh_hai_lop"]["dien_giai"], item, "so_sanh_hai_lop")
    validate_vietnamese(result["tong_hop_shap"]["dien_giai"], item, "tong_hop_shap")
    normalized_sentences = []
    for feature in result["giai_thich_dac_trung"]:
        normalized_sentences.append(validate_vietnamese(feature["dien_giai"], item, feature["ten_dac_trung"]))
    if len(set(normalized_sentences)) < 3:
        raise ValueError("Năm diễn giải còn lặp, chưa có ba cách viết khác nhau.")
    expected_sources = {guide["nguon_du_lieu"] for guide in check_guide[item["predicted_class"]]}
    for suggestion in result["de_xuat_kiem_tra"]:
        if suggestion["nguon_du_lieu"] not in expected_sources:
            raise ValueError("Tên nguồn nhật ký cần viết đúng tiếng Việt có dấu như hướng dẫn.")
        validate_vietnamese(suggestion["noi_dung_can_kiem_tra"], item, "noi_dung_can_kiem_tra")
        validate_vietnamese(suggestion["muc_dich"], item, "muc_dich")
    for text in result["gioi_han"]:
        validate_vietnamese(text, item, "gioi_han")
