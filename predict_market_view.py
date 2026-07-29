"""
NSE Participant OI Market Prediction System
Analyzes participant positioning to predict next-day NIFTY market view.

Core Logic:
- Contrarian indicator: Clients (retail traders) - invert their stance
- Smart money: FII + Pro (follow their direction)
- Primary signal: Index Futures net buy/sell
- Secondary: Index Options (Calls/Puts) for confirmation
"""

import glob
import json
import os
from datetime import datetime, timedelta


class ParticipantDataExtractor:
    """Extract participant data from cached CSV files."""

    def get_latest_three_days(self):
        """
        Find last 3 trading day CSV files.
        Returns: [(date_str, data_dict), ...] sorted newest to oldest
        """
        csv_files = glob.glob("participant_oi_*.csv")
        if len(csv_files) < 2:
            raise FileNotFoundError(
                f"Need at least 2 CSV files for comparison, found {len(csv_files)}"
            )

        # Sort by date in filename (DDMMYYYY format)
        def extract_date(filename):
            # Extract DDMMYYYY from filename like "participant_oi_24072026.csv"
            date_str = filename.split("_")[-1].replace(".csv", "")
            return datetime.strptime(date_str, "%d%m%Y")

        csv_files.sort(key=extract_date, reverse=True)

        # Get latest 3 files (or at least 2)
        needed_files = csv_files[:min(3, len(csv_files))]

        results = []
        for csv_file in needed_files:
            date_str = csv_file.split("_")[-1].replace(".csv", "")
            data = self.parse_nse_csv(csv_file)
            results.append((date_str, data))

        return results

    def parse_nse_csv(self, csv_file):
        """
        Parse CSV to extract participant data.
        Returns: {
            'Client': {'fut_idx_long': X, 'fut_idx_short': X, ...},
            'DII': {...}, 'FII': {...}, 'Pro': {...}
        }
        """
        with open(csv_file, "r") as f:
            lines = f.readlines()

        data = {}
        for line in lines[2:7]:  # Rows 3-6 (skip title and header, include TOTAL)
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) < 14:
                continue

            participant = parts[0].strip()
            if participant in ("Client", "DII", "FII", "Pro"):
                data[participant] = {
                    "fut_idx_long": int(parts[1]),
                    "fut_idx_short": int(parts[2]),
                    "fut_stk_long": int(parts[3]),
                    "fut_stk_short": int(parts[4].strip()),
                    "opt_idx_call_long": int(parts[5]),
                    "opt_idx_put_long": int(parts[6]),
                    "opt_idx_call_short": int(parts[7]),
                    "opt_idx_put_short": int(parts[8]),
                    "opt_stk_call_long": int(parts[9]) if len(parts) > 9 else 0,
                    "opt_stk_put_long": int(parts[10]) if len(parts) > 10 else 0,
                    "opt_stk_call_short": int(parts[11]) if len(parts) > 11 else 0,
                    "opt_stk_put_short": int(parts[12]) if len(parts) > 12 else 0,
                }

        return data


