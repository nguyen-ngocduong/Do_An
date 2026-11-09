"""REST API và Swagger; giao diện Next.js được phục vụ riêng từ FE/."""

import fcntl
from contextlib import asynccontextmanager
from pathlib import Path as FilePath
from typing import Annotated, Literal

import psutil
import pandas as pd
from fastapi import APIRouter, Depends, FastAPI, File, Form, Header, HTTPException, Path, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from BE.artifacts import ModelRuntime
from BE.auth import SESSION_COOKIE, SESSION_SECONDS, SessionStore, secure_cookie, valid_credentials, verify_browser_origin
from BE.config import MODEL_ID, Settings, load_settings
from BE.dashboard import dashboard_summary
from BE.exports import CASE_FILES, case_file, prediction_csv, report_zip
from BE.gemini_service import GeminiService
from BE.jobs import JobManager, QueueCapacityError, RequestConflict
from BE.playbooks import get_playbook
from BE.reviews import read_review, save_review
from BE.schemas import (
    AlertDetail, AlertPage, AlertStatus, AlertUpdate, AudienceLevel, ClassName,
    ControlRequest, DashboardPeriod, DashboardSummary, ErrorResponse, ExplanationDetail, ExplanationList, ExplanationRequest,
    ExplanationFilter, ExplanationPage, ExplanationStatus, Playbook,
    HumanReviewRequest, InputRow, LoginRequest, PredictionList, RunDeleted, RunInfo, RunList, RunSummary, SessionInfo,
)
from BE.storage import AlertConflict
from BE.utils import read_json


RunId = Annotated[str, Path(pattern=r"^[a-f0-9]{32}$", description="ID lần chạy do POST /api/runs trả về.")]
RowIndex = Annotated[int, Path(ge=0, description="Chỉ số dòng CSV bắt đầu từ 0.")]


class UploadLimitMiddleware:
    """Giới hạn body trước khi multipart được ghi ra file tạm."""

    def __init__(self, app, max_bytes):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") != "/api/runs":
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.max_bytes:
                response = JSONResponse(status_code=413, content={"detail": "CSV vượt giới hạn dung lượng cho phép."})
                await response(scope, receive, send)
                return
            if not message.get("more_body", False):
                break
        delivered = False

        async def buffered_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, buffered_receive, send)


