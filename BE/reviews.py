"""Đánh giá do con người nhập; tách khỏi nhãn dự đoán và trạng thái cảnh báo."""

from fastapi import HTTPException

from BE.exports import case_file
from BE.utils import json_hash, sha256_file, utc_now


def review_context(manager, run_id, row_index, audience_level):
    prediction = manager.store.prediction(run_id, row_index)
    if prediction is None:
        raise HTTPException(404, "Dòng chưa có kết quả dự đoán để đánh giá.")
    state = manager.store.explanation(run_id, row_index, audience_level)
    if state and state["status"] in ["queued", "shap_running", "gemini_running"]:
        raise HTTPException(409, "Mẫu đang được giải thích. Chờ ghi xong kết quả trước khi đánh giá.")
    files = {}
    for name in ["explanation.json", "report_vi.md", "top5_features.csv", "waterfall.png", "explanation_vi.json", "explanation_vi_draft.json"]:
        path = case_file(manager, run_id, row_index, name, audience_level)
        if path.is_file():
            files[name] = sha256_file(path)
    context = {
        "run_id": run_id, "row_index": row_index, "audience_level": audience_level,
        "predicted_class": prediction["predicted_class"],
        "predicted_probability": prediction["predicted_probability"],
        "file_sha256": files,
    }
    context["evidence_signature"] = json_hash(context)
    return context


def read_review(manager, run_id, row_index, audience_level):
    context = review_context(manager, run_id, row_index, audience_level)
    review = manager.store.human_review(run_id, row_index, audience_level)
    return {
        "context": context, "review": review,
        "stale": bool(review and review["evidence_signature"] != context["evidence_signature"]),
    }


def save_review(manager, run_id, row_index, audience_level, body, username):
    context = review_context(manager, run_id, row_index, audience_level)
    if body.evidence_signature != context["evidence_signature"]:
        raise HTTPException(409, "Bằng chứng đã thay đổi. Tải lại bản đánh giá trước khi lưu.")
    if body.proposed_label is not None and body.prediction_assessment != "disagree":
        raise HTTPException(422, "Chỉ đề xuất nhãn khác khi không đồng ý với dự đoán.")
    if body.proposed_label == context["predicted_class"]:
        raise HTTPException(422, "Nhãn đề xuất cần khác nhãn dự đoán khi không đồng ý.")
    review = {
        **body.model_dump(), "context": context,
        "reviewer_username": username, "updated_at": utc_now(),
        "scope_note": "Đánh giá do người dùng nhập; tư cách chuyên gia chưa được xác minh. Không thay thế nhãn model hoặc chứng minh sự kiện tấn công thực tế.",
    }
    manager.store.save_human_review(run_id, row_index, audience_level, review)
    return {"context": context, "review": review, "stale": False}
