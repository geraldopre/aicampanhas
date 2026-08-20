import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .prompts import MASTER_SYSTEM_PROMPT, PortfolioOptimizationPlan, HotelAnalysisReport, HotelWeeklyMetrics, ProposedAction
from .guardrails import MediaGuardrails
from ..config import settings

logger = logging.getLogger(__name__)

class MediaReasoningEngine:
    """
    Motor de Raciocínio de Mídia de Performance.
    Consolida métricas dos 9 hotéis, submete ao modelo de IA e valida os guardrails.
    """

    def __init__(self, model_name: str = settings.DEFAULT_MODEL):
        self.model_name = model_name

    def analyze_portfolio(
        self,
        hotels_data: List[Dict[str, Any]],
        hotels_config_map: Dict[str, Dict[str, Any]]
    ) -> PortfolioOptimizationPlan:
        """
        Gera o plano completo de otimização para o portfólio de hotéis.
        """
        user_prompt = self._build_portfolio_prompt(hotels_data)

        # 1. Tentar chamada via LLM
        plan_dict = self._call_llm(user_prompt)

        # 2. Se a chamada LLM falhar ou não houver API Key, usa o Motor Heurístico Determinístico
        if not plan_dict:
            logger.info("Executando motor heurístico determinístico de fallback.")
            plan = self._heuristic_fallback(hotels_data, hotels_config_map)
        else:
            try:
                plan = PortfolioOptimizationPlan.model_validate(plan_dict)
            except Exception as e:
                logger.error(f"Erro ao validar JSON da IA com Pydantic: {e}. Usando fallback heurístico.")
                plan = self._heuristic_fallback(hotels_data, hotels_config_map)

        # 3. Aplicar a camada de Guardrails de Segurança
        final_plan = MediaGuardrails.enforce_guardrails(plan, hotels_config_map)
        return final_plan

    def _build_portfolio_prompt(self, hotels_data: List[Dict[str, Any]]) -> str:
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = f"Data da Análise: {today_str}\n\n"
        prompt += "Abaixo estão os dados consolidados de desempenho dos últimos 7 dias para os hotéis do Grupo Wish:\n\n"
        prompt += json.dumps(hotels_data, indent=2, ensure_ascii=False)
        prompt += "\n\nGere o diagnóstico e a lista de ações operacionais com base nas regras de negócio fornecidas."
        return prompt

    def _call_llm(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        # Suporte a Gemini
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=MASTER_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                logger.warning(f"Falha ao chamar Gemini API: {e}")

        # Suporte a OpenAI
        if settings.OPENAI_API_KEY:
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2
                }
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
                data = res.json()
                return json.loads(data["choices"][0]["message"]["content"])
            except Exception as e:
                logger.warning(f"Falha ao chamar OpenAI API: {e}")

        # Suporte a Anthropic
        if settings.ANTHROPIC_API_KEY:
            try:
                import requests
                headers = {
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "system": MASTER_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt + "\n\nResponda estritamente em JSON."}],
                    "temperature": 0.2
                }
                res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
                data = res.json()
                text = data["content"][0]["text"]
                # Extrai JSON
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                return json.loads(text)
            except Exception as e:
                logger.warning(f"Falha ao chamar Anthropic API: {e}")

        return None

    def _heuristic_fallback(
        self,
        hotels_data: List[Dict[str, Any]],
        hotels_config_map: Dict[str, Dict[str, Any]]
    ) -> PortfolioOptimizationPlan:
        """
        Motor analítico determinístico que aplica rigorosamente as regras de negócio
        caso nenhuma API de LLM externa esteja configurada.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        hotels_report = []

        total_portfolio_spend = 0.0
        total_portfolio_revenue = 0.0

        for h in hotels_data:
            hotel_id = h["hotel_id"]
            hotel_name = h["hotel_name"]
            config = hotels_config_map.get(hotel_id, {})
            target_roas = config.get("target_roas", 9.0)
            max_cpa = config.get("max_cpa_brl", 170.0)

            campaigns = h.get("campaigns", [])
            hotel_spend = sum(c.get("spend_7d_brl", 0) for c in campaigns)
            hotel_revenue = sum(c.get("revenue_7d_brl", 0) for c in campaigns)
            hotel_bookings = sum(c.get("bookings", 0) for c in campaigns)

            hotel_roas = round(hotel_revenue / hotel_spend, 2) if hotel_spend > 0 else 0.0
            hotel_cpa = round(hotel_spend / hotel_bookings, 2) if hotel_bookings > 0 else 0.0

            total_portfolio_spend += hotel_spend
            total_portfolio_revenue += hotel_revenue

            health = "HEALTHY" if hotel_roas >= target_roas else ("ATTENTION" if hotel_roas >= target_roas * 0.8 else "CRITICAL")

            actions: List[ProposedAction] = []

            for c in campaigns:
                c_type = c.get("campaign_type", "")
                daily_b = c.get("current_daily_budget_brl", 0.0)
                roas = c.get("roas", 0.0)
                cpa = c.get("cpa_brl", 0.0)
                lost_budget = c.get("lost_is_budget", 0.0)
                freq = c.get("frequency", 1.0)

                # Regra 1: Brand Protection
                if c_type == "SEARCH_BRAND" and lost_budget >= 0.10:
                    new_b = round(daily_b * 1.20, 2)
                    actions.append(ProposedAction(
                        platform=c["platform"],
                        campaign_id=c["campaign_id"],
                        campaign_name=c["campaign_name"],
                        campaign_type=c_type,
                        action_type="UPDATE_DAILY_BUDGET",
                        current_daily_budget_brl=daily_b,
                        new_daily_budget_brl=new_b,
                        change_pct=20.0,
                        priority="HIGH",
                        guardrail_passed=True,
                        rationale=f"Aumento de 20% para cobrir {int(lost_budget*100)}% de perda por orçamento na busca da marca própria (ROAS {roas})."
                    ))

                # Regra 2: Escalar PMax com alto ROAS
                elif c_type == "PMAX" and roas >= target_roas * 1.15 and lost_budget >= 0.15:
                    new_b = round(daily_b * 1.20, 2)
                    actions.append(ProposedAction(
                        platform=c["platform"],
                        campaign_id=c["campaign_id"],
                        campaign_name=c["campaign_name"],
                        campaign_type=c_type,
                        action_type="UPDATE_DAILY_BUDGET",
                        current_daily_budget_brl=daily_b,
                        new_daily_budget_brl=new_b,
                        change_pct=20.0,
                        priority="HIGH",
                        guardrail_passed=True,
                        rationale=f"Escala de 20% na PMax: ROAS de {roas} supera meta de {target_roas} com {int(lost_budget*100)}% de demanda reprimida."
                    ))

                # Regra 3: Reduzir Meta Ads saturado ou Display ineficiente
                elif (c_type == "META_CONVERSION" and (freq >= 3.2 or roas < target_roas * 0.75)) or (c_type == "DISPLAY" and roas < target_roas * 0.6):
                    new_b = round(daily_b * 0.80, 2)
                    motivo = f"Frequência elevada ({freq}) e CPA de R$ {cpa:.2f}" if c_type == "META_CONVERSION" else f"ROAS ineficiente de {roas}"
                    actions.append(ProposedAction(
                        platform=c["platform"],
                        campaign_id=c["campaign_id"],
                        campaign_name=c["campaign_name"],
                        campaign_type=c_type,
                        action_type="UPDATE_DAILY_BUDGET",
                        current_daily_budget_brl=daily_b,
                        new_daily_budget_brl=new_b,
                        change_pct=-20.0,
                        priority="HIGH",
                        guardrail_passed=True,
                        rationale=f"Redução preventiva de 20% em {c_type}: {motivo}. Verba realocada para canais de maior conversão."
                    ))

            summary = (
                f"{hotel_name} encerrou a semana com ROAS de {hotel_roas} (Meta: {target_roas}) e CPA de R$ {hotel_cpa:.2f} "
                f"(Limite: R$ {max_cpa:.2f}). Total de {hotel_bookings} reservas geradas."
            )

            hotels_report.append(HotelAnalysisReport(
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                health_score=health,
                weekly_metrics=HotelWeeklyMetrics(
                    spend_brl=round(hotel_spend, 2),
                    revenue_brl=round(hotel_revenue, 2),
                    roas_actual=hotel_roas,
                    roas_target=target_roas,
                    cpa_actual_brl=hotel_cpa,
                    cpa_max_brl=max_cpa,
                    bookings_count=hotel_bookings
                ),
                hotel_summary=summary,
                actions=actions
            ))

        global_roas = round(total_portfolio_revenue / total_portfolio_spend, 2) if total_portfolio_spend > 0 else 0.0
        global_summary = (
            f"Relatório Semanal do Portfólio Grupo Wish: R$ {total_portfolio_spend:,.2f} investidos, gerando "
            f"R$ {total_portfolio_revenue:,.2f} em receita com ROAS Médio de {global_roas}. "
            f"Identificadas oportunidades de escala em PMax/Search Brand e realocação de verba em Meta Ads com saturação de frequência."
        )

        return PortfolioOptimizationPlan(
            analysis_date=today_str,
            global_executive_summary=global_summary,
            hotels=hotels_report
        )
