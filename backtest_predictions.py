"""
Backtesting Framework for Market Predictions
Validates prediction accuracy against historical NIFTY movements.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests


class NiftyDataFetcher:
    """Fetch historical NIFTY data from NSE or alternative sources."""

    def __init__(self):
        self.cache_file = "nifty_historical_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cached NIFTY data."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save NIFTY data cache."""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def get_nifty_close(self, date_str: str) -> Optional[float]:
        """
        Get NIFTY closing price for a date.

        Args:
            date_str: Date in "DDMMYYYY" format

        Returns:
            Closing price or None if not available
        """
        # Check cache first
        if date_str in self.cache:
            return self.cache[date_str].get("close")

        # Try to fetch from NSE (simplified - in production use proper API)
        try:
            # Note: NSE historical data requires proper session/cookies
            # For backtesting, you may need to manually populate the cache
            # or use alternative data sources like Yahoo Finance
            return None
        except Exception:
            return None

    def add_manual_entry(self, date_str: str, open_price: float, close_price: float):
        """Manually add NIFTY data (for backtesting setup)."""
        self.cache[date_str] = {
            "open": open_price,
            "close": close_price,
            "change": close_price - open_price,
            "change_percent": (close_price - open_price) / open_price * 100,
        }
        self._save_cache()

    def calculate_next_day_movement(
        self, date_str: str
    ) -> Optional[Dict]:
        """
        Calculate next trading day movement.

        Returns:
            Dict with movement, change_percent, or None
        """
        # Parse date
        dt = datetime.strptime(date_str, "%d%m%Y")

        # Try next few days (to handle weekends/holidays)
        for i in range(1, 10):
            next_date = dt + timedelta(days=i)
            next_date_str = next_date.strftime("%d%m%Y")

            if next_date_str in self.cache:
                data = self.cache[next_date_str]
                change_percent = data["change_percent"]

                # Classify movement
                if change_percent > 0.5:
                    movement = "BULLISH"
                elif change_percent < -0.5:
                    movement = "BEARISH"
                else:
                    movement = "NEUTRAL"

                return {
                    "date": next_date_str,
                    "movement": movement,
                    "change_percent": change_percent,
                    "close": data["close"],
                }

        return None


