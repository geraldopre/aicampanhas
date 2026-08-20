import logging
from typing import Dict, Any, List
import requests
from .base import BaseAdConnector
from ..config import settings

logger = logging.getLogger(__name__)

class MetaAdsClient(BaseAdConnector):
    """
    Cliente para integração com a Meta Marketing API (Facebook / Instagram Ads).
    Extrai métricas de conversão e custo por campanha/conjunto de anúncios e realiza ajustes de verba.
    """

    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.initialized = bool(self.access_token)

    def fetch_weekly_performance(self, hotel_config: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        if not self.initialized:
            from .mock_connector import MockAdConnector
            return [c for c in MockAdConnector().fetch_weekly_performance(hotel_config, days) if c["platform"] == "meta_ads"]

        account_id = hotel_config.get("accounts", {}).get("meta_ad_account_id", "")
        if not account_id.startswith("act_"):
            account_id = f"act_{account_id}"

        url = f"{self.base_url}/{account_id}/campaigns"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,daily_budget,lifetime_budget,status,insights.date_preset(last_7d){spend,purchase_roas,actions,frequency,cpm}",
            "filtering": "[{'field':'effective_status','operator':'IN','value':['ACTIVE']}]"
        }

        try:
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            campaigns = []

            for item in data.get("data", []):
                insights = item.get("insights", {}).get("data", [{}])[0]
                spend = float(insights.get("spend", 0.0))
                daily_budget = float(item.get("daily_budget", 0)) / 100.0 if "daily_budget" in item else 0.0

                # Extrai ROAS de compra
                roas_list = insights.get("purchase_roas", [])
                roas = float(roas_list[0].get("value", 0.0)) if roas_list else 0.0

                # Extrai reservas (compras)
                actions = insights.get("actions", [])
                bookings = 0
                for a in actions:
                    if a.get("action_type") in ["purchase", "omni_purchase"]:
                        bookings = int(a.get("value", 0))
                        break

                revenue = spend * roas
                cpa = round(spend / bookings, 2) if bookings > 0 else 0.0
                frequency = float(insights.get("frequency", 1.0))

                campaigns.append({
                    "platform": "meta_ads",
                    "campaign_id": item["id"],
                    "campaign_name": item["name"],
                    "campaign_type": "META_CONVERSION" if "conv" in item["name"].lower() or "reserva" in item["name"].lower() else "META_TRAFFIC",
                    "current_daily_budget_brl": daily_budget,
                    "spend_7d_brl": spend,
                    "revenue_7d_brl": revenue,
                    "roas": round(roas, 2),
                    "cpa_brl": cpa,
                    "bookings": bookings,
                    "frequency": round(frequency, 2),
                    "cpm_brl": float(insights.get("cpm", 0.0))
                })

            return campaigns
        except Exception as e:
            logger.error(f"Erro ao buscar dados do Meta Ads para {account_id}: {e}")
            from .mock_connector import MockAdConnector
            return [c for c in MockAdConnector().fetch_weekly_performance(hotel_config, days) if c["platform"] == "meta_ads"]

    def update_campaign_daily_budget(
        self,
        customer_id_or_account_id: str,
        campaign_id: str,
        new_daily_budget_brl: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        if dry_run or not self.initialized:
            return {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "platform": "meta_ads",
                "campaign_id": campaign_id,
                "new_daily_budget_brl": new_daily_budget_brl,
                "message": f"[Dry-Run Meta Ads] Orçamento diário da campanha {campaign_id} simulado para R$ {new_daily_budget_brl:.2f}"
            }

        url = f"{self.base_url}/{campaign_id}"
        # A Meta API espera orçamentos em centavos
        payload = {
            "daily_budget": int(new_daily_budget_brl * 100),
            "access_token": self.access_token
        }

        try:
            res = requests.post(url, data=payload, timeout=15)
            data = res.json()
            if data.get("success"):
                return {
                    "status": "SUCCESS",
                    "mode": "LIVE",
                    "platform": "meta_ads",
                    "campaign_id": campaign_id,
                    "new_daily_budget_brl": new_daily_budget_brl
                }
            else:
                return {
                    "status": "ERROR",
                    "platform": "meta_ads",
                    "campaign_id": campaign_id,
                    "error": data.get("error", {}).get("message", "Erro desconhecido na Meta API")
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "platform": "meta_ads",
                "campaign_id": campaign_id,
                "error": str(e)
            }
