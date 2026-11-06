"""SHAP trên 46 đặc trưng gốc của toàn pipeline đã freeze."""

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from BE.config import MODEL_ID
from BE.utils import read_json, write_json


def explain_sample(runtime, sample, row_index, expected_probabilities, case_dir):
    cached_path = case_dir / "explanation.json"
    if cached_path.is_file():
        item = read_json(cached_path)
        np.testing.assert_allclose(
            list(item["probabilities"].values()), expected_probabilities, rtol=1e-6, atol=1e-7
        )
        if all((case_dir / name).is_file() for name in ["shap_values.npz", "waterfall.png", "top5_features.csv"]):
            return item

    case_dir.mkdir(parents=True, exist_ok=True)
    background = runtime.background
    protocol = runtime.shap_protocol
    seed = protocol["random_state"] + row_index

    def predict_probabilities(values):
        return runtime.predict(np.asarray(values, dtype=np.float32)).astype(np.float64)

    def exact_feature_matches(row):
        # Giữ cách so sánh chính xác của notebook, kể cả giá trị thiếu.
        same_values = background == row
        both_missing = np.isnan(background) & np.isnan(row)
        return same_values | both_missing

    started = time.perf_counter()
    masker = shap.maskers.Independent(background, max_samples=protocol["background_size"])
    masker.invariants = exact_feature_matches
    explainer = shap.PermutationExplainer(
        predict_probabilities, masker, feature_names=runtime.feature_names,
        link=shap.links.identity, seed=seed,
    )
    explanation = explainer(
        sample, max_evals=protocol["max_evals"],
        batch_size=runtime.settings.prediction_batch_size, silent=True,
    )
    if explanation.values.shape != (1, len(runtime.feature_names), len(runtime.class_names)):
        raise ValueError("SHAP sai kích thước đặc trưng/lớp.")
    if explanation.base_values.shape != (1, len(runtime.class_names)):
        raise ValueError("SHAP thiếu xác suất nền của tám lớp.")
    if not np.isfinite(explanation.values).all() or not np.isfinite(explanation.base_values).all():
        raise ValueError("SHAP sinh NaN/Inf.")
    probabilities = predict_probabilities(sample)[0]
    reconstructed = explanation.base_values[0] + explanation.values[0].sum(axis=0)
    tolerance = protocol["additivity_tolerance"]
    np.testing.assert_allclose(reconstructed, probabilities, rtol=0, atol=tolerance)
    np.testing.assert_allclose(explanation.base_values[0], runtime.background_probabilities, rtol=0, atol=tolerance)
    np.testing.assert_allclose(probabilities, expected_probabilities, rtol=1e-6, atol=1e-7)

    predicted_id = int(probabilities.argmax())
    contributions = explanation.values[0]
    base_values = explanation.base_values[0]
    class_contributions = contributions[:, predicted_id]
    indices = np.argsort(-np.abs(class_contributions), kind="stable")[:5]
    top_features = []
    for rank, index in enumerate(indices, start=1):
        value = float(sample[0, index])
        shap_value = float(class_contributions[index])
        direction = "increase" if shap_value > 0 else "decrease" if shap_value < 0 else "no_change"
        top_features.append({
            "rank": rank, "feature": runtime.feature_names[index],
            "value": None if np.isnan(value) else value, "missing": bool(np.isnan(value)),
            "shap_value": shap_value, "impact_percentage_points": 100 * shap_value,
            "direction": direction,
        })
    item = {
        "case_id": f"row_{row_index:04d}", "input_row_index": row_index, "model_id": MODEL_ID,
        "predicted_class": runtime.class_names[predicted_id],
        "predicted_probability": float(probabilities[predicted_id]),
        "probabilities": {name: float(probabilities[i]) for i, name in enumerate(runtime.class_names)},
        "explained_class": runtime.class_names[predicted_id], "output_unit": "probability",
        "base_probability": float(base_values[predicted_id]),
        "shap_sum": float(class_contributions.sum()),
        "other_features_shap_sum": float(class_contributions.sum() - class_contributions[indices].sum()),
        "top_features": top_features,
        "max_additivity_error_all_classes": float(np.abs(reconstructed - probabilities).max()),
        "shap_seconds": time.perf_counter() - started, "seed": seed,
    }
    np.savez_compressed(
        case_dir / "shap_values.npz", values=contributions, base_values=base_values,
        input_values=sample[0], probabilities=probabilities,
        feature_names=np.asarray(runtime.feature_names), class_names=np.asarray(runtime.class_names),
    )
    pd.DataFrame(top_features).to_csv(case_dir / "top5_features.csv", index=False)
    try:
        local_explanation = shap.Explanation(
            values=class_contributions, base_values=base_values[predicted_id],
            data=sample[0], feature_names=runtime.feature_names,
        )
        shap.plots.waterfall(local_explanation, max_display=6, show=False)
        plt.title(f"Dòng {row_index} — {item['predicted_class']}")
        plt.tight_layout()
        plt.savefig(case_dir / "waterfall.png", dpi=140, bbox_inches="tight")
    finally:
        plt.close("all")
    # Ghi JSON cuối cùng, sau khi đã có đủ file cần cho cache.
    write_json(cached_path, item)
    return item