class PredictionBacktester:
    """Backtest prediction accuracy against actual market movements."""

    def __init__(self):
        self.nifty_fetcher = NiftyDataFetcher()

    def run_backtest(
        self, prediction_history_file: str = "prediction_history.json"
    ) -> Dict:
        """
        Run backtest on historical predictions.

        Returns:
            Dict with backtest results and metrics
        """
        # Load prediction history
        if not os.path.exists(prediction_history_file):
            return {
                "error": "No prediction history found",
                "predictions_count": 0,
            }

        with open(prediction_history_file, "r") as f:
            history = json.load(f)

        predictions = history.get("predictions", [])
        if not predictions:
            return {"error": "No predictions to backtest", "predictions_count": 0}

        # Process each prediction
        results = []
        for pred in predictions:
            # Convert date format "DD MMM YYYY" to "DDMMYYYY"
            date_str = datetime.strptime(pred["date"], "%d %b %Y").strftime("%d%m%Y")

            # Get actual next-day movement
            actual = self.nifty_fetcher.calculate_next_day_movement(date_str)

            if actual:
                is_correct = self._check_prediction(
                    pred["market_view"], actual["movement"]
                )

                results.append(
                    {
                        "date": pred["date"],
                        "predicted": pred["market_view"],
                        "actual": actual["movement"],
                        "confidence": pred["confidence"],
                        "is_correct": is_correct,
                        "nifty_change": actual["change_percent"],
                    }
                )

        # Calculate metrics
        metrics = self._calculate_metrics(results)

        return {
            "total_predictions": len(predictions),
            "backtested_predictions": len(results),
            "results": results,
            "metrics": metrics,
        }

    def _check_prediction(self, predicted: str, actual: str) -> bool:
        """Check if prediction matches actual movement."""
        # Strong predictions
        if "STRONG_BULLISH" in predicted:
            return actual == "BULLISH"
        if "STRONG_BEARISH" in predicted:
            return actual == "BEARISH"

        # Regular predictions
        if "BULLISH" in predicted:
            return actual == "BULLISH"
        if "BEARISH" in predicted:
            return actual == "BEARISH"

        # Neutral
        return actual == "NEUTRAL"

    def _calculate_metrics(self, results: List[Dict]) -> Dict:
        """Calculate backtest performance metrics."""
        if not results:
            return {}

        total = len(results)
        correct = sum(1 for r in results if r["is_correct"])
        accuracy = correct / total * 100

        # By confidence
        by_confidence = {}
        for conf in ["HIGH", "MEDIUM", "LOW"]:
            conf_results = [r for r in results if r["confidence"] == conf]
            if conf_results:
                conf_correct = sum(1 for r in conf_results if r["is_correct"])
                by_confidence[conf] = {
                    "total": len(conf_results),
                    "correct": conf_correct,
                    "accuracy": conf_correct / len(conf_results) * 100,
                }

        # Average NIFTY change when predicted correctly
        correct_results = [r for r in results if r["is_correct"]]
        avg_correct_change = (
            sum(abs(r["nifty_change"]) for r in correct_results) / len(correct_results)
            if correct_results
            else 0
        )

        return {
            "total": total,
            "correct": correct,
            "wrong": total - correct,
            "accuracy": accuracy,
            "by_confidence": by_confidence,
            "avg_nifty_change_when_correct": avg_correct_change,
        }

    def generate_report(self, backtest_results: Dict) -> str:
        """Generate human-readable backtest report."""
        if "error" in backtest_results:
            return f"❌ Backtest Error: {backtest_results['error']}"

        metrics = backtest_results.get("metrics", {})
        if not metrics:
            return "No backtest data available."

        lines = []
        lines.append("═" * 60)
        lines.append("📊 PREDICTION BACKTEST REPORT")
        lines.append("═" * 60)
        lines.append("")

        # Overall stats
        lines.append(
            f"📈 Total Predictions: {backtest_results['total_predictions']}"
        )
        lines.append(
            f"✓ Backtested: {backtest_results['backtested_predictions']} "
            f"(with actual NIFTY data)"
        )
        lines.append("")

        # Accuracy
        acc = metrics["accuracy"]
        acc_emoji = "🎯" if acc >= 70 else "📊" if acc >= 50 else "⚠️"
        lines.append(f"{acc_emoji} Overall Accuracy: {acc:.1f}%")
        lines.append(
            f"   ✓ Correct: {metrics['correct']} | ✗ Wrong: {metrics['wrong']}"
        )
        lines.append(
            f"   📈 Avg NIFTY move when correct: {metrics['avg_nifty_change_when_correct']:.2f}%"
        )
        lines.append("")

        # By confidence
        if metrics.get("by_confidence"):
            lines.append("📋 Accuracy by Confidence Level:")
            for conf, data in metrics["by_confidence"].items():
                conf_emoji = "🔥" if conf == "HIGH" else "⚡" if conf == "MEDIUM" else "💭"
                lines.append(
                    f"   {conf_emoji} {conf}: {data['accuracy']:.1f}% "
                    f"({data['correct']}/{data['total']})"
                )
            lines.append("")

        # Recent results
        recent = backtest_results["results"][-10:]
        lines.append("📅 Last 10 Predictions:")
        for r in recent:
            status = "✓" if r["is_correct"] else "✗"
            lines.append(
                f"   {status} {r['date']}: {r['predicted']} → {r['actual']} "
                f"({r['nifty_change']:+.2f}%)"
            )

        lines.append("")
        lines.append("═" * 60)

        return "\n".join(lines)


def main():
    """Run backtest and generate report."""
    print("📊 Running Prediction Backtest...")
    print("─" * 40)

    backtester = PredictionBacktester()

    # Check if we have NIFTY data
    if not os.path.exists("nifty_historical_cache.json"):
        print("⚠️  No NIFTY historical data found.")
        print("   To run backtest, you need to populate NIFTY data:")
        print("   1. Use backtest_predictions.NiftyDataFetcher()")
        print("   2. Call add_manual_entry(date, open, close) for each date")
        print("   3. Or integrate with Yahoo Finance / NSE API")
        return

    # Run backtest
    results = backtester.run_backtest()

    # Generate and display report
    report = backtester.generate_report(results)
    print("\n" + report)

    # Save detailed results
    with open("backtest_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n✓ Detailed results saved to backtest_results.json")


if __name__ == "__main__":
    main()
