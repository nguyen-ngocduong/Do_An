"""Schema REST API; Swagger hiển thị cùng hợp đồng mà BE kiểm tra."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator


ClassName = Literal["Normal", "BruteForce", "DDoS", "DoS", "Mirai", "Recon", "Spoofing", "Web-Based"]
AudienceLevel = Literal["basic", "technical"]
ExplanationStatus = Literal["queued", "shap_running", "gemini_running", "completed", "partial", "failed", "interrupted"]
ExplanationFilter = Literal["not_requested", "queued", "shap_running", "gemini_running", "completed", "partial", "failed", "interrupted"]
AlertStatus = Literal["new", "acknowledged", "closed"]


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=4096, repr=False)
    remember: bool = Field(default=False, description="Ghi nhớ cookie trên trình duyệt, vẫn hết hạn tối đa sau tám giờ.")


class SessionInfo(BaseModel):
    username: str
    expires_at: float | None = Field(default=None, description="Unix timestamp; null khi dùng HTTP Basic.")


class ControlRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["pause", "resume", "stop"] = Field(description="Tạm dừng, tiếp tục hoặc dừng replay.")


class ExplanationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    row_indices: list[Annotated[StrictInt, Field(ge=0)]] = Field(
        min_length=1, max_length=50, description="Chỉ số dòng bắt đầu từ 0; tối đa 50 dòng không lặp.",
        examples=[[0, 1]],
    )
    use_gemini: bool = Field(default=True, description="False để chỉ tính SHAP và tạo báo cáo số liệu.")
    retry_gemini: bool = Field(
        default=False,
        description="Chủ động gọi lại Gemini, lưu lịch sử cũ. Có thể phát sinh yêu cầu API mới; vẫn dùng cache SHAP.",
    )
    audience_level: AudienceLevel = Field(
        default="technical", description="basic: Dễ hiểu; technical: Kỹ thuật. Mỗi mức có cache Gemini riêng, dùng chung SHAP.",
    )

    @field_validator("row_indices")
    @classmethod
    def unique_indices(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Danh sách chỉ số dòng không được lặp.")
        return values


class RunInfo(BaseModel):
    id: str
    filename: str
    mode: Literal["batch", "replay"]
    interval_seconds: float
    status: Literal["queued", "running", "paused", "stopped", "interrupted", "failed", "completed"]
    total_rows: int
    processed_rows: int
    created_at: str
    updated_at: str
    signature: str = Field(description="Dấu vân tay model/background/cấu hình của lần chạy.")
    message: str
    explanation_counts: dict[str, int] = Field(default_factory=dict)


class RunList(BaseModel):
    items: list[RunInfo]
    total: int


class RunDeleted(BaseModel):
    run_id: str
    files_deleted: bool
    message: str


DashboardPeriod = Literal["today", "7d", "30d", "all"]


class DashboardMetrics(BaseModel):
    predicted_rows: int
    normal_rows: int
    suspected_rows: int
    suspected_percentage: float | None = Field(description="null khi chưa có mẫu dự đoán.")
    pending_alerts: int
    shap_rows: int = Field(description="Mẫu có explanation.json dùng chung đã lưu; đếm một lần cho hai mức diễn giải.")
    run_count: int


class DashboardDay(BaseModel):
    date: str
    normal_rows: int
    suspected_rows: int
    total_rows: int


class DashboardRunOption(BaseModel):
    id: str
    filename: str
    created_at: str


class DashboardAlert(BaseModel):
    id: int
    run_id: str
    row_index: int
    status: AlertStatus
    created_at: str
    predicted_class: ClassName
    predicted_probability: float
    filename: str


class DashboardSummary(BaseModel):
    generated_at: str
    period: DashboardPeriod
    timezone: str
    start_date: str | None
    end_date: str
    trend_start_date: str
    trend_end_date: str
    audience_level: AudienceLevel
    selected_run: DashboardRunOption | None
    metrics: DashboardMetrics
    class_counts: dict[str, int]
    daily_activity: list[DashboardDay]
    alert_counts: dict[str, int]
    explanation_counts: dict[str, int]
    gemini_counts: dict[str, int]
    review_counts: dict[str, int]
    saved_reviews: int
    proposed_labels: int
    recent_runs: list[RunInfo]
    recent_alerts: list[DashboardAlert]
    run_options: list[DashboardRunOption]
    available_run_count: int


class PredictionInfo(BaseModel):
    run_id: str
    row_index: int
    predicted_class: str
    predicted_probability: float
    probabilities: dict[str, float]
    predict_seconds: float = Field(
        description="Replay: thời gian suy luận dòng. Batch: thời gian suy luận batch chia đều cho số dòng."
    )
    created_at: str
    explanation_status: ExplanationFilter = "not_requested"
    gemini_status: str = "not_requested"
    alert_id: int | None = None
    alert_status: AlertStatus | None = None


class PredictionList(BaseModel):
    items: list[PredictionInfo]
    total: int
    offset: int
    limit: int
    total_predicted: int = Field(description="Tổng dòng đã dự đoán, trước khi áp dụng bộ lọc; total là số dòng khớp bộ lọc.")
    audience_level: AudienceLevel = "technical"


class InputRow(BaseModel):
    run_id: str
    row_index: int
    features: dict[str, float | None] = Field(
        description="46 đặc trưng đúng thứ tự model, float32 trước tiền xử lý; giá trị thiếu là null. Không có nhãn thật."
    )


class ExplanationState(BaseModel):
    run_id: str
    row_index: int
    status: ExplanationStatus
    use_gemini: bool
    gemini_status: str
    message: str
    updated_at: str
    audience_level: AudienceLevel = "technical"


class ExplanationList(BaseModel):
    run_id: str
    items: list[ExplanationState]


class ExplanationPage(ExplanationList):
    total: int
    offset: int
    limit: int
    audience_level: AudienceLevel


class PlaybookSource(BaseModel):
    title: str
    url: str


class Playbook(BaseModel):
    class_name: ClassName
    title: str
    version: str
    checks: list[str]
    response_steps: list[str]
    sources: list[PlaybookSource]
    scope_note: str
    automatic_actions: bool = False


class ExplanationDetail(ExplanationState):
    explanation: dict | None = Field(default=None, description="Bằng chứng số SHAP do Python dựng.")
    gemini: dict | None = Field(default=None, description="Diễn giải đạt kiểm tra hoặc bản nháp có nhãn trạng thái.")
    files: dict[str, str] = Field(default_factory=dict)
    playbook: Playbook | None = None


class RunSummary(BaseModel):
    run_id: str
    prediction_status: str
    total_rows: int
    processed_rows: int
    pending_rows: int
    class_counts: dict[str, int]
    normal_rows: int
    suspected_attack_rows: int
    explanation_counts: dict[str, int]
    gemini_counts: dict[str, int]
    alert_counts: dict[str, int]
    audience_level: AudienceLevel
    human_semantic_review: str = "user_review_available"


class AlertUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: AlertStatus = Field(description="new → acknowledged → closed; closed → acknowledged để mở lại.")
    note: str | None = Field(default=None, max_length=2000, description="Ghi chú của người vận hành; bỏ qua để giữ ghi chú cũ.")


class HumanReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer_name: str = Field(min_length=1, max_length=128)
    prediction_assessment: Literal["not_reviewed", "agree", "disagree", "uncertain"] = "not_reviewed"
    proposed_label: ClassName | None = None
    explanation_clarity: Annotated[StrictInt, Field(ge=1, le=5)] | None = None
    evidence_faithfulness: Annotated[StrictInt, Field(ge=1, le=5)] | None = None
    actionability: Annotated[StrictInt, Field(ge=1, le=5)] | None = None
    notes: str = Field(default="", max_length=4000)
    evidence_signature: str = Field(pattern=r"^[a-f0-9]{64}$", description="Dấu vân tay bằng chứng đang được đánh giá, lấy từ GET human-review.")

    @field_validator("reviewer_name")
    @classmethod
    def reviewer_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Cần nhập tên người đánh giá.")
        return value.strip()


class AlertInfo(BaseModel):
    id: int
    run_id: str
    row_index: int
    predicted_class: ClassName
    predicted_probability: float
    status: AlertStatus
    note: str
    created_at: str
    updated_at: str
    explanation_status: ExplanationFilter = "not_requested"
    gemini_status: str = "not_requested"


class AlertPage(BaseModel):
    items: list[AlertInfo]
    total: int
    offset: int
    limit: int
    audience_level: AudienceLevel


class AlertEvent(BaseModel):
    id: int
    alert_id: int
    previous_status: AlertStatus | None
    status: AlertStatus
    note: str
    actor: str
    created_at: str


class AlertDetail(AlertInfo):
    history: list[AlertEvent]
    playbook: Playbook
    prediction: PredictionInfo
    explanation_url: str
    audience_level: AudienceLevel
    human_semantic_review: str = "user_review_available"


class ErrorResponse(BaseModel):
    detail: str | list