class SignalClassifier:
    """Classify participant stance as BULLISH/BEARISH/NEUTRAL."""

    # Thresholds
    NEUTRAL_THRESHOLD = 5000  # Below this = NEUTRAL
    HIGH_MAGNITUDE = 30000  # Above this = weight 1.0
    MEDIUM_MAGNITUDE = 15000  # 15k-30k = weight 0.5-1.0

    def classify_participant_advanced(
        self, today_data, yesterday_data, participant
    ):
        """
        Advanced classification including Stock Futures/Options.

        Returns extended classification with stock derivatives analysis.
        """
        # Get basic classification
        basic = self.classify_participant(today_data, yesterday_data, participant)

        # Add Stock Futures/Options analysis if data is available
        t = today_data[participant]
        y = yesterday_data[participant]

        # Check if stock derivative data exists
        has_stock_data = all(
            key in t
            for key in [
                "fut_stk_long",
                "fut_stk_short",
                "opt_stk_call_long",
                "opt_stk_call_short",
                "opt_stk_put_long",
                "opt_stk_put_short",
            ]
        )

        if has_stock_data:
            # Stock Futures
            stk_fut_long_chg = t["fut_stk_long"] - y["fut_stk_long"]
            stk_fut_short_chg = t["fut_stk_short"] - y["fut_stk_short"]
            stk_fut_net = stk_fut_long_chg - stk_fut_short_chg

            # Stock Options
            stk_call_long_chg = t.get("opt_stk_call_long", 0) - y.get(
                "opt_stk_call_long", 0
            )
            stk_call_short_chg = t.get("opt_stk_call_short", 0) - y.get(
                "opt_stk_call_short", 0
            )
            stk_call_net = stk_call_long_chg - stk_call_short_chg

            stk_put_long_chg = t.get("opt_stk_put_long", 0) - y.get(
                "opt_stk_put_long", 0
            )
            stk_put_short_chg = t.get("opt_stk_put_short", 0) - y.get(
                "opt_stk_put_short", 0
            )
            stk_put_net = stk_put_long_chg - stk_put_short_chg

            stk_options_net = stk_call_net - stk_put_net

            # Determine stock derivatives stance
            stk_total_net = stk_fut_net + stk_options_net
            if abs(stk_total_net) < self.NEUTRAL_THRESHOLD:
                stk_stance = "NEUTRAL"
            elif stk_total_net > 0:
                stk_stance = "BULLISH"
            else:
                stk_stance = "BEARISH"

            # Add to basic classification
            basic["stock_derivatives"] = {
                "fut_net": int(stk_fut_net),
                "options_net": int(stk_options_net),
                "total_net": int(stk_total_net),
                "stance": stk_stance,
            }
        else:
            # Stock data not available
            basic["stock_derivatives"] = {
                "fut_net": 0,
                "options_net": 0,
                "total_net": 0,
                "stance": "UNAVAILABLE",
            }

        return basic

    def classify_participant(self, today_data, yesterday_data, participant):
        """
        Classify participant stance based on Index Futures and Options.

        Primary: Index Futures Net = (Long Change - Short Change)
        Secondary: Index Options Net (Calls bullish, Puts bearish)

        Returns: {
            'stance': 'BULLISH'/'BEARISH'/'NEUTRAL',
            'fut_net': int,
            'options_net': int,
            'magnitude': int,
            'weight': float,
            'options_confirm': bool
        }
        """
        t = today_data[participant]
        y = yesterday_data[participant]

        # Calculate Index Futures changes
        fut_long_chg = t["fut_idx_long"] - y["fut_idx_long"]
        fut_short_chg = t["fut_idx_short"] - y["fut_idx_short"]
        fut_net = fut_long_chg - fut_short_chg

        # Calculate Index Options changes
        # Calls: Buying calls = bullish, Selling calls = bearish
        call_long_chg = t["opt_idx_call_long"] - y["opt_idx_call_long"]
        call_short_chg = t["opt_idx_call_short"] - y["opt_idx_call_short"]
        call_net = call_long_chg - call_short_chg

        # Puts: Buying puts = bearish, Selling puts = bullish
        put_long_chg = t["opt_idx_put_long"] - y["opt_idx_put_long"]
        put_short_chg = t["opt_idx_put_short"] - y["opt_idx_put_short"]
        put_net = put_long_chg - put_short_chg

        # Options net: Positive call net + negative put net = bullish
        options_net = call_net - put_net

        # Primary classification based on Futures
        magnitude = abs(fut_net)
        if magnitude < self.NEUTRAL_THRESHOLD:
            stance = "NEUTRAL"
        elif fut_net > 0:
            stance = "BULLISH"
        else:
            stance = "BEARISH"

        # Weight based on magnitude
        if magnitude >= self.HIGH_MAGNITUDE:
            weight = 1.0
        elif magnitude >= self.MEDIUM_MAGNITUDE:
            weight = 0.5 + (magnitude - self.MEDIUM_MAGNITUDE) / (
                self.HIGH_MAGNITUDE - self.MEDIUM_MAGNITUDE
            ) * 0.5
        else:
            weight = magnitude / self.MEDIUM_MAGNITUDE * 0.5

        # Check if options confirm futures direction
        options_confirm = False
        if stance == "BULLISH" and options_net > 0:
            options_confirm = True
        elif stance == "BEARISH" and options_net < 0:
            options_confirm = True
        elif stance == "NEUTRAL":
            options_confirm = abs(options_net) < self.NEUTRAL_THRESHOLD

        return {
            "stance": stance,
            "fut_net": int(fut_net),
            "options_net": int(options_net),
            "magnitude": int(magnitude),
            "weight": round(weight, 2),
            "options_confirm": options_confirm,
        }


