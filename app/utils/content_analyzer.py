import re
from datetime import datetime


class ContentAnalyzer:
    """Analyzes email content quality and returns probability modifiers."""

    # ------------------------------------------------------------------ #
    # Subject line analysis
    # ------------------------------------------------------------------ #

    def analyze_subject_line(self, subject: str) -> dict:
        length = len(subject)
        if 40 <= length <= 60:
            length_modifier = 0.05
        elif length < 20:
            length_modifier = -0.08
        elif length > 80:
            length_modifier = -0.10
        else:
            length_modifier = 0.0

        emoji_modifier = 0.03 if self._has_emoji(subject) else 0.0

        personalization_modifier = (
            0.04 if re.search(r"\b(you|your)\b", subject, re.IGNORECASE) else 0.0
        )

        urgency_modifier = (
            0.06
            if re.search(r"\b(limited|now|today|hurry)\b", subject, re.IGNORECASE)
            else 0.0
        )

        spam_modifier = (
            -0.15
            if re.search(r"!!!|FREE!!!|ACT NOW!!!", subject)
            else 0.0
        )

        total_subject_modifier = (
            length_modifier
            + emoji_modifier
            + personalization_modifier
            + urgency_modifier
            + spam_modifier
        )

        return {
            "length_modifier": length_modifier,
            "emoji_modifier": emoji_modifier,
            "personalization_modifier": personalization_modifier,
            "urgency_modifier": urgency_modifier,
            "spam_modifier": spam_modifier,
            "total_subject_modifier": total_subject_modifier,
        }

    # ------------------------------------------------------------------ #
    # Body content analysis
    # ------------------------------------------------------------------ #

    def analyze_body_content(self, body: str) -> dict:
        word_count = len(body.split())

        if 100 <= word_count <= 200:
            length_modifier = 0.05
        elif word_count < 50:
            length_modifier = -0.05
        elif word_count > 300:
            length_modifier = -0.08
        else:
            length_modifier = 0.0

        cta_link_modifier = (
            0.10 if re.search(r"https?://", body) else 0.0
        )

        formatting_modifier = (
            0.03
            if re.search(r"<(b|strong|i|em)\b", body, re.IGNORECASE)
            else 0.0
        )

        emoji_modifier = 0.02 if self._has_emoji(body) else 0.0

        benefit_focus_modifier = (
            0.08
            if re.search(
                r"\b(higher returns|earn more|save|benefit)\b", body, re.IGNORECASE
            )
            else 0.0
        )

        urgency_modifier = (
            0.06
            if re.search(r"\b(limited|now|today|hurry|urgent)\b", body, re.IGNORECASE)
            else 0.0
        )

        spam_modifier = (
            -0.10
            if re.search(r"!!!|FREE!!!|ACT NOW!!!", body)
            else 0.0
        )

        total_body_modifier = (
            length_modifier
            + cta_link_modifier
            + formatting_modifier
            + emoji_modifier
            + benefit_focus_modifier
            + urgency_modifier
            + spam_modifier
        )

        return {
            "length_modifier": length_modifier,
            "cta_link_modifier": cta_link_modifier,
            "formatting_modifier": formatting_modifier,
            "emoji_modifier": emoji_modifier,
            "benefit_focus_modifier": benefit_focus_modifier,
            "urgency_modifier": urgency_modifier,
            "spam_modifier": spam_modifier,
            "total_body_modifier": total_body_modifier,
        }

    # ------------------------------------------------------------------ #
    # Timing analysis
    # ------------------------------------------------------------------ #

    def analyze_timing(self, scheduled_time: datetime) -> dict:
        day = scheduled_time.weekday()  # 0=Monday … 6=Sunday

        if day in (1, 2):  # Tuesday, Wednesday
            day_of_week_modifier = 0.08
        elif day == 0:  # Monday
            day_of_week_modifier = 0.03
        elif day == 3:  # Thursday
            day_of_week_modifier = 0.02
        elif day == 4:  # Friday
            day_of_week_modifier = -0.05
        else:  # Weekend
            day_of_week_modifier = -0.12

        hour = scheduled_time.hour

        if 8 <= hour < 10:
            time_of_day_modifier = 0.10
        elif 10 <= hour < 12:
            time_of_day_modifier = 0.05
        elif 12 <= hour < 14:
            time_of_day_modifier = -0.03
        elif 14 <= hour < 16:
            time_of_day_modifier = 0.03
        elif 16 <= hour < 18:
            time_of_day_modifier = 0.0
        else:  # Evening / Night
            time_of_day_modifier = -0.10

        total_timing_modifier = day_of_week_modifier + time_of_day_modifier

        return {
            "day_of_week_modifier": day_of_week_modifier,
            "time_of_day_modifier": time_of_day_modifier,
            "total_timing_modifier": total_timing_modifier,
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _has_emoji(text: str) -> bool:
        """Return True if the text contains at least one emoji character."""
        return bool(
            re.search(
                "["
                "\U0001f600-\U0001f64f"
                "\U0001f300-\U0001f5ff"
                "\U0001f680-\U0001f6ff"
                "\U0001f1e0-\U0001f1ff"
                "\U00002700-\U000027bf"
                "\U0000fe00-\U0000fe0f"
                "\U0001f900-\U0001f9ff"
                "\U0001fa00-\U0001fa6f"
                "\U0001fa70-\U0001faff"
                "]+",
                text,
            )
        )
