import logging
from typing import Dict, Any, List
from .prompts import PortfolioOptimizationPlan, ProposedAction

logger = logging.getLogger(__name__)

class MediaGuardrails:
    """
    Camada de segurança determinística que valida e corrige qualquer proposta gerada pela IA
    antes de ser enviada para aprovação ou execução.
    """

    MAX_PERCENT_SWING = 20.0  # Máximo de 20% de aumento ou corte semanal
    MIN_DAILY_BUDGET_BRL = 20.0  # Orçamento mínimo diário por campanha

    @classmethod
    def enforce_guardrails(
        cls,
        plan: PortfolioOptimizationPlan,
        hotels_config_map: Dict[str, Dict[str, Any]]
    ) -> PortfolioOptimizationPlan:
        """
        Varre todas as ações de todos os hotéis no plano e aplica os limites de segurança.
        """
        for hotel in plan.hotels:
            config = hotels_config_map.get(hotel.hotel_id, {})
            monthly_budget = config.get("monthly_budget_brl", 30000.0)
            max_daily_hotel_spend = (monthly_budget / 30.0) * 1.15  # Tolerância de 15% no pacing diário

            total_daily_proposed = 0.0

            for action in hotel.actions:
                current_b = action.current_daily_budget_brl
                new_b = action.new_daily_budget_brl

                if current_b <= 0:
                    continue

                actual_change_pct = ((new_b - current_b) / current_b) * 100.0

                # 1. Trava de Variação Máxima de 20%
                if actual_change_pct > cls.MAX_PERCENT_SWING:
                    logger.warning(
                        f"Guardrail acionado: Aumento excessivo ({actual_change_pct:.1f}%) na campanha {action.campaign_name}. "
                        f"Limitando a +{cls.MAX_PERCENT_SWING}%."
                    )
                    clamped_b = round(current_b * (1 + (cls.MAX_PERCENT_SWING / 100.0)), 2)
                    action.new_daily_budget_brl = clamped_b
                    action.change_pct = cls.MAX_PERCENT_SWING
                    action.rationale += f" [Guardrail: Aumento limitado a +{cls.MAX_PERCENT_SWING}% para proteger Smart Bidding]"

                elif actual_change_pct < -cls.MAX_PERCENT_SWING:
                    logger.warning(
                        f"Guardrail acionado: Corte excessivo ({actual_change_pct:.1f}%) na campanha {action.campaign_name}. "
                        f"Limitando a -{cls.MAX_PERCENT_SWING}%."
                    )
                    clamped_b = round(current_b * (1 - (cls.MAX_PERCENT_SWING / 100.0)), 2)
                    clamped_b = max(clamped_b, cls.MIN_DAILY_BUDGET_BRL)
                    action.new_daily_budget_brl = clamped_b
                    action.change_pct = -cls.MAX_PERCENT_SWING
                    action.rationale += f" [Guardrail: Redução limitada a -{cls.MAX_PERCENT_SWING}%]"

                # 2. Piso mínimo de orçamento diário
                if action.new_daily_budget_brl < cls.MIN_DAILY_BUDGET_BRL and action.action_type == "UPDATE_DAILY_BUDGET":
                    action.new_daily_budget_brl = cls.MIN_DAILY_BUDGET_BRL
                    action.rationale += f" [Guardrail: Ajustado para o piso mínimo de R$ {cls.MIN_DAILY_BUDGET_BRL:.2f}]"

                total_daily_proposed += action.new_daily_budget_brl

            # 3. Pacing Mensal do Hotel
            if total_daily_proposed > max_daily_hotel_spend:
                logger.warning(
                    f"Guardrail acionado: Orçamento total diário proposto (R$ {total_daily_proposed:.2f}) "
                    f"para {hotel.hotel_name} excede o pacing mensal seguro (R$ {max_daily_hotel_spend:.2f})."
                )
                ratio = max_daily_hotel_spend / total_daily_proposed
                for action in hotel.actions:
                    if action.action_type == "UPDATE_DAILY_BUDGET" and action.new_daily_budget_brl > action.current_daily_budget_brl:
                        action.new_daily_budget_brl = round(action.new_daily_budget_brl * ratio, 2)
                        action.change_pct = round(((action.new_daily_budget_brl - action.current_daily_budget_brl) / action.current_daily_budget_brl) * 100, 1)
                        action.rationale += " [Guardrail: Normalizado para respeitar o teto orçamentário mensal]"

        return plan
