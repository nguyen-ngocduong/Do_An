# Bàn giao holdout blending 8 lớp

Model nguồn nhánh duong. Cài requirements_runtime.txt trên Python 3.13.
Chỉ load bundle đáng tin cậy do nhóm tạo; joblib thực thi Python khi load.

```python
import sys
from pathlib import Path
import pandas as pd
bundle = Path("/path/to/handoff")
sys.path.insert(0, str(bundle))
from blending_module import load_bundle
model = load_bundle(bundle)
frame = pd.read_csv(bundle / "example_raw_features.csv", float_precision="round_trip")
labels = model.predict_raw(frame)
probabilities = model.predict_proba_raw(frame)
Z = model.build_meta_features(frame)
```

CSV có đủ 44 feature đúng schema; extra columns bỏ qua, label không là đầu vào. Giữ Magnitue đúng chính tả schema. Input này là feature table, không phải PCAP.

Base dùng pilot 1M; preprocessing fit full source train; meta fit val sau mask. Val/test đã từng được xem. Điểm OOF là development, không phải xác nhận độc lập.

Kiên: demo cần bundle và mẫu query, không cần train/test. Đo RAM/latency trên máy triển khai.
Hải: LIME/CF raw 44 feature gọi model.predict_proba_raw cho MỌI query perturbation; meta-level 24 score là mức giải thích khác. Không giữ Z cũ khi thay raw query.
pipeline.joblib chứa cả hệ thống; base_models/ và meta_model.joblib là bản sao cho audit/XAI riêng.