def create_app(settings=None, runtime=None, gemini_client=None):
    @asynccontextmanager
    async def lifespan(application):
        configured = settings or load_settings()
        if not configured.admin_username or not configured.admin_password:
            raise ValueError("Đặt tài khoản ADMIN_USERNAME/ADMIN_PASSWORD trước khi mở BE.")
        configured.runtime_dir.mkdir(parents=True, exist_ok=True)
        process_lock = (configured.runtime_dir / "server.lock").open("a")
        manager = None
        try:
            try:
                fcntl.flock(process_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("Runtime đã có server sử dụng; chạy Uvicorn với một worker.") from None
            application.state.settings = configured
            application.state.sessions = SessionStore()
            shared_runtime = runtime or await run_in_threadpool(ModelRuntime, configured)
            gemini = GeminiService(shared_runtime, configured, client=gemini_client)
            manager = JobManager(shared_runtime, configured, gemini)
            application.state.manager = manager
            yield
        finally:
            if manager is not None:
                await run_in_threadpool(manager.stop)
            process_lock.close()

    application = FastAPI(
        title="CICIoT2023 — Predict, SHAP và Gemini",
        description=(
            "REST API trên một server. Upload CSV đặc trưng gốc, dự đoán theo lô hoặc phát lại, "
            "rồi chọn dòng cần giải thích. Model được nạp một lần; không huấn luyện lại. "
            "Các yêu cầu xử lý dài trả ID/trạng thái để theo dõi."
        ),
        version="1.8.0", lifespan=lifespan,
        docs_url=None, redoc_url=None, openapi_url=None,
    )
    upload_limit = (settings or Settings()).max_upload_bytes + 64 * 1024
    application.add_middleware(UploadLimitMiddleware, max_bytes=upload_limit)
    security = HTTPBasic(auto_error=False)

    def authenticate(request: Request, credentials: HTTPBasicCredentials | None = Depends(security)):
        configured = request.app.state.settings
        if credentials is not None:
            if not valid_credentials(credentials.username, credentials.password, configured):
                raise HTTPException(401, "Tài khoản hoặc mật khẩu không đúng.", headers={"WWW-Authenticate": "Basic"})
            if request.method not in ["GET", "HEAD", "OPTIONS"]:
                verify_browser_origin(request)
            return credentials.username
        session = request.app.state.sessions.read(request.cookies.get(SESSION_COOKIE))
        if session is None:
            # Không yêu cầu popup Basic khi trình duyệt dùng trang đăng nhập riêng.
            headers = {"WWW-Authenticate": "Basic"} if request.url.path in ["/", "/docs", "/openapi.json"] else {}
            raise HTTPException(401, "Phiên đăng nhập không còn hiệu lực. Vui lòng đăng nhập lại.", headers=headers)
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            verify_browser_origin(request)
        return session["username"]

    @application.post("/api/auth/login", response_model=SessionInfo, tags=["Đăng nhập"])
    def login(body: LoginRequest, request: Request, response: Response):
        verify_browser_origin(request)
        sessions = request.app.state.sessions
        client_ip = request.client.host if request.client else "local"
        passed = sessions.login_attempt(client_ip, body.username, body.password, request.app.state.settings)
        if not passed:
            raise HTTPException(401, "Tên đăng nhập hoặc mật khẩu không đúng.")
        sessions.revoke(request.cookies.get(SESSION_COOKIE))
        token, expires_at = sessions.create(body.username)
        response.set_cookie(
            SESSION_COOKIE, token, max_age=SESSION_SECONDS if body.remember else None, path="/",
            httponly=True, secure=secure_cookie(request), samesite="strict",
        )
        response.headers["Cache-Control"] = "no-store"
        return {"username": body.username, "expires_at": expires_at}

    @application.get("/api/auth/session", response_model=SessionInfo, tags=["Đăng nhập"])
    def session_info(request: Request, response: Response, username: str = Depends(authenticate)):
        response.headers["Cache-Control"] = "no-store"
        session = request.app.state.sessions.read(request.cookies.get(SESSION_COOKIE))
        return {"username": username, "expires_at": session["expires_at"] if session else None}

    @application.post("/api/auth/logout", tags=["Đăng nhập"])
    def logout(request: Request, response: Response):
        verify_browser_origin(request)
        request.app.state.sessions.revoke(request.cookies.get(SESSION_COOKIE))
        response.delete_cookie(SESSION_COOKIE, path="/", secure=secure_cookie(request), httponly=True, samesite="strict")
        response.headers["Cache-Control"] = "no-store"
        return {"message": "Đã đăng xuất."}

    def manager_from(request: Request):
        return request.app.state.manager

    def require_run(manager, run_id):
        result = manager.store.get_run(run_id)
        if result is None:
            raise HTTPException(404, "Không tìm thấy lần chạy.")
        return result

    @application.exception_handler(RequestConflict)
    @application.exception_handler(AlertConflict)
    async def conflict_handler(request, error):
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @application.exception_handler(QueueCapacityError)
    async def capacity_handler(request, error):
        return JSONResponse(status_code=429, content={"detail": str(error)})

    @application.exception_handler(ValueError)
    async def value_handler(request, error):
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @application.exception_handler(RequestValidationError)
    async def validation_handler(request, error):
        # Không phản chiếu raw body hoặc credentials vào thông báo lỗi.
        issues = []
        for item in error.errors():
            messages = {
                "missing": "Thiếu trường bắt buộc.",
                "literal_error": "Giá trị không thuộc các lựa chọn được hỗ trợ.",
                "int_type": "Cần số nguyên; không nhận chuỗi hoặc giá trị đúng/sai.",
                "int_parsing": "Không chuyển được giá trị thành số nguyên.",
                "greater_than_equal": "Giá trị nhỏ hơn giới hạn tối thiểu trong schema.",
                "less_than_equal": "Giá trị vượt giới hạn tối đa trong schema.",
                "too_short": "Chưa đủ phần tử theo schema.",
                "too_long": "Có quá nhiều phần tử theo schema.",
                "extra_forbidden": "Yêu cầu có trường không được hỗ trợ.",
                "string_pattern_mismatch": "Chuỗi không đúng định dạng yêu cầu.",
            }
            message = messages.get(item["type"], "Giá trị không hợp lệ theo schema.")
            if item["type"] == "value_error":
                message = str(item.get("ctx", {}).get("error", message))
            issues.append({"field": ".".join(str(part) for part in item["loc"]), "message": message})
        return JSONResponse(status_code=422, content={"detail": "Dữ liệu yêu cầu không hợp lệ.", "errors": issues})

    @application.get("/", include_in_schema=False, dependencies=[Depends(authenticate)])
    def home():
        return RedirectResponse("/docs", status_code=307)

    @application.get("/docs", include_in_schema=False, dependencies=[Depends(authenticate)])
    def swagger():
        return get_swagger_ui_html(openapi_url="/openapi.json", title="CICIoT2023 — Swagger API")

    @application.get("/openapi.json", include_in_schema=False, dependencies=[Depends(authenticate)])
    def openapi():
        return JSONResponse(application.openapi())

    @application.get("/health", tags=["Trạng thái"], summary="Kiểm tra ứng dụng sẵn sàng")
    def health(request: Request):
        manager = manager_from(request)
        return {"status": "ready" if manager.runtime.ready else "not_ready"}

    router = APIRouter(
        prefix="/api", dependencies=[Depends(authenticate)],
        responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse},
                   409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )

    @router.get("/schema", tags=["Model và đầu vào"], summary="Schema CSV và thứ tự tám lớp")
    def input_schema(request: Request):
        return manager_from(request).runtime.input_schema

    @router.get("/observability", tags=["Trạng thái"], summary="Trạng thái cấu hình Langfuse, không trả khóa")
    def observability(request: Request):
        return {**manager_from(request).telemetry.status(), "ingestion_idempotency": True}

    @router.get("/input-template", tags=["Model và đầu vào"], summary="Tải CSV mẫu có đủ tên đặc trưng")
    def input_template(request: Request):
        names = manager_from(request).runtime.feature_names
        content = pd.DataFrame(columns=names).to_csv(index=False)
        return Response(content, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="input_template.csv"'})

    @router.get("/model", tags=["Model và đầu vào"], summary="Model, kiểm tra nguồn và trạng thái Gemini")
    def model_info(request: Request):
        manager = manager_from(request)
        return {
            "model_id": MODEL_ID, "model_load_count": manager.runtime.load_count,
            "checks": manager.runtime.checks, "threads": manager.settings.threads,
            "gemini_configured": manager.gemini.client is not None,
            "gemini_model": manager.settings.gemini_model,
            "rss_mib": psutil.Process().memory_info().rss / 1024**2,
            "prediction_worker_alive": manager.prediction_thread.is_alive(),
            "explanation_worker_alive": manager.explanation_thread.is_alive(),
            "limits": {"csv_rows": manager.settings.max_input_rows,
                       "upload_bytes": manager.settings.max_upload_bytes,
                       "explanation_rows": manager.settings.max_explain_rows},
            "shap_config": {name: manager.runtime.shap_protocol[name] for name in
                            ["background_size", "max_evals", "additivity_tolerance"]},
        }

    @router.post("/runs", response_model=RunInfo, status_code=202, tags=["Lần chạy"],
                 summary="Upload CSV và bắt đầu dự đoán", responses={413: {"model": ErrorResponse}})
    async def create_run(
        request: Request,
        file: Annotated[UploadFile, File(description="CSV UTF-8 có 46 đặc trưng gốc; label là cột tùy chọn.")],
        mode: Annotated[Literal["batch", "replay"], Form(description="Theo lô hoặc dự đoán khi phát từng dòng.")] = "batch",
        interval_seconds: Annotated[float, Form(ge=0.05, le=60, description="Nhịp replay yêu cầu; lưu thời gian xử lý thực tế.")] = 1.0,
        idempotency_key: Annotated[str | None, Header(pattern=r"^[A-Za-z0-9:._-]{1,160}$") ] = None,
    ):
        manager = manager_from(request)
        content = await file.read(manager.settings.max_upload_bytes + 1)
        await file.close()
        if len(content) > manager.settings.max_upload_bytes:
            raise HTTPException(413, "CSV vượt giới hạn 10 MiB.")
        if not content:
            raise HTTPException(422, "CSV đang trống.")
        filename = FilePath(file.filename or "input.csv").name
        if not filename.lower().endswith(".csv"):
            raise HTTPException(422, "Chỉ nhận file .csv.")
        return await run_in_threadpool(manager.create_run, content, filename, mode, interval_seconds, idempotency_key)

    @router.get("/dashboard", response_model=DashboardSummary, tags=["Tổng quan"],
                summary="Thống kê toàn hệ thống theo thời gian xử lý mẫu",
                description="Ngày theo Asia/Ho_Chi_Minh. Mẫu lọc theo thời gian dự đoán; cảnh báo/đánh giá là trạng thái hiện tại của nhóm mẫu đó. Toàn lịch sử giữ biểu đồ 30 ngày gần nhất. Chỉ đọc dữ liệu đã lưu; không gọi model hoặc Gemini.")
    def get_dashboard(request: Request, period: DashboardPeriod = "7d",
                      run_id: str | None = Query(default=None, pattern=r"^[a-f0-9]{32}$")):
        manager = manager_from(request)
        if run_id:
            require_run(manager, run_id)
        return dashboard_summary(manager, period, run_id)

    @router.get("/runs", response_model=RunList, tags=["Lần chạy"], summary="Danh sách lịch sử")
    def list_runs(request: Request, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
        return manager_from(request).store.list_runs(offset, limit)

    @router.get("/runs/{run_id}", response_model=RunInfo, tags=["Lần chạy"], summary="Tiến độ và trạng thái lần chạy")
    def get_run(request: Request, run_id: RunId):
        return require_run(manager_from(request), run_id)

    @router.delete("/runs/{run_id}", response_model=RunDeleted, tags=["Lần chạy"],
                   summary="Xóa lịch sử, CSV đã tải lên và toàn bộ kết quả của một lần chạy",
                   description="Chỉ xóa khi dự đoán và SHAP/Gemini đã dừng. Xóa cả cảnh báo, nhật ký xử lý và đánh giá thủ công; không thể hoàn tác.")
    def delete_run(request: Request, run_id: RunId):
        try:
            return manager_from(request).delete_run(run_id)
        except KeyError:
            raise HTTPException(404, "Không tìm thấy lần chạy.") from None

    @router.get("/runs/{run_id}/predictions", response_model=PredictionList, tags=["Dự đoán"], summary="Các dòng đã có dự đoán")
    def get_predictions(
        request: Request, run_id: RunId, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
        predicted_class: ClassName | None = None, explanation_status: ExplanationFilter | None = None,
        audience_level: AudienceLevel = "technical",
    ):
        manager = manager_from(request)
        require_run(manager, run_id)
        return manager.store.prediction_page(run_id, offset, limit, predicted_class, explanation_status, audience_level)

    @router.get("/runs/{run_id}/inputs/{row_index}", response_model=InputRow, tags=["Dự đoán"],
                summary="Đặc trưng đầu vào của một dòng CSV đã lưu; không suy luận lại")
    def get_input_row(request: Request, run_id: RunId, row_index: RowIndex):
        manager = manager_from(request)
        run = require_run(manager, run_id)
        if row_index >= run["total_rows"]:
            raise HTTPException(404, "Chỉ số dòng nằm ngoài CSV của lần chạy.")
        values = manager.load_input(run_id)[row_index]
        features = {}
        for name, value in zip(manager.runtime.feature_names, values):
            features[name] = None if pd.isna(value) else float(value)
        return {"run_id": run_id, "row_index": row_index, "features": features}

    @router.get("/runs/{run_id}/summary", response_model=RunSummary, tags=["Lần chạy"],
                summary="Thống kê tám lớp, giải thích và cảnh báo của lần chạy")
    def run_summary(request: Request, run_id: RunId, audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        require_run(manager, run_id)
        return manager.store.summary(run_id, audience_level)

    @router.post("/runs/{run_id}/control", response_model=RunInfo, tags=["Dự đoán"], summary="Điều khiển replay")
    def control_run(request: Request, run_id: RunId, body: ControlRequest):
        manager = manager_from(request)
        require_run(manager, run_id)
        return manager.control(run_id, body.action)

    @router.post("/runs/{run_id}/explanations", response_model=ExplanationList, status_code=202,
                 tags=["SHAP và Gemini"], summary="Giải thích những dòng đã chọn", responses={429: {"model": ErrorResponse}})
    def explain(request: Request, run_id: RunId, body: ExplanationRequest):
        manager = manager_from(request)
        require_run(manager, run_id)
        items = manager.request_explanations(run_id, body.row_indices, body.use_gemini, body.retry_gemini, body.audience_level)
        return {"run_id": run_id, "items": items}

    @router.get("/runs/{run_id}/explanations", response_model=ExplanationPage, tags=["SHAP và Gemini"],
                summary="Danh sách trạng thái giải thích; đọc không tạo lời gọi Gemini")
    def list_explanations(
        request: Request, run_id: RunId, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
        status: ExplanationStatus | None = None, audience_level: AudienceLevel = "technical",
    ):
        manager = manager_from(request)
        require_run(manager, run_id)
        return manager.store.explanation_page(run_id, offset, limit, status, audience_level)

    @router.get("/runs/{run_id}/explanations/{row_index}", response_model=ExplanationDetail,
                tags=["SHAP và Gemini"], summary="Trạng thái, SHAP và diễn giải của một mẫu")
    def get_explanation(request: Request, run_id: RunId, row_index: RowIndex, audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        require_run(manager, run_id)
        state = manager.store.explanation(run_id, row_index, audience_level)
        if state is None:
            raise HTTPException(404, "Mẫu chưa được yêu cầu giải thích.")
        shared_directory = manager.case_dir(run_id, row_index)
        directory = manager.explanation_dir(run_id, row_index, audience_level)
        state["files"] = {}
        if (shared_directory / "explanation.json").is_file():
            state["explanation"] = read_json(shared_directory / "explanation.json")
            playbook_path = directory / "playbook.json"
            state["playbook"] = (read_json(playbook_path) if playbook_path.is_file()
                                 else get_playbook(state["explanation"]["predicted_class"]))
        if state["status"] in ["completed", "partial"]:
            result_path = directory / "explanation_vi.json"
            if not result_path.is_file():
                result_path = directory / "explanation_vi_draft.json"
            if result_path.is_file():
                state["gemini"] = read_json(result_path)
            for name in sorted(CASE_FILES):
                if case_file(manager, run_id, row_index, name, audience_level).is_file():
                    state["files"][name] = f"/api/runs/{run_id}/explanations/{row_index}/files/{name}?audience_level={audience_level}"
        return state

    @router.get("/runs/{run_id}/explanations/{row_index}/files/{filename}", tags=["SHAP và Gemini"], summary="Tải biểu đồ hoặc file giải thích")
    def get_case_file(request: Request, run_id: RunId, row_index: RowIndex, filename: str,
                      audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        require_run(manager, run_id)
        state = manager.store.explanation(run_id, row_index, audience_level)
        if filename not in CASE_FILES or state is None:
            raise HTTPException(404, "Không tìm thấy file kết quả.")
        if state["status"] not in ["completed", "partial"]:
            raise HTTPException(409, "Tác vụ chưa hoàn tất ghi file.")
        path = case_file(manager, run_id, row_index, filename, audience_level)
        if not path.is_file():
            raise HTTPException(404, "Chưa có file kết quả này.")
        return FileResponse(path, filename=filename)

    @router.get("/runs/{run_id}/human-reviews/{row_index}", tags=["Đánh giá thủ công"], summary="Đọc đánh giá và dấu vân tay bằng chứng")
    def get_human_review(request: Request, run_id: RunId, row_index: RowIndex, audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        require_run(manager, run_id)
        return read_review(manager, run_id, row_index, audience_level)

    @router.put("/runs/{run_id}/human-reviews/{row_index}", tags=["Đánh giá thủ công"], summary="Lưu đánh giá của người dùng; không đổi nhãn model")
    def put_human_review(request: Request, run_id: RunId, row_index: RowIndex, body: HumanReviewRequest,
                         audience_level: AudienceLevel = "technical", username: str = Depends(authenticate)):
        manager = manager_from(request)
        with manager.control_lock:
            require_run(manager, run_id)
            return save_review(manager, run_id, row_index, audience_level, body, username)

    @router.get("/runs/{run_id}/human-reviews/{row_index}/export", tags=["Đánh giá thủ công"], summary="Tải đánh giá đã lưu, kèm dấu vân tay và tình trạng bằng chứng")
    def export_human_review(request: Request, run_id: RunId, row_index: RowIndex, audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        require_run(manager, run_id)
        result = read_review(manager, run_id, row_index, audience_level)
        if result["review"] is None:
            raise HTTPException(404, "Chưa có bản đánh giá đã lưu.")
        return JSONResponse(result, headers={"Content-Disposition": f'attachment; filename="human_review_row_{row_index}_{audience_level}.json"'})

    @router.get("/playbooks/{class_name}", response_model=Playbook, tags=["Hướng dẫn kiểm tra"],
                summary="Hướng dẫn có nguồn theo lớp; hoạt động khi chưa có Gemini")
    def playbook(class_name: ClassName):
        return get_playbook(class_name)

    @router.get("/alerts", response_model=AlertPage, tags=["Cảnh báo"],
                summary="Cảnh báo theo model; lọc và phân trang")
    def list_alerts(
        request: Request, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
        status: AlertStatus | None = None, predicted_class: ClassName | None = None,
        run_id: str | None = Query(None, pattern=r"^[a-f0-9]{32}$"), audience_level: AudienceLevel = "technical",
    ):
        manager = manager_from(request)
        if run_id is not None:
            require_run(manager, run_id)
        return manager.store.alert_page(offset, limit, status, predicted_class, run_id, audience_level)

    def alert_detail(manager, alert_id, audience_level):
        result = manager.store.alert(alert_id, audience_level)
        if result is None:
            raise HTTPException(404, "Không tìm thấy cảnh báo.")
        result["prediction"] = manager.store.prediction(result["run_id"], result["row_index"])
        result["prediction"].update(
            explanation_status=result["explanation_status"], gemini_status=result["gemini_status"],
            alert_id=result["id"], alert_status=result["status"],
        )
        result["playbook"] = get_playbook(result["predicted_class"])
        result["audience_level"] = audience_level
        result["explanation_url"] = (
            f"/api/runs/{result['run_id']}/explanations/{result['row_index']}?audience_level={audience_level}"
        )
        return result

    @router.get("/alerts/{alert_id}", response_model=AlertDetail, tags=["Cảnh báo"],
                summary="Dự đoán, hướng dẫn và lịch sử xử lý cảnh báo")
    def get_alert(request: Request, alert_id: int = Path(ge=1), audience_level: AudienceLevel = "technical"):
        return alert_detail(manager_from(request), alert_id, audience_level)

    @router.patch("/alerts/{alert_id}", response_model=AlertDetail, tags=["Cảnh báo"],
                  summary="Tiếp nhận, đóng hoặc mở lại cảnh báo; không thay đổi dự đoán")
    def update_alert(request: Request, body: AlertUpdate, alert_id: int = Path(ge=1),
                     actor: str = Depends(authenticate), audience_level: AudienceLevel = "technical"):
        manager = manager_from(request)
        if not manager.store.update_alert(alert_id, body.status, body.note, actor):
            raise HTTPException(404, "Không tìm thấy cảnh báo.")
        return alert_detail(manager, alert_id, audience_level)

    @router.get("/runs/{run_id}/export", tags=["Xuất kết quả"], summary="Tải CSV dự đoán hoặc gói báo cáo ZIP")
    def export(request: Request, run_id: RunId, format: Literal["csv", "zip"] = "csv"):
        manager = manager_from(request)
        with manager.control_lock:
            require_run(manager, run_id)
            if format == "csv":
                return Response(
                    prediction_csv(manager, run_id), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{run_id}_predictions.csv"'},
                )
            path = report_zip(manager, run_id)
        return FileResponse(
            path, media_type="application/zip", filename=f"{run_id}_reports.zip",
            background=BackgroundTask(path.unlink, missing_ok=True),
        )

    application.include_router(router)
    return application


app = create_app()
