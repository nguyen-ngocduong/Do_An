"""Dựng số liệu bằng Python, giữ diễn giải Gemini thành phần riêng."""

from BE.gemini_validation import summarize_evidence
from BE.playbooks import get_playbook
from BE.utils import write_json


def write_report(item, gemini_record, case_dir):
    evidence = summarize_evidence(item)
    lines = [
        f"# Giải thích dòng CSV {item['input_row_index']}", "",
        f"Trạng thái Gemini: **{gemini_record['status']}**. {gemini_record['message']}", "",
        "Mức diễn giải: **" + ("Dễ hiểu" if gemini_record.get("audience_level") == "basic" else "Kỹ thuật") + "**.", "",
        "## Dự đoán và số liệu do chương trình dựng", "",
        f"- Model: `{item['model_id']}`.",
        f"- Lớp dự đoán: **{item['predicted_class']}**; xác suất đầu ra: **{100 * item['predicted_probability']:.4f}%**.",
        f"- Lớp đứng thứ hai: **{evidence['lop_thu_hai']}**; xác suất: **{100 * evidence['xac_suat_lop_thu_hai']:.4f}%**.",
        f"- Chênh lệch hai đầu ra: **{evidence['chenh_lech_diem_phan_tram']:.4f} điểm phần trăm**.",
        f"- Xác suất nền SHAP: {100 * item['base_probability']:.6f}%.",
        f"- Tổng SHAP: {100 * item['shap_sum']:+.6f} điểm phần trăm.",
        f"- Phần ngoài top 5: {100 * item['other_features_shap_sum']:+.6f} điểm phần trăm.", "",
        "| Đặc trưng | Giá trị gốc | SHAP | Tác động (điểm %) |",
        "|---|---:|---:|---:|",
    ]
    for feature in item["top_features"]:
        value = "Thiếu" if feature["missing"] else f"{feature['value']:.8g}"
        lines.append(
            f"| {feature['feature']} | {value} | {feature['shap_value']:+.8f} | {feature['impact_percentage_points']:+.6f} |"
        )
    lines.extend(["", "![Biểu đồ SHAP](waterfall.png)", "", "## Diễn giải Gemini", ""])
    result = gemini_record.get("result")
    if result is None:
        lines.append("Chưa có diễn giải Gemini được phép hiển thị; xem trạng thái ở đầu báo cáo.")
    else:
        if gemini_record["status"] != "accepted":
            lines.extend(["**BẢN NHÁP CẦN SỬA — chưa đạt kiểm tra văn bản.**", ""])
        lines.extend([
            result["tom_tat"], "", result["so_sanh_hai_lop"]["dien_giai"], "",
            result["tong_hop_shap"]["dien_giai"], "",
        ])
        for feature in result["giai_thich_dac_trung"]:
            lines.append(f"- **{feature['ten_dac_trung']}**: {feature['dien_giai']}")
        lines.extend(["", "## Gợi ý kiểm tra có điều kiện", ""])
        for suggestion in result["de_xuat_kiem_tra"]:
            lines.append(
                f"- **{suggestion['nguon_du_lieu']}**: {suggestion['noi_dung_can_kiem_tra']} "
                f"Mục đích: {suggestion['muc_dich']}"
            )
        lines.extend(["", "## Giới hạn", ""])
        for text in result["gioi_han"]:
            lines.append(f"- {text}")
    playbook = get_playbook(item["predicted_class"])
    write_json(case_dir / "playbook.json", playbook)
    lines.extend(["", "## Hướng dẫn tham khảo do chương trình tra theo lớp", "", playbook["scope_note"], ""])
    lines.extend(f"- {text}" for text in playbook["checks"])
    lines.extend(["", "Các bước xử lý cần người vận hành quyết định:", ""])
    lines.extend(f"- {text}" for text in playbook["response_steps"])
    lines.extend(["", f"Phiên bản hướng dẫn: {playbook['version']}. Nguồn tham khảo:", ""])
    for source in playbook["sources"]:
        lines.append(f"- [{source['title']}]({source['url']})")
    lines.extend([
        "", "SHAP giải thích đầu ra model, chưa chứng minh tấn công thực tế hoặc quan hệ nhân quả.",
        "Validation/test nguồn đã từng được xem; đánh giá thủ công được lưu riêng với báo cáo này.", "",
    ])
    path = case_dir / "report_vi.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
