import logging
from typing import Dict, Any, List
from .base import BaseAdConnector
from ..config import settings

logger = logging.getLogger(__name__)

class GoogleAdsClient(BaseAdConnector):
    """
    Cliente oficial para integração com a Google Ads API.
    Gerencia consultas GAQL para métricas de Search, PMax e Display,
    e mutações via CampaignBudgetService.
    """

    def __init__(self):
        self.initialized = False
        if settings.GOOGLE_ADS_DEVELOPER_TOKEN and settings.GOOGLE_ADS_REFRESH_TOKEN:
            try:
                # Inicializa o cliente oficial da biblioteca google-ads se configurado
                from google.ads.googleads.client import GoogleAdsClient as OfficialGoogleAdsClient
                credentials = {
                    "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                    "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                    "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                    "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
                    "login_customer_id": settings.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
                    "use_proto_plus": True
                }
                self.client = OfficialGoogleAdsClient.load_from_dict(credentials)
                self.initialized = True
                logger.info("Google Ads Client inicializado com sucesso.")
            except Exception as e:
                logger.warning(f"Não foi possível inicializar Google Ads API: {e}. Operando em modo Mock/Fallback.")
        else:
            logger.info("Credenciais do Google Ads não detectadas no .env. Operando em modo Mock/Fallback.")

    def fetch_weekly_performance(self, hotel_config: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        if not self.initialized:
            from .mock_connector import MockAdConnector
            return [c for c in MockAdConnector().fetch_weekly_performance(hotel_config, days) if c["platform"] == "google_ads"]

        customer_id = hotel_config.get("accounts", {}).get("google_ads_customer_id", "").replace("-", "")
        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                metrics.cost_micros,
                metrics.conversions_value,
                metrics.conversions,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share
            FROM campaign
            WHERE segments.date DURING LAST_{days}_DAYS
                AND campaign.status = 'ENABLED'
        """

        response = ga_service.search(customer_id=customer_id, query=query)
        campaigns = []

        for row in response:
            cost = row.metrics.cost_micros / 1_000_000.0
            conv_value = row.metrics.conversions_value
            conversions = row.metrics.conversions
            daily_budget = row.campaign_budget.amount_micros / 1_000_000.0
            roas = round(conv_value / cost, 2) if cost > 0 else 0.0
            cpa = round(cost / conversions, 2) if conversions > 0 else 0.0

            channel_type = str(row.campaign.advertising_channel_type.name)
            campaign_type = "SEARCH_BRAND" if "brand" in row.campaign.name.lower() or "institucional" in row.campaign.name.lower() else (
                "PMAX" if "PERFORMANCE_MAX" in channel_type else "SEARCH_GENERIC"
            )

            campaigns.append({
                "platform": "google_ads",
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "campaign_type": campaign_type,
                "current_daily_budget_brl": daily_budget,
                "spend_7d_brl": cost,
                "revenue_7d_brl": conv_value,
                "roas": roas,
                "cpa_brl": cpa,
                "bookings": int(conversions),
                "lost_is_budget": row.metrics.search_budget_lost_impression_share or 0.0,
                "lost_is_rank": row.metrics.search_rank_lost_impression_share or 0.0
            })

        return campaigns

    def update_campaign_daily_budget(
        self,
        customer_id_or_account_id: str,
        campaign_id: str,
        new_daily_budget_brl: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        customer_id = customer_id_or_account_id.replace("-", "")
        if dry_run or not self.initialized:
            return {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "platform": "google_ads",
                "account_id": customer_id,
                "campaign_id": campaign_id,
                "new_daily_budget_brl": new_daily_budget_brl,
                "message": f"[Dry-Run Google Ads] Orçamento da campanha {campaign_id} simulado para R$ {new_daily_budget_brl:.2f}/dia."
            }

        try:
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            campaign_service = self.client.get_service("CampaignService")

            # 1. Recuperar o ID do CampaignBudget associado
            q = f"SELECT campaign.id, campaign.campaign_budget FROM campaign WHERE campaign.id = {campaign_id}"
            res = self.client.get_service("GoogleAdsService").search(customer_id=customer_id, query=q)
            budget_resource_name = None
            for r in res:
                budget_resource_name = r.campaign.campaign_budget
                break

            if not budget_resource_name:
                raise ValueError(f"CampaignBudget não encontrado para a campanha {campaign_id}")

            # 2. Mutação do orçamento
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            campaign_budget = budget_operation.update
            campaign_budget.resource_name = budget_resource_name
            campaign_budget.amount_micros = int(new_daily_budget_brl * 1_000_000)
            self.client.copy_from(
                budget_operation.update_mask,
                self.client.get_type("FieldMask")(paths=["amount_micros"])
            )

            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[budget_operation]
            )

            return {
                "status": "SUCCESS",
                "mode": "LIVE",
                "platform": "google_ads",
                "account_id": customer_id,
                "campaign_id": campaign_id,
                "new_daily_budget_brl": new_daily_budget_brl,
                "resource_name": budget_response.results[0].resource_name
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar orçamento Google Ads para {campaign_id}: {e}")
            return {
                "status": "ERROR",
                "platform": "google_ads",
                "campaign_id": campaign_id,
                "error": str(e)
            }
