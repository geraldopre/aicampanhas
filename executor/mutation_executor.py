import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from ..agent.prompts import PortfolioOptimizationPlan, ProposedAction
from ..connectors.google_ads_client import GoogleAdsClient
from ..connectors.meta_ads_client import MetaAdsClient
from ..connectors.mock_connector import MockAdConnector
from ..config import settings

logger = logging.getLogger(__name__)

class MutationExecutor:
    """
    Executor de mutações em contas de anúncios.
    Aplica os ajustes de orçamento aprovados e registra histórico em log de auditoria.
    """

    def __init__(self, dry_run: bool = settings.DRY_RUN):
        self.dry_run = dry_run
        self.google_client = GoogleAdsClient()
        self.meta_client = MetaAdsClient()
        self.mock_client = MockAdConnector()

    def execute_plan(
        self,
        plan: PortfolioOptimizationPlan,
        hotels_config_map: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        results = []
        execution_timestamp = datetime.now().isoformat()

        for hotel in plan.hotels:
            hotel_config = hotels_config_map.get(hotel.hotel_id, {})
            accounts = hotel_config.get("accounts", {})

            for action in hotel.actions:
                if action.action_type != "UPDATE_DAILY_BUDGET":
                    continue

                res = self._apply_single_action(action, accounts)
                res["hotel_id"] = hotel.hotel_id
                res["hotel_name"] = hotel.hotel_name
                res["timestamp"] = execution_timestamp
                res["rationale"] = action.rationale
                results.append(res)

        # Salvar no log de auditoria
        self._append_to_audit_log(results)
        return results

    def _apply_single_action(self, action: ProposedAction, accounts: Dict[str, str]) -> Dict[str, Any]:
        platform = action.platform
        campaign_id = action.campaign_id
        new_budget = action.new_daily_budget_brl

        if platform == "google_ads":
            customer_id = accounts.get("google_ads_customer_id", "000-000-0000")
            return self.google_client.update_campaign_daily_budget(
                customer_id_or_account_id=customer_id,
                campaign_id=campaign_id,
                new_daily_budget_brl=new_budget,
                dry_run=self.dry_run
            )

        elif platform == "meta_ads":
            account_id = accounts.get("meta_ad_account_id", "act_000000")
            return self.meta_client.update_campaign_daily_budget(
                customer_id_or_account_id=account_id,
                campaign_id=campaign_id,
                new_daily_budget_brl=new_budget,
                dry_run=self.dry_run
            )

        else:
            return self.mock_client.update_campaign_daily_budget(
                customer_id_or_account_id="other_platform",
                campaign_id=campaign_id,
                new_daily_budget_brl=new_budget,
                dry_run=self.dry_run
            )

    def _append_to_audit_log(self, execution_results: List[Dict[str, Any]]):
        audit_file = settings.AUDIT_LOG_FILE
        existing_logs = []

        if audit_file.exists():
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    existing_logs = json.load(f)
            except Exception:
                existing_logs = []

        existing_logs.extend(execution_results)

        try:
            with open(audit_file, "w", encoding="utf-8") as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)
            logger.info(f"Log de auditoria atualizado em {audit_file} com {len(execution_results)} registros.")
        except Exception as e:
            logger.error(f"Erro ao gravar log de auditoria: {e}")
