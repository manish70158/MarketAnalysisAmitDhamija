"""
Historical Prediction Tracker
Stores predictions and enables accuracy measurement over time.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class PredictionTracker:
    """Track predictions and measure accuracy over time."""

    def __init__(self, db_file="prediction_history.json"):
        self.db_file = db_file
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load prediction history from JSON file."""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as f:
                return json.load(f)
        return {"predictions": [], "metadata": {"created": datetime.now().isoformat()}}

    def _save_history(self):
        """Save prediction history to JSON file."""
        with open(self.db_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_prediction(self, prediction_data: Dict):
        """
        Add a new prediction to history.

        Args:
            prediction_data: Dict containing date, market_view, confidence, etc.
        """
        # Check if prediction for this date already exists
        date_str = prediction_data.get("date")
        existing = next(
            (p for p in self.history["predictions"] if p["date"] == date_str), None
        )

        if existing:
            # Update existing prediction
            existing.update(prediction_data)
        else:
            # Add new prediction
            prediction_data["recorded_at"] = datetime.now().isoformat()
            self.history["predictions"].append(prediction_data)

        self._save_history()

    def update_actual_result(
        self, date_str: str, actual_movement: str, nifty_change_percent: float
    ):
        """
        Update prediction with actual market outcome.

        Args:
            date_str: Date in "DD MMM YYYY" format
            actual_movement: "BULLISH", "BEARISH", or "NEUTRAL"
            nifty_change_percent: Percentage change in NIFTY
        """
        prediction = next(
            (p for p in self.history["predictions"] if p["date"] == date_str), None
        )

        if prediction:
            prediction["actual_movement"] = actual_movement
            prediction["nifty_change_percent"] = nifty_change_percent
            prediction["is_correct"] = self._check_accuracy(
                prediction["market_view"], actual_movement
            )
            prediction["updated_at"] = datetime.now().isoformat()
            self._save_history()
            return True
        return False

    def _check_accuracy(self, predicted: str, actual: str) -> bool:
        """Check if prediction matches actual outcome."""
        # Strong predictions
        if "STRONG_BULLISH" in predicted:
            return "BULLISH" in actual
        if "STRONG_BEARISH" in predicted:
            return "BEARISH" in actual

        # Regular predictions
        if "BULLISH" in predicted:
            return "BULLISH" in actual or actual == "MILDLY_BULLISH"
        if "BEARISH" in predicted:
            return "BEARISH" in actual or actual == "MILDLY_BEARISH"

        # Neutral
        return actual == "NEUTRAL"

    def get_accuracy_stats(self, days: Optional[int] = None) -> Dict:
        """
        Calculate accuracy statistics.

        Args:
            days: Number of recent days to analyze (None = all)

        Returns:
            Dict with accuracy metrics
        """
        predictions = self.history["predictions"]

        # Filter to recent days if specified
        if days:
            predictions = predictions[-days:]

        # Filter to predictions with actual outcomes
        completed = [p for p in predictions if "actual_movement" in p]

        if not completed:
            return {
                "total_predictions": len(predictions),
                "completed_predictions": 0,
                "accuracy": 0,
                "by_confidence": {},
            }

        correct = sum(1 for p in completed if p.get("is_correct", False))
        total = len(completed)

        # Breakdown by confidence level
        by_confidence = {}
        for conf in ["HIGH", "MEDIUM", "LOW"]:
            conf_preds = [p for p in completed if p["confidence"] == conf]
            if conf_preds:
                conf_correct = sum(1 for p in conf_preds if p.get("is_correct", False))
                by_confidence[conf] = {
                    "total": len(conf_preds),
                    "correct": conf_correct,
                    "accuracy": conf_correct / len(conf_preds) * 100,
                }

        return {
            "total_predictions": len(predictions),
            "completed_predictions": total,
            "correct_predictions": correct,
            "accuracy": correct / total * 100 if total > 0 else 0,
            "by_confidence": by_confidence,
        }

    def generate_report(self, days: Optional[int] = 30) -> str:
        """Generate human-readable accuracy report."""
        stats = self.get_accuracy_stats(days)

        if stats["completed_predictions"] == 0:
            return "No completed predictions to analyze yet."

        lines = []
        lines.append("═" * 60)
        lines.append("📊 PREDICTION ACCURACY REPORT")
        lines.append("═" * 60)
        lines.append("")

        period = f"Last {days} days" if days else "All time"
        lines.append(f"📅 Period: {period}")
        lines.append(
            f"📈 Total Predictions: {stats['total_predictions']} "
            f"({stats['completed_predictions']} with outcomes)"
        )
        lines.append("")

        # Overall accuracy
        acc = stats["accuracy"]
        acc_emoji = "🎯" if acc >= 70 else "📊" if acc >= 50 else "⚠️"
        lines.append(f"{acc_emoji} Overall Accuracy: {acc:.1f}%")
        lines.append(
            f"   ✓ Correct: {stats['correct_predictions']} | "
            f"✗ Wrong: {stats['completed_predictions'] - stats['correct_predictions']}"
        )
        lines.append("")

        # By confidence
        if stats["by_confidence"]:
            lines.append("📋 Breakdown by Confidence:")
            for conf, data in stats["by_confidence"].items():
                conf_emoji = "🔥" if conf == "HIGH" else "⚡" if conf == "MEDIUM" else "💭"
                lines.append(
                    f"   {conf_emoji} {conf}: {data['accuracy']:.1f}% "
                    f"({data['correct']}/{data['total']})"
                )

        lines.append("")
        lines.append("═" * 60)

        return "\n".join(lines)

    def get_recent_predictions(self, count: int = 10) -> List[Dict]:
        """Get N most recent predictions."""
        return self.history["predictions"][-count:]


def main():
    """Test the tracker with current prediction."""
    tracker = PredictionTracker()

    # Load current prediction if it exists
    if os.path.exists("market_prediction.json"):
        with open("market_prediction.json", "r") as f:
            prediction = json.load(f)

        print("📝 Adding current prediction to history...")
        tracker.add_prediction(prediction)
        print(f"   ✓ Prediction for {prediction['date']} recorded")

        # Show stats
        print("\n" + tracker.generate_report(days=30))

    else:
        print("No prediction file found. Run predict_market_view.py first.")


if __name__ == "__main__":
    main()
