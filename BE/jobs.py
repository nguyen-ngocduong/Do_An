"""Hai worker trong cùng process: dự đoán và giải thích theo yêu cầu."""

import logging
import hashlib
import queue
import shutil
import threading
import time
import uuid

import numpy as np
import pandas as pd
import psutil

from BE.config import MODEL_ID
from BE.reporting import write_report
from BE.shap_service import explain_sample
from BE.storage import Store
from BE.telemetry import Telemetry
from BE.utils import read_json, sha256_file, utc_now, write_json


logger = logging.getLogger(__name__)


class RequestConflict(Exception):
    """Yêu cầu chưa phù hợp với trạng thái hiện tại."""


class QueueCapacityError(Exception):
    """Đã đủ số mẫu đang chờ giải thích."""


class JobManager:
    def __init__(self, runtime, settings, gemini):
        self.runtime = runtime
        self.settings = settings
        self.gemini = gemini
        self.telemetry = Telemetry(settings)
        self.gemini.telemetry = self.telemetry
        self.store = Store(settings.runtime_dir / "app.sqlite3")
        self.runs_dir = settings.runtime_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.control_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.prediction_wakeup = threading.Event()
        self.gemini.shutdown_event = self.shutdown_event
        self.active_run = None
        self.pending_cases = set()
        self.prediction_queue = queue.Queue(maxsize=1)
        self.explanation_queue = queue.Queue(maxsize=settings.max_explain_rows)
        self.prediction_thread = threading.Thread(target=self.prediction_worker, name="prediction-worker", daemon=True)
        self.explanation_thread = threading.Thread(target=self.explanation_worker, name="explanation-worker", daemon=True)
        self.prediction_thread.start()
        self.explanation_thread.start()

    def run_dir(self, run_id):
        return self.runs_dir / run_id

    def case_dir(self, run_id, row_index):
        return self.run_dir(run_id) / "cases" / f"row_{row_index:04d}"

    def explanation_dir(self, run_id, row_index, audience_level="technical"):
        if audience_level == "technical":
            return self.case_dir(run_id, row_index)
        if audience_level == "basic":
            return self.case_dir(run_id, row_index) / "audiences" / "basic"
        raise ValueError("Mức diễn giải không hợp lệ.")

    def require_signature(self, run_id):
        run = self.store.get_run(run_id)
        if run is None:
            raise RequestConflict("Lần chạy đã bị xóa hoặc không còn tồn tại.")
        if run["signature"] != self.runtime.signature:
            raise RequestConflict("Lần chạy dùng artifact/cấu hình khác. Tạo lần chạy mới để giữ kết quả nguồn.")
        return run

    def create_run(self, content, filename, mode, interval, source_id=None):
        request_hash = hashlib.sha256(content + f"\n{filename}\n{mode}\n{interval}".encode()).hexdigest()
        with self.control_lock:
            if self.shutdown_event.is_set():
                raise RequestConflict("Server đang dừng.")
            if source_id is not None:
                receipt = self.store.ingestion_receipt(source_id)
                if receipt is not None:
                    if receipt["request_hash"] != request_hash:
                        raise RequestConflict("Idempotency-Key đã được dùng với nội dung khác.")
                    previous = self.store.get_run(receipt["run_id"])
                    if previous is None:
                        raise RequestConflict("Nguồn này đã được nhập rồi xóa; không tự tạo lại lần chạy.")
                    return previous
            if self.active_run is not None:
                raise RequestConflict("Đang có lần chạy dự đoán/phát lại. Hoàn tất hoặc dừng lần chạy đó trước.")
            run_id = uuid.uuid4().hex
            directory = self.run_dir(run_id)
            directory.mkdir()
            try:
                input_path = directory / "input.csv"
                input_path.write_bytes(content)
                values = self.runtime.read_csv(input_path)
                if len(values) > self.settings.max_input_rows:
                    raise ValueError("CSV vượt giới hạn số dòng.")
                np.save(directory / "input_values.npy", values, allow_pickle=False)
                pd.DataFrame(values, columns=self.runtime.feature_names).to_csv(
                    directory / "input_features.csv", index=False, float_format="%.17g"
                )
                write_json(directory / "protocol.json", {
                    "protocol": "single_server_backend_v1", "run_id": run_id,
                    "model_id": MODEL_ID, "bundle_sha256": self.runtime.bundle_sha256,
                    "signature": self.runtime.signature, "mode": mode,
                    "interval_seconds": interval, "input_sha256": sha256_file(input_path),
                    "input_values_sha256": sha256_file(directory / "input_values.npy"),
                    "rows": len(values), "feature_names": self.runtime.feature_names,
                    "class_names": self.runtime.class_names, "versions": self.runtime.versions,
                    "threads": self.settings.threads, "created_at": utc_now(),
                    "ground_truth_used": False, "model_refitted": False,
                    "validation_test_previously_viewed": True, "human_semantic_review": "deferred",
                    "ingestion_source_id": source_id,
                })
                self.store.create_run(run_id, filename, mode, interval, len(values), self.runtime.signature,
                                      source_id, request_hash)
            except Exception:
                shutil.rmtree(directory)
                raise
            self.active_run = run_id
            self.prediction_queue.put_nowait(run_id)
            return self.store.get_run(run_id)

    def load_input(self, run_id):
        directory = self.run_dir(run_id)
        protocol = read_json(directory / "protocol.json")
        if protocol["signature"] != self.runtime.signature:
            raise RequestConflict("Cấu hình lần chạy khác runtime hiện tại.")
        if sha256_file(directory / "input_values.npy") != protocol["input_values_sha256"]:
            raise ValueError("Checksum dữ liệu đầu vào đã lưu không khớp.")
        return np.load(directory / "input_values.npy", allow_pickle=False)

    def delete_run(self, run_id):
        with self.control_lock:
            run = self.store.get_run(run_id)
            if run is None:
                raise KeyError("Không tìm thấy lần chạy.")
            if self.active_run == run_id or run["status"] in ["queued", "running", "paused"]:
                raise RequestConflict("Lần chạy còn đang xử lý. Dừng Replay hoặc chờ dự đoán hoàn tất trước khi xóa.")
            if any(case[0] == run_id for case in self.pending_cases):
                raise RequestConflict("Lần chạy còn tác vụ SHAP/Gemini. Chờ giải thích hoàn tất trước khi xóa.")
            if any(case["status"] in ["queued", "shap_running", "gemini_running"] for case in self.store.explanations(run_id)):
                raise RequestConflict("Lần chạy còn giải thích chưa kết thúc. Chờ xử lý hoàn tất trước khi xóa.")

            directory = self.run_dir(run_id)
            if directory.is_symlink() or directory.parent.resolve() != self.runs_dir.resolve():
                raise RequestConflict("Thư mục lần chạy không hợp lệ; chưa xóa dữ liệu.")
            removed_directory = self.runs_dir / f".deleted-{uuid.uuid4().hex}"
            moved = directory.exists()
            if moved:
                directory.rename(removed_directory)
            try:
                self.store.delete_run(run_id)
            except Exception:
                if moved:
                    removed_directory.rename(directory)
                raise

            files_deleted = True
            if moved:
                try:
                    shutil.rmtree(removed_directory)
                except OSError:
                    files_deleted = False
                    logger.exception("Đã xóa lịch sử %s nhưng chưa dọn được %s", run_id, removed_directory)
            message = "Đã xóa lần chạy và các kết quả đã lưu."
            if not files_deleted:
                message = "Đã xóa lịch sử, nhưng một số tệp chưa được dọn. Liên hệ quản trị viên để hoàn tất xóa dữ liệu."
            return {"run_id": run_id, "files_deleted": files_deleted, "message": message}

    def control(self, run_id, action):
        with self.control_lock:
            run = self.require_signature(run_id)
            status = run["status"]
            if run["mode"] != "replay" and not (action == "resume" and status in ["interrupted", "failed"]):
                raise RequestConflict("Batch chỉ hỗ trợ resume nếu bị gián đoạn/lỗi; pause và stop dành cho replay.")
            if action == "pause":
                if status not in ["queued", "running"]:
                    raise RequestConflict("Chỉ tạm dừng lần chạy đang chờ hoặc đang chạy.")
                self.store.set_run_status(run_id, "paused", "Dòng đang suy luận có thể hoàn tất trước khi tạm dừng.")
            elif action == "stop":
                if status not in ["queued", "running", "paused"]:
                    raise RequestConflict("Lần chạy hiện không hoạt động.")
                self.store.set_run_status(run_id, "stopped", "Đã yêu cầu dừng; giữ kết quả đã xử lý.")
            elif action == "resume":
                if status == "paused":
                    self.store.set_run_status(run_id, "running")
                elif status in ["interrupted", "failed", "stopped"]:
                    if self.active_run is not None:
                        raise RequestConflict("Worker dự đoán còn bận; chờ trước khi tiếp tục.")
                    if run["processed_rows"] >= run["total_rows"]:
                        self.store.set_run_status(run_id, "completed")
                        return self.store.get_run(run_id)
                    self.load_input(run_id)
                    self.active_run = run_id
                    self.store.set_run_status(run_id, "queued")
                    self.prediction_queue.put_nowait(run_id)
                else:
                    raise RequestConflict("Trạng thái hiện tại không thể tiếp tục.")
            self.prediction_wakeup.set()
            return self.store.get_run(run_id)

    def prediction_worker(self):
        while not self.shutdown_event.is_set():
            try:
                run_id = self.prediction_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                self.process_predictions(run_id)
            except Exception as error:
                logger.exception("Lỗi tác vụ dự đoán %s", run_id)
                self.store.set_run_status(run_id, "failed", f"Không xử lý được dự đoán ({type(error).__name__}).")
            finally:
                with self.control_lock:
                    self.active_run = None
                self.prediction_queue.task_done()

    def process_predictions(self, run_id):
        with self.telemetry.span("nidr.predict", metadata={"run_id": run_id, "model_id": MODEL_ID}) as observation:
            observation.update(input={"run_id": run_id, "model_id": MODEL_ID})
            self._process_predictions(run_id)
            run = self.store.get_run(run_id)
            observation.update(output={"status": run["status"], "processed_rows": run["processed_rows"]})

    def _process_predictions(self, run_id):
        self.prediction_wakeup.clear()
        run = self.require_signature(run_id)
        values = self.load_input(run_id)
        row_index = run["processed_rows"]
        if run["mode"] == "batch":
            self.store.set_run_status(run_id, "running")
            started = time.perf_counter()
            probabilities = self.runtime.predict(values[row_index:])
            seconds_per_row = (time.perf_counter() - started) / len(probabilities)
            for offset, row in enumerate(probabilities):
                if self.shutdown_event.is_set():
                    self.store.set_run_status(run_id, "interrupted", "Server dừng khi đang lưu dự đoán.")
                    return
                self.store.save_prediction(run_id, row_index + offset, row, self.runtime.class_names, seconds_per_row)
            self.store.set_run_status(run_id, "completed")
            return

        while row_index < len(values):
            if self.shutdown_event.is_set():
                self.store.set_run_status(run_id, "interrupted", "Server dừng; có thể tiếp tục phần chưa xử lý.")
                return
            with self.control_lock:
                run = self.store.get_run(run_id)
                status = run["status"]
                if status == "stopped":
                    return
                if status == "queued":
                    self.store.set_run_status(run_id, "running")
            if status == "paused":
                self.prediction_wakeup.wait(0.1)
                self.prediction_wakeup.clear()
                continue
            started = time.perf_counter()
            probabilities = self.runtime.predict(values[row_index:row_index + 1])[0]
            seconds = time.perf_counter() - started
            self.store.save_prediction(run_id, row_index, probabilities, self.runtime.class_names, seconds)
            row_index += 1
            if row_index < len(values):
                self.prediction_wakeup.wait(max(0, run["interval_seconds"] - seconds))
                self.prediction_wakeup.clear()
        if self.store.get_run(run_id)["status"] != "stopped":
            self.store.set_run_status(run_id, "completed")

    def request_explanations(self, run_id, indices, use_gemini, retry_gemini=False, audience_level="technical"):
        with self.control_lock:
            self.require_signature(run_id)
            for index in indices:
                if self.store.prediction(run_id, index) is None:
                    raise RequestConflict(f"Dòng {index} chưa có dự đoán; chưa thể giải thích.")
            pending = []
            for index in indices:
                existing = self.store.explanation(run_id, index, audience_level)
                if (run_id, index, audience_level) in self.pending_cases:
                    continue
                if existing and existing["status"] in ["completed", "partial"] and not retry_gemini:
                    wants_missing_gemini = use_gemini and existing["gemini_status"] in ["gemini_disabled", "not_configured"]
                    if not wants_missing_gemini:
                        continue
                pending.append(index)
            if len(self.pending_cases) + len(pending) > self.settings.max_explain_rows:
                raise QueueCapacityError("Hàng chờ đã đủ 50 mẫu; chờ các mẫu hiện tại hoàn tất.")
            for index in pending:
                self.pending_cases.add((run_id, index, audience_level))
                self.store.queue_explanation(run_id, index, use_gemini, audience_level)
                self.explanation_queue.put_nowait((run_id, index, use_gemini, retry_gemini, audience_level))
            return [self.store.explanation(run_id, index, audience_level) for index in indices]

    def explanation_worker(self):
        while not self.shutdown_event.is_set():
            try:
                task = self.explanation_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            run_id, index, use_gemini, retry_gemini, audience_level = task
            try:
                self.process_explanation(run_id, index, use_gemini, retry_gemini, audience_level)
            except Exception as error:
                logger.exception("Lỗi giải thích %s / %s", run_id, index)
                self.store.update_explanation(
                    run_id, index, "failed", "not_completed",
                    f"Không hoàn tất giải thích ({type(error).__name__}); kết quả dự đoán vẫn được giữ.",
                    audience_level,
                )
            finally:
                with self.control_lock:
                    self.pending_cases.discard((run_id, index, audience_level))
                self.explanation_queue.task_done()

    def process_explanation(self, run_id, index, use_gemini, retry_gemini, audience_level="technical"):
        with self.telemetry.span("nidr.explanation", metadata={
            "run_id": run_id, "row_index": index, "audience_level": audience_level,
            "use_gemini": use_gemini,
        }) as observation:
            observation.update(input={"run_id": run_id, "row_index": index,
                                      "audience_level": audience_level, "use_gemini": use_gemini})
            self._process_explanation(run_id, index, use_gemini, retry_gemini, audience_level, observation)

    def _process_explanation(self, run_id, index, use_gemini, retry_gemini, audience_level, observation):
        self.require_signature(run_id)
        shared_directory = self.case_dir(run_id, index)
        directory = self.explanation_dir(run_id, index, audience_level)
        directory.mkdir(parents=True, exist_ok=True)
        if retry_gemini:
            archive = directory / "previous_gemini" / uuid.uuid4().hex
            for pattern in ["gemini_*.json", "explanation_vi*.json"]:
                for path in directory.glob(pattern):
                    archive.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(path), str(archive / path.name))
        self.store.update_explanation(run_id, index, "shap_running", audience_level=audience_level)
        values = self.load_input(run_id)
        prediction = self.store.prediction(run_id, index)
        expected = np.asarray([prediction["probabilities"][name] for name in self.runtime.class_names])
        with self.telemetry.span("nidr.shap", metadata={"run_id": run_id, "row_index": index}) as shap_span:
            shap_span.update(input={"row_index": index, "input_feature_count": len(self.runtime.feature_names),
                                    "model_id": MODEL_ID})
            item = explain_sample(self.runtime, values[index:index + 1], index, expected, shared_directory)
            shap_span.update(output={"class": item["predicted_class"], "shap_seconds": item["shap_seconds"]})
        self.store.update_explanation(run_id, index, "gemini_running", audience_level=audience_level)
        record = self.gemini.explain(item, directory, enabled=use_gemini, audience_level=audience_level)
        write_report(item, record, directory)
        status = "completed" if record["status"] in ["accepted", "gemini_disabled"] else "partial"
        if record["status"] == "interrupted":
            status = "interrupted"
        write_json(directory / "execution.json", {
            "shap_seconds": item["shap_seconds"], "api_seconds": record["api_seconds"],
            "total_tokens": record["total_tokens"], "rss_mib": psutil.Process().memory_info().rss / 1024**2,
            "updated_at": utc_now(), "signature": self.runtime.signature,
            "audience_level": audience_level,
            "langfuse_trace_id": observation.trace_id,
        })
        self.store.update_explanation(run_id, index, status, record["status"], record["message"], audience_level)
        observation.update(output={"status": status, "gemini_status": record["status"],
                                   "total_tokens": record["total_tokens"]})

    def stop(self):
        self.shutdown_event.set()
        self.prediction_wakeup.set()
        self.prediction_thread.join(timeout=15)
        self.explanation_thread.join(timeout=75)
        for run in self.store.list_runs(limit=10000)["items"]:
            if run["status"] in ["queued", "running", "paused"]:
                self.store.set_run_status(run["id"], "interrupted", "Server đã dừng; kết quả đã hoàn thành vẫn được lưu.")
            for case in self.store.explanations(run["id"]):
                if case["status"] in ["queued", "shap_running", "gemini_running"]:
                    self.store.update_explanation(
                        run["id"], case["row_index"], "interrupted", "interrupted", "Server đã dừng.", case["audience_level"],
                    )
        self.gemini.close()
        self.telemetry.close()
