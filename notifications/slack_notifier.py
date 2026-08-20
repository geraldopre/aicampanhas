import json
import logging
import requests
from typing import Dict, Any
from ..agent.prompts import PortfolioOptimizationPlan
from ..config import settings

logger = logging.getLogger(__name__)

class SlackNotifier:
    """
    Formatador e despachante de relatórios executivos e cartões de aprovação interativa
    para Slack e webhooks.
    """

    @classmethod
    def send_optimization_report(cls, plan: PortfolioOptimizationPlan) -> bool:
        if not settings.SLACK_WEBHOOK_URL:
            logger.info("SLACK_WEBHOOK_URL não configurado. Exibindo payload formatado no log/console.")
            return False

        payload = cls.build_slack_blocks(plan)
        try:
            res = requests.post(settings.SLACK_WEBHOOK_URL, json=payload, timeout=10)
            if res.status_code == 200:
                logger.info("Relatório de otimização enviado com sucesso ao Slack.")
                return True
            else:
                logger.warning(f"Erro ao enviar para o Slack: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção ao disparar webhook do Slack: {e}")
            return False

    @classmethod
    def build_slack_blocks(cls, plan: PortfolioOptimizationPlan) -> Dict[str, Any]:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🏨 Otimização Semanal de Mídia - Grupo Wish ({plan.analysis_date})",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{plan.global_executive_summary}*"
                }
            },
            {"type": "divider"}
        ]

        total_actions = sum(len(h.actions) for h in plan.hotels)

        for hotel in plan.hotels:
            health_emoji = "🟢" if hotel.health_score == "HEALTHY" else ("🟡" if hotel.health_score == "ATTENTION" else "🔴")
            m = hotel.weekly_metrics

            hotel_text = (
                f"{health_emoji} *{hotel.hotel_name}*\n"
                f"• *Investimento:* R$ {m.spend_brl:,.2f} | *Receita:* R$ {m.revenue_brl:,.2f}\n"
                f"• *ROAS Real:* `{m.roas_actual}x` (Meta: `{m.roas_target}x`) | *CPA:* R$ {m.cpa_actual_brl:.2f} ({m.bookings_count} reservas)\n"
                f"_{hotel.hotel_summary}_"
            )

            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": hotel_text}
            })

            if hotel.actions:
                action_lines = []
                for act in hotel.actions:
                    icon = "📈" if act.change_pct > 0 else "📉"
                    action_lines.append(
                        f"  {icon} *{act.campaign_name}* ({act.platform.upper()}):\n"
                        f"     R$ {act.current_daily_budget_brl:.2f} ➔ *R$ {act.new_daily_budget_brl:.2f}* ({act.change_pct:+.1f}%)\n"
                        f"     _Justificativa: {act.rationale}_"
                    )

                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Ajustes Propostos:*\n" + "\n".join(action_lines)
                    }
                })

            blocks.append({"type": "divider"})

        # Ações interativas no rodapé
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": f"✅ Aprovar {total_actions} Ajustes", "emoji": True},
                    "style": "primary",
                    "value": "approve_all_optimizations",
                    "action_id": "approve_btn"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✏️ Abrir Dashboard / Editar", "emoji": True},
                    "value": "open_dashboard",
                    "action_id": "dashboard_btn"
                }
            ]
        })

        return {"blocks": blocks}