class MarketViewPredictor:
    """Apply decision tree rules to predict market view."""

    def predict(self, client, fii, pro, dii, trend_data=None):
        """
        Apply contrarian + smart money logic.

        Rules:
        1. Invert Client stance (contrarian indicator)
        2. Check alignment with FII and Pro (smart money)
        3. Calculate confidence based on magnitude and confirmation

        Returns: (view, confidence, key_factors, reasoning)
        """
        # Invert Client stance (contrarian)
        client_contrarian = self._invert_stance(client["stance"])

        # Collect stances
        stances = {
            "Client (Contrarian)": client_contrarian,
            "FII": fii["stance"],
            "Pro": pro["stance"],
            "DII": dii["stance"],
        }

        # Decision tree logic
        view = self._determine_view(client_contrarian, fii["stance"], pro["stance"])

        # Calculate confidence
        confidence = self._calculate_confidence(
            client, fii, pro, dii, view, trend_data
        )

        # Generate key factors
        key_factors = self._generate_key_factors(
            client, fii, pro, dii, client_contrarian, view
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            client, fii, pro, dii, client_contrarian, view, confidence
        )

        return view, confidence, key_factors, reasoning

    def _invert_stance(self, stance):
        """Invert stance for contrarian indicator."""
        if stance == "BULLISH":
            return "BEARISH"
        elif stance == "BEARISH":
            return "BULLISH"
        else:
            return "NEUTRAL"

    def _determine_view(self, client_contrarian, fii_stance, pro_stance):
        """
        Determine market view based on alignment.

        Strong signals: Client contrarian + both FII and Pro aligned
        Moderate: Client contrarian + one of FII/Pro aligned
        Mild: Only FII and Pro aligned (no contrarian)
        Neutral: Mixed or all neutral
        """
        # Count bullish and bearish signals
        bullish_count = sum(
            1 for s in [client_contrarian, fii_stance, pro_stance] if s == "BULLISH"
        )
        bearish_count = sum(
            1 for s in [client_contrarian, fii_stance, pro_stance] if s == "BEARISH"
        )

        # Strong signals: All 3 aligned
        if bullish_count == 3:
            return "STRONG_BULLISH"
        if bearish_count == 3:
            return "STRONG_BEARISH"

        # Moderate signals: 2 out of 3 aligned (including contrarian)
        if bullish_count == 2 and client_contrarian == "BULLISH":
            return "BULLISH"
        if bearish_count == 2 and client_contrarian == "BEARISH":
            return "BEARISH"

        # Mild signals: FII and Pro aligned, but no strong contrarian
        if fii_stance == pro_stance == "BULLISH":
            return "MILDLY_BULLISH"
        if fii_stance == pro_stance == "BEARISH":
            return "MILDLY_BEARISH"

        # Mixed or neutral
        return "NEUTRAL"

    def _calculate_confidence(self, client, fii, pro, dii, view, trend_data):
        """
        Calculate confidence: HIGH/MEDIUM/LOW

        HIGH: Large magnitude (>25k avg), options confirm, strong alignment
        MEDIUM: Moderate magnitude or partial confirmation
        LOW: Weak signals or conflicting data
        """
        # Average magnitude of smart money (FII + Pro)
        avg_magnitude = (fii["magnitude"] + pro["magnitude"]) / 2

        # Options confirmation
        options_confirm_count = sum(
            1 for p in [client, fii, pro] if p["options_confirm"]
        )

        # Check for strong alignment
        if "STRONG" in view:
            alignment_score = 3
        elif view in ["BULLISH", "BEARISH"]:
            alignment_score = 2
        elif "MILDLY" in view:
            alignment_score = 1
        else:
            alignment_score = 0

        # Calculate confidence
        if (
            avg_magnitude > 25000
            and options_confirm_count >= 2
            and alignment_score >= 2
        ):
            return "HIGH"
        elif avg_magnitude > 15000 and (
            options_confirm_count >= 1 or alignment_score >= 1
        ):
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_key_factors(self, client, fii, pro, dii, client_contrarian, view):
        """Generate list of key factors driving the prediction."""
        factors = []

        # Client positioning
        if client["magnitude"] > 20000:
            direction = "bearish" if client["stance"] == "BEARISH" else "bullish"
            factors.append(
                f"Clients heavily {direction} ({client['fut_net']:+,} contracts) → Strong contrarian {client_contrarian.lower()} signal"
            )

        # FII positioning
        if fii["magnitude"] > 15000:
            direction = "bullish" if fii["stance"] == "BULLISH" else "bearish"
            confirm = " with options confirmation" if fii["options_confirm"] else ""
            factors.append(
                f"FII strongly {direction} ({fii['fut_net']:+,} contracts){confirm}"
            )

        # Pro positioning
        if pro["magnitude"] > 15000:
            direction = "bullish" if pro["stance"] == "BULLISH" else "bearish"
            confirm = " with options confirmation" if pro["options_confirm"] else ""
            factors.append(
                f"Pro strongly {direction} ({pro['fut_net']:+,} contracts){confirm}"
            )

        # Combined smart money
        smart_money_net = fii["fut_net"] + pro["fut_net"]
        if abs(smart_money_net) > 40000:
            factors.append(
                f"Combined smart money (FII+Pro): {smart_money_net:+,} contracts (very high)"
            )

        # DII positioning (if significant)
        if dii["magnitude"] > 10000:
            direction = "bullish" if dii["stance"] == "BULLISH" else "bearish"
            factors.append(f"DII {direction} ({dii['fut_net']:+,} contracts)")

        return factors

    def _generate_reasoning(
        self, client, fii, pro, dii, client_contrarian, view, confidence
    ):
        """Generate human-readable reasoning for the prediction."""
        reasoning_parts = []

        # Main thesis
        if "STRONG" in view:
            reasoning_parts.append(
                f"{view.replace('_', ' ').title()} view based on strong alignment between contrarian Client positioning and smart money (FII+Pro)."
            )
        elif view in ["BULLISH", "BEARISH"]:
            reasoning_parts.append(
                f"{view.title()} view with partial alignment between contrarian Client signal and institutional money."
            )
        elif "MILDLY" in view:
            reasoning_parts.append(
                f"{view.replace('_', ' ').title()} view primarily driven by FII and Pro alignment, with weak contrarian signal."
            )
        else:
            reasoning_parts.append(
                "Neutral view due to mixed signals or lack of clear directional positioning."
            )

        # Add confidence context
        if confidence == "HIGH":
            reasoning_parts.append(
                "High conviction setup with large positions and confirmation across multiple indicators."
            )
        elif confidence == "MEDIUM":
            reasoning_parts.append(
                "Moderate conviction with reasonable position sizes but limited confirmation."
            )
        else:
            reasoning_parts.append(
                "Low conviction due to weak signals or conflicting data points."
            )

        return " ".join(reasoning_parts)


