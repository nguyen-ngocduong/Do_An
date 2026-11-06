import json
import time
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from BE.artifacts import ModelRuntime
from BE.config import Settings
from BE.main import create_app


@pytest.fixture(scope="session")
def model_runtime(tmp_path_factory):
    settings = Settings(runtime_dir=tmp_path_factory.mktemp("real_model"))
    return ModelRuntime(settings)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        runtime_dir=tmp_path / "runtime", admin_username="tester",
        admin_password="test-password", gemini_pause_seconds=0,
    )


@pytest.fixture
def client(settings, model_runtime):
    with TestClient(create_app(settings, model_runtime)) as http:
        http.auth = ("tester", "test-password")
        yield http


def upload(client, content, mode="batch", interval=0.05):
    response = client.post(
        "/api/runs", files={"file": ("samples.csv", content, "text/csv")},
        data={"mode": mode, "interval_seconds": interval},
    )
    assert response.status_code == 202, response.text
    return response.json()["id"]


def wait_run(client, run_id, status="completed", timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = client.get(f"/api/runs/{run_id}").json()
        if result["status"] == status:
            return result
        assert result["status"] != "failed", result
        time.sleep(0.02)
    raise AssertionError(f"Không nhận được trạng thái {status}: {result}")


def wait_case(client, run_id, row_index, timeout=90, audience_level="technical"):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"/api/runs/{run_id}/explanations/{row_index}", params={"audience_level": audience_level})
        assert response.status_code == 200, response.text
        result = response.json()
        if result["status"] in ["completed", "partial", "failed", "interrupted"]:
            assert result["status"] != "failed", result
            return result
        time.sleep(0.05)
    raise AssertionError(f"Giải thích chưa hoàn thành: {result}")


class FakeResponse:
    def __init__(self, result):
        self.text = json.dumps(result, ensure_ascii=False)

    def model_dump(self, **kwargs):
        return {
            "candidates": [{"finish_reason": "STOP"}],
            "usage_metadata": {"total_token_count": 42},
            "model_version": "gemini-3.5-flash-lite",
        }


class FakeGeminiClient:
    """Phản hồi giả chỉ để kiểm tra API/validator, không đánh giá chất lượng LLM."""

    def __init__(self, behavior="valid"):
        self.behavior = behavior
        self.models = self
        self.calls = []

    def generate_content(self, model, contents, config):
        self.calls.append(contents)
        if self.behavior == "timeout":
            raise TimeoutError("Không được đưa nội dung ngoại lệ nhạy cảm vào output.")
        if self.behavior == "quota":
            from google.genai.errors import ClientError
            raise ClientError(429, {"error": {"message": "Quota", "status": "RESOURCE_EXHAUSTED"}})
        raw = contents.split("DỮ LIỆU DỰ ĐOÁN VÀ SHAP:\n", 1)[1]
        item, _ = json.JSONDecoder().raw_decode(raw)
        evidence = item["bang_chung_tong_hop"]
        sentences = [
            "Đây là yếu tố có đóng góp nổi bật trong nhóm đang xét của mẫu dữ liệu này.",
            "Tác động của đặc trưng bổ sung bằng chứng cho đầu ra được mô hình tính toán.",
            "Giá trị đóng góp cần được đọc cùng các yếu tố còn lại và nền tham chiếu.",
            "Sự đóng góp của đặc trưng phản ánh cách mô hình xử lý dữ liệu trong mẫu này.",
            "Vai trò của yếu tố được xác định trong phạm vi nhóm đặc trưng đang xem xét.",
        ]
        features = []
        for feature, sentence in zip(item["top_5_dac_trung"], sentences):
            features.append({"ten_dac_trung": feature["ten_dac_trung"],
                             "huong_tac_dong": feature["huong_tac_dong"], "dien_giai": sentence})
        result = {
            "tom_tat": "Các đặc trưng nổi bật đang đóng góp vào lựa chọn của mô hình. Kết quả cần được đối chiếu thêm với dữ liệu quan sát thực tế.",
            "lop_du_doan": item["lop_du_doan"],
            "so_sanh_hai_lop": {
                "lop_thu_hai": evidence["lop_thu_hai"], "khoang_cach_nho": evidence["khoang_cach_nho"],
                "dien_giai": "Hai đầu ra được đối chiếu theo kết quả tính toán; chênh lệch này chưa bảo đảm dự đoán chính xác.",
            },
            "tong_hop_shap": {
                "ho_tro_manh_nhat": evidence["ho_tro_manh_nhat"],
                "phan_doi_manh_nhat": evidence["phan_doi_manh_nhat"],
                "dien_giai": "Các đóng góp đang mô tả đầu ra của mô hình so với nền tham chiếu, chưa chứng minh nguyên nhân thực tế.",
            },
            "giai_thich_dac_trung": features,
            "de_xuat_kiem_tra": [
                {"nguon_du_lieu": guide["nguon_du_lieu"],
                 "noi_dung_can_kiem_tra": "Nếu nhật ký này được ghi nhận, đối chiếu các hoạt động liên quan để bổ sung bằng chứng.",
                 "muc_dich": "Làm rõ bối cảnh quan sát trước khi đưa ra kết luận về sự kiện thực tế."}
                for guide in item["huong_dan_kiem_tra_tham_khao"]
            ],
            "gioi_han": [
                "Giải thích phản ánh đầu ra của mô hình và chưa xác nhận hành vi tấn công thực tế.",
                "Các đóng góp phụ thuộc dữ liệu nền được chọn và chưa chứng minh quan hệ nhân quả.",
            ],
        }
        if self.behavior == "wrong_class":
            result["lop_du_doan"] = "Normal" if result["lop_du_doan"] != "Normal" else "DDoS"
        if self.behavior == "ascii_first" and len(self.calls) == 1:
            result["tom_tat"] = "Cac dac trung dang dong gop vao lua chon cua mo hinh va can doi chieu them."
        return FakeResponse(result)

    def close(self):
        pass
