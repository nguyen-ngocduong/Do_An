"""Tạo diễn giải tiếng Việt từ bằng chứng SHAP đã được kiểm tra."""

import json
import time
import threading

import jsonschema
from google import genai
from google.genai import errors, types

from BE.config import MODEL_ID
from BE.gemini_validation import DIRECTION_VI, summarize_evidence, validate_evidence, validate_text
from BE.utils import json_hash, read_json, write_json


def build_llm_input(item, check_guide):
    features = []
    for feature in item["top_features"]:
        features.append({
            "thu_hang": feature["rank"], "ten_dac_trung": feature["feature"],
            "gia_tri_goc": feature["value"], "gia_tri_thieu": feature["missing"],
            "shap_don_vi_xac_suat": feature["shap_value"],
            "tac_dong_diem_phan_tram": feature["impact_percentage_points"],
            "huong_tac_dong": DIRECTION_VI[feature["direction"]],
        })
    return {
        "ma_mau": item["case_id"], "model_phat_hien": MODEL_ID,
        "lop_du_doan": item["predicted_class"], "xac_suat_cac_lop": item["probabilities"],
        "lop_duoc_giai_thich": item["explained_class"],
        "xac_suat_du_doan": item["predicted_probability"],
        "xac_suat_nen_tham_chieu": item["base_probability"],
        "tong_shap_tat_ca_dac_trung": item["shap_sum"],
        "tong_shap_ngoai_top_5": item["other_features_shap_sum"],
        "don_vi_dau_ra": "Xác suất; SHAP nhân 100 là điểm phần trăm.",
        "top_5_dac_trung": features,
        "bang_chung_tong_hop": summarize_evidence(item),
        "huong_dan_kiem_tra_tham_khao": check_guide[item["predicted_class"]],
    }


