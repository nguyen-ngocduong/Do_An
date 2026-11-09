"""REST nội bộ cùng mạng Docker. Không in tài khoản hoặc response nhạy cảm."""

import os

import httpx


class BackendBusy(Exception):
    pass


class NidrClient:
    def __init__(self, client=None):
        self.client = client or httpx.Client(
            base_url=os.getenv("NIDR_API_URL", "http://backend:8000"),
            auth=(os.environ["ADMIN_USERNAME"], os.environ["ADMIN_PASSWORD"]),
            timeout=15, trust_env=False,
        )

    def feature_names(self):
        capabilities = self.client.get("/api/observability")
        if capabilities.status_code != 200 or not capabilities.json().get("ingestion_idempotency"):
            raise RuntimeError("Consumer cần BE 1.8.0+ có hỗ trợ Idempotency-Key; chưa gửi dữ liệu.")
        response = self.client.get("/api/schema")
        response.raise_for_status()
        # Schema đóng băng của BE có input_features.
        schema = response.json()
        return schema.get("feature_names") or schema["input_features"]

    def submit(self, content, filename, source_id, mode="batch", interval=0.05):
        response = self.client.post(
            "/api/runs", files={"file": (filename, content, "text/csv")},
            data={"mode": mode, "interval_seconds": str(interval)},
            headers={"Idempotency-Key": source_id},
        )
        if response.status_code == 409 and str(response.json().get("detail", "")).startswith("Đang có lần chạy"):
            raise BackendBusy()
        if response.status_code != 202:
            raise RuntimeError(f"BE từ chối nhập CSV (HTTP {response.status_code}); chưa đánh dấu đã nhập.")
        return response.json()

    def run(self, run_id):
        response = self.client.get(f"/api/runs/{run_id}")
        if response.status_code != 200:
            raise RuntimeError(f"Không đọc được lần chạy (HTTP {response.status_code}).")
        return response.json()

    def close(self):
        self.client.close()
