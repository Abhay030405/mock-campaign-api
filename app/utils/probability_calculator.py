import random

from app.models.schemas import Customer

BASE_OPEN_RATE = 0.35  # 35%
BASE_CLICK_RATE = 0.08  # 8%


class ProbabilityCalculator:
    """Calculates per-customer open and click probabilities."""

    def calculate_customer_probabilities(
        self,
        customer: Customer,
        content_modifiers: dict,
        timing_modifiers: dict,
    ) -> dict:
        open_prob = self._calculate_open_probability(
            customer, content_modifiers, timing_modifiers
        )
        click_prob = self._calculate_click_probability(
            customer, content_modifiers, timing_modifiers
        )
        return {
            "open_probability": open_prob,
            "click_probability": click_prob,
        }

    # ------------------------------------------------------------------ #
    # Open probability
    # ------------------------------------------------------------------ #

    @staticmethod
    def _calculate_open_probability(
        customer: Customer,
        content_modifiers: dict,
        timing_modifiers: dict,
    ) -> float:
        open_prob = BASE_OPEN_RATE

        # Age modifiers
        if 18 <= customer.Age <= 25:
            open_prob += 0.05
        elif 26 <= customer.Age <= 40:
            open_prob += 0.03
        elif customer.Age >= 56:
            open_prob -= 0.08

        # Social media modifier
        if customer.Social_Media_Active == "Yes":
            open_prob += 0.05
        else:
            open_prob -= 0.03

        # Occupation type modifier
        if customer.Occupation_type == "Professional":
            open_prob += 0.08
        elif customer.Occupation_type == "Self-employed":
            open_prob += 0.02
        elif customer.Occupation_type == "Retired":
            open_prob -= 0.05

        # Content modifiers
        open_prob += content_modifiers.get("total_subject_modifier", 0.0)

        # Timing modifiers
        open_prob += timing_modifiers.get("total_timing_modifier", 0.0)

        # Random noise ±3%
        open_prob += random.uniform(-0.03, 0.03)

        # Clamp between 0.05 and 0.90
        return max(0.05, min(0.90, open_prob))

    # ------------------------------------------------------------------ #
    # Click probability
    # ------------------------------------------------------------------ #

    @staticmethod
    def _calculate_click_probability(
        customer: Customer,
        content_modifiers: dict,
        timing_modifiers: dict,
    ) -> float:
        click_prob = BASE_CLICK_RATE

        # Age modifiers
        if 18 <= customer.Age <= 25:
            click_prob += 0.03
        elif 26 <= customer.Age <= 40:
            click_prob += 0.02
        elif customer.Age >= 56:
            click_prob -= 0.05

        # Gender modifier (financial product targeting female senior citizens)
        if customer.Gender == "Female" and customer.Age >= 60:
            click_prob += 0.10

        # App installed modifier
        if customer.App_Installed == "Yes":
            click_prob += 0.10

        # Social media modifier
        if customer.Social_Media_Active == "Yes":
            click_prob += 0.02

        # Credit score modifier
        if customer.Credit_score > 750:
            click_prob += 0.05
        elif customer.Credit_score >= 650:
            click_prob += 0.02
        else:
            click_prob -= 0.03

        # Occupation type for students
        if customer.Occupation_type == "Student":
            click_prob += 0.03

        # Content modifiers
        click_prob += content_modifiers.get("total_body_modifier", 0.0)

        # Timing modifiers
        click_prob += timing_modifiers.get("total_timing_modifier", 0.0)

        # Random noise ±3%
        click_prob += random.uniform(-0.03, 0.03)

        # Clamp between 0.02 and 0.60
        return max(0.02, min(0.60, click_prob))