class GeminiService:
    def __init__(self, runtime, settings, client=None):
        self.settings = settings
        self.config = runtime.generation_config
        self.schema = self.config["response_json_schema"]
        self.check_guide = runtime.check_guide
        self.client = client
        self.shutdown_event = threading.Event()
        if self.client is None and settings.gemini_api_key:
            self.client = genai.Client(
                api_key=settings.gemini_api_key,
                http_options=types.HttpOptions(
                    timeout=60000, retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )

    def close(self):
        if self.client is not None:
            self.client.close()

    def call(self, case_dir, attempt, prompt):
        request = {"model": self.settings.gemini_model, "contents": prompt, "config": self.config}
        request_hash = json_hash(request)
        response_path = case_dir / f"gemini_response_{attempt:02d}.json"
        if response_path.is_file():
            saved = read_json(response_path)
            if saved["request_sha256"] != request_hash:
                raise ValueError("Cache Gemini khác yêu cầu; cần chạy lại có chủ đích.")
            return saved
        write_json(case_dir / f"gemini_request_{attempt:02d}.json", request)
        saved = {
            "request_sha256": request_hash, "requested_model": self.settings.gemini_model,
            "attempt": attempt,
        }
        started = time.perf_counter()
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model, contents=prompt, config=self.config,
            )
            saved["response"] = response.model_dump(mode="json", exclude_none=True)
            saved["text"] = response.text or ""
            saved["api_status"] = "received"
        except errors.APIError as error:
            saved["api_status"] = "api_error"
            saved["http_code"] = error.code
        except Exception as error:
            # Không ghi exception message có thể chứa URL hoặc thông tin xác thực.
            saved["api_status"] = "request_error"
            saved["error_type"] = type(error).__name__
        saved["api_seconds"] = time.perf_counter() - started
        write_json(response_path, saved)
        self.shutdown_event.wait(self.settings.gemini_pause_seconds)
        return saved

    def explain(self, item, case_dir, enabled=True, audience_level="technical"):
        if audience_level not in ["basic", "technical"]:
            raise ValueError("Mức diễn giải phải là basic hoặc technical.")
        llm_input = build_llm_input(item, self.check_guide)
        write_json(case_dir / "llm_input.json", llm_input)
        prompt = (
            "Viết báo cáo tiếng Việt ĐẦY ĐỦ DẤU, đúng chính tả cho mẫu dưới đây. "
            "Tổng hợp yếu tố hỗ trợ/phản đối trong top 5 và so sánh hai lớp đứng đầu. "
            "Phân biệt vai trò năm đặc trưng, tránh lặp câu. Không có nhãn thật trong đầu vào. "
            "Chỉ trả JSON theo schema và rà soát dấu tiếng Việt trước khi trả lời.\n\n"
            "DỮ LIỆU DỰ ĐOÁN VÀ SHAP:\n" + json.dumps(llm_input, ensure_ascii=False, indent=2)
        )
        # Giữ nguyên prompt kỹ thuật để tái sử dụng các cache đã có.
        if audience_level == "basic":
            prompt = (
                "MỨC DIỄN GIẢI: DỄ HIỂU. Viết cho người chưa chuyên về an toàn thông tin. "
                "Ưu tiên câu ngắn, từ phổ thông; giải nghĩa thuật ngữ khi cần. "
                "Giữ đủ các mục của schema, tên lớp/đặc trưng và hướng SHAP. "
                "Không bỏ bằng chứng hoặc biến dự đoán thành kết luận tấn công đã xác minh.\n\n"
                + prompt
            )
        (case_dir / "user_prompt.txt").write_text(prompt, encoding="utf-8")
        original_prompt = prompt
        record = {
            "status": "gemini_disabled", "message": "Đã tắt Gemini cho yêu cầu này.",
            "result": None, "selected_attempt": None, "attempts_saved": 0,
            "api_seconds": 0.0, "total_tokens": 0, "human_semantic_review": "deferred",
            "audience_level": audience_level,
        }
        if enabled and self.client is None:
            record.update(status="not_configured", message="Chưa cấu hình GEMINI_API_KEY; dự đoán và SHAP vẫn được lưu.")
        if enabled and self.client is not None:
            for attempt in [1, 2]:
                if self.shutdown_event.is_set():
                    record.update(status="interrupted", message="Server đang dừng; chưa tự gọi tiếp Gemini.")
                    break
                saved = self.call(case_dir, attempt, prompt)
                record["attempts_saved"] = attempt
                record["api_seconds"] += saved["api_seconds"]
                tokens = saved.get("response", {}).get("usage_metadata", {}).get("total_token_count")
                if tokens is not None and record["total_tokens"] is not None:
                    record["total_tokens"] += tokens
                else:
                    record["total_tokens"] = None
                if saved["api_status"] != "received":
                    record.update(status=saved["api_status"], message="Gemini lỗi API/kết nối; không tự thử lại lỗi API.")
                    break
                try:
                    candidates = saved["response"].get("candidates", [])
                    if not candidates or candidates[0].get("finish_reason") != "STOP":
                        raise ValueError("Phản hồi chưa kết thúc bình thường.")
                    result = json.loads(saved["text"])
                    jsonschema.validate(result, self.schema)
                    validate_evidence(result, item, self.schema, self.check_guide)
                except (ValueError, KeyError, TypeError, jsonschema.ValidationError) as error:
                    record.update(status="invalid_evidence", message=f"Diễn giải không đạt kiểm tra bằng chứng ({type(error).__name__}).")
                    break
                record["result"] = result
                record["selected_attempt"] = attempt
                try:
                    validate_text(result, item, self.check_guide)
                    record.update(status="accepted", message="Đạt kiểm tra tự động; đánh giá ngữ nghĩa thủ công đang tạm hoãn.")
                    break
                except (ValueError, KeyError, TypeError) as error:
                    record.update(status="needs_text_review", message=f"Cần sửa văn bản: {error}")
                    if attempt == 2:
                        break
                    prompt = (
                        original_prompt + "\n\nPHẢN HỒI CẦN SỬA TIẾNG VIỆT:\n"
                        + json.dumps(result, ensure_ascii=False, indent=2)
                        + "\nLÝ DO CẦN SỬA: " + str(error)
                        + "\nChỉ sửa các đoạn văn và tên nguồn nhật ký thành tiếng Việt đầy đủ dấu. "
                        "Giữ nguyên lớp, cờ so sánh, tên yếu tố mạnh nhất, thứ tự đặc trưng và hướng SHAP. "
                        "Trả lại toàn bộ JSON đúng schema."
                    )
        if record["result"] is not None and record["status"] != "accepted":
            record["status"] = "needs_text_review"
            record["message"] = "Giữ bản nháp hợp lệ về bằng chứng. " + record["message"]
        for name in ["explanation_vi.json", "explanation_vi_draft.json"]:
            (case_dir / name).unlink(missing_ok=True)
        if record["result"] is not None:
            name = "explanation_vi.json" if record["status"] == "accepted" else "explanation_vi_draft.json"
            write_json(case_dir / name, record["result"])
        write_json(case_dir / "gemini_status.json", {key: value for key, value in record.items() if key != "result"})
        return record