class PredictionOutputGenerator:
    """Generate JSON and text outputs."""

    def generate_json(
        self, date_str, market_view, confidence, participants, key_factors, reasoning
    ):
        """Generate JSON output."""
        output = {
            "date": self._format_date(date_str),
            "market_view": market_view,
            "confidence": confidence,
            "participants": participants,
            "key_factors": key_factors,
            "reasoning": reasoning,
        }
        return output

    def generate_text(
        self, date_str, market_view, confidence, participants, key_factors, reasoning
    ):
        """Generate formatted text summary."""
        lines = []

        # Header
        lines.append("═" * 63)
        lines.append(f"📊 NIFTY MARKET VIEW PREDICTION - {self._format_date(date_str)}")
        lines.append("═" * 63)
        lines.append("")

        # Market view and confidence
        view_emoji = self._get_view_emoji(market_view)
        lines.append(f"🎯 MARKET VIEW: {view_emoji} {market_view.replace('_', ' ')}")
        conf_emoji = "🔥" if confidence == "HIGH" else "⚡" if confidence == "MEDIUM" else "💭"
        lines.append(f"📈 CONFIDENCE: {conf_emoji} {confidence}")
        lines.append("")

        # Participant breakdown
        lines.append("📋 PARTICIPANT BREAKDOWN:")
        lines.append("")

        # Client (with contrarian signal)
        c = participants["Client"]
        lines.append("🔴 CLIENTS (Retail - Contrarian):")
        lines.append(
            f"   • Index Futures: {self._format_net_action(c['fut_net'])} → {c['stance']}"
        )
        lines.append(f"   • Contrarian Signal: {c['contrarian_view']} ✓")
        lines.append(f"   • Magnitude: {self._describe_magnitude(c['magnitude'])}")
        if c.get("options_confirm"):
            lines.append("   • Options confirm futures direction ✓")
        lines.append("")

        # FII
        f = participants["FII"]
        lines.append(f"🟢 FII: {self._format_net_action(f['fut_net'])} → {f['stance']}")
        if f.get("options_confirm"):
            lines.append("   • Options confirm futures direction ✓")
        lines.append(f"   • Magnitude: {self._describe_magnitude(f['magnitude'])}")
        lines.append("")

        # Pro
        p = participants["Pro"]
        lines.append(f"🟢 PRO: {self._format_net_action(p['fut_net'])} → {p['stance']}")
        if p.get("options_confirm"):
            lines.append("   • Options confirm futures direction ✓")
        lines.append(f"   • Magnitude: {self._describe_magnitude(p['magnitude'])}")
        lines.append("")

        # DII
        d = participants["DII"]
        lines.append(f"🔵 DII: {self._format_net_action(d['fut_net'])} → {d['stance']}")
        lines.append(f"   • Magnitude: {self._describe_magnitude(d['magnitude'])}")
        lines.append("")

        # Key factors
        lines.append("✅ KEY FACTORS:")
        for i, factor in enumerate(key_factors, 1):
            lines.append(f"{i}. {factor}")
        lines.append("")

        # Interpretation
        lines.append("💡 INTERPRETATION:")
        lines.append(reasoning)
        lines.append("")

        # Disclaimer
        lines.append("⚠️ DISCLAIMER: Educational purposes only. Not investment advice.")
        lines.append("═" * 63)

        return "\n".join(lines)

    def _format_date(self, date_str):
        """Format date string from DDMMYYYY to DD MMM YYYY."""
        dt = datetime.strptime(date_str, "%d%m%Y")
        return dt.strftime("%d %b %Y").upper()

    def _get_view_emoji(self, view):
        """Get emoji for market view."""
        if "BULLISH" in view:
            return "🚀" if "STRONG" in view else "📈"
        elif "BEARISH" in view:
            return "🔻" if "STRONG" in view else "📉"
        else:
            return "➡️"

    def _format_net_action(self, net):
        """Format net position as action."""
        if net > 0:
            return f"Bought Net {net:,}"
        elif net < 0:
            return f"Sold Net {abs(net):,}"
        else:
            return "No Change"

    def _describe_magnitude(self, magnitude):
        """Describe magnitude in words."""
        if magnitude > 30000:
            return f"Very Strong ({magnitude:,})"
        elif magnitude > 20000:
            return f"Strong ({magnitude:,})"
        elif magnitude > 10000:
            return f"Moderate ({magnitude:,})"
        else:
            return f"Weak ({magnitude:,})"

    def generate_high_confidence_alert(
        self, date_str, market_view, key_factors
    ):
        """Generate concise high-confidence alert for Telegram."""
        lines = []

        # Eye-catching header
        lines.append("🔥" * 20)
        lines.append("🚨 HIGH CONFIDENCE SETUP DETECTED 🚨")
        lines.append("🔥" * 20)
        lines.append("")

        # View
        view_emoji = self._get_view_emoji(market_view)
        lines.append(f"📅 Date: {self._format_date(date_str)}")
        lines.append(
            f"🎯 Market View: {view_emoji} {market_view.replace('_', ' ').upper()}"
        )
        lines.append(f"🔥 Confidence: HIGH")
        lines.append("")

        # Top factors
        lines.append("⚡ KEY REASONS:")
        for i, factor in enumerate(key_factors[:5], 1):  # Top 5 factors
            lines.append(f"{i}. {factor}")
        lines.append("")

        # Call to action
        lines.append("💼 ACTION RECOMMENDED:")
        if "BULLISH" in market_view:
            lines.append("Consider bullish strategies for next trading session")
        elif "BEARISH" in market_view:
            lines.append("Consider bearish strategies for next trading session")
        lines.append("")

        lines.append("⚠️ Disclaimer: Educational only. Trade at your own risk.")
        lines.append("🔥" * 20)

        return "\n".join(lines)


def create_fallback_message():
    """Generate neutral message if prediction fails."""
    with open("market_prediction.txt", "w") as f:
        f.write(
            "═" * 63 + "\n"
            "📊 NIFTY MARKET VIEW PREDICTION\n"
            "═" * 63 + "\n\n"
            "⚠️ Market prediction unavailable today.\n"
            "Please analyze the data manually.\n\n"
            "═" * 63 + "\n"
        )


def main():
    """Main execution function."""
    try:
        print("🔍 NSE Market Prediction Engine")
        print("─" * 40)

        # Extract data
        print("📂 Extracting participant data...")
        extractor = ParticipantDataExtractor()
        dates = extractor.get_latest_three_days()

        if len(dates) < 2:
            raise ValueError(f"Need at least 2 trading days, found {len(dates)}")

        today_date, today_data = dates[0]
        day1_date, day1_data = dates[1]

        print(f"   Today:     {today_date}")
        print(f"   Yesterday: {day1_date}")

        # Classify participants with advanced signals
        print("\n🧮 Classifying participant stances (with advanced signals)...")
        classifier = SignalClassifier()

        classifications = {}
        for participant in ["Client", "DII", "FII", "Pro"]:
            classifications[participant] = classifier.classify_participant_advanced(
                today_data, day1_data, participant
            )
            print(
                f"   {participant:6s}: Index={classifications[participant]['stance']:8s} "
                f"(net: {classifications[participant]['fut_net']:+7,}), "
                f"Stock={classifications[participant]['stock_derivatives']['stance']:8s}"
            )

        # Predict market view
        print("\n🎯 Predicting market view...")
        predictor = MarketViewPredictor()
        market_view, confidence, key_factors, reasoning = predictor.predict(
            classifications["Client"],
            classifications["FII"],
            classifications["Pro"],
            classifications["DII"],
        )

        print(f"   View:       {market_view}")
        print(f"   Confidence: {confidence}")

        # Prepare participant data for output (with contrarian view for Client)
        participants_output = {}
        for p in ["Client", "DII", "FII", "Pro"]:
            participants_output[p] = {
                "stance": classifications[p]["stance"],
                "fut_net": classifications[p]["fut_net"],
                "options_net": classifications[p]["options_net"],
                "magnitude": classifications[p]["magnitude"],
                "weight": classifications[p]["weight"],
                "options_confirm": classifications[p]["options_confirm"],
            }
            # Add contrarian view for Client
            if p == "Client":
                if classifications[p]["stance"] == "BULLISH":
                    participants_output[p]["contrarian_view"] = "BEARISH"
                elif classifications[p]["stance"] == "BEARISH":
                    participants_output[p]["contrarian_view"] = "BULLISH"
                else:
                    participants_output[p]["contrarian_view"] = "NEUTRAL"

        # Generate outputs
        print("\n💾 Generating outputs...")
        generator = PredictionOutputGenerator()

        # JSON output
        json_output = generator.generate_json(
            today_date,
            market_view,
            confidence,
            participants_output,
            key_factors,
            reasoning,
        )
        with open("market_prediction.json", "w") as f:
            json.dump(json_output, f, indent=2)
        print("   ✓ market_prediction.json")

        # Text output
        text_output = generator.generate_text(
            today_date,
            market_view,
            confidence,
            participants_output,
            key_factors,
            reasoning,
        )
        with open("market_prediction.txt", "w") as f:
            f.write(text_output)
        print("   ✓ market_prediction.txt")

        # High-confidence alert (separate file for conditional sending)
        if confidence == "HIGH":
            alert_text = generator.generate_high_confidence_alert(
                today_date, market_view, key_factors
            )
            with open("high_confidence_alert.txt", "w") as f:
                f.write(alert_text)
            print("   ✓ high_confidence_alert.txt (🔥 HIGH CONFIDENCE)")
        else:
            # Remove alert file if not high confidence
            if os.path.exists("high_confidence_alert.txt"):
                os.remove("high_confidence_alert.txt")

        # Add to historical tracking
        try:
            from prediction_tracker import PredictionTracker

            tracker = PredictionTracker()
            tracker.add_prediction(json_output)
            print("   ✓ Added to prediction history")
        except Exception as e:
            print(f"   ⚠ Could not update history: {e}")

        print("\n✅ Prediction complete!")
        return True

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("   Creating fallback message...")
        create_fallback_message()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        print("   Creating fallback message...")
        create_fallback_message()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
