from typing import Dict, Any, List
import random
from .base import BaseAdConnector

class MockAdConnector(BaseAdConnector):
    """
    Conector Mock para testes e simulação com dados realistas para os 9 hotéis do Grupo Wish.
    Simula comportamentos típicos de mercado (Search Brand com alto ROAS, PMax escalando com perda de verba,
    Meta Ads sofrendo com fadiga de criativos e Display com baixa conversão).
    """

    def fetch_weekly_performance(self, hotel_config: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        hotel_id = hotel_config["hotel_id"]
        monthly_budget = hotel_config.get("monthly_budget_brl", 30000.0)
        weekly_budget = monthly_budget / 4.3
        target_roas = hotel_config.get("target_roas", 9.0)
        max_cpa = hotel_config.get("max_cpa_brl", 170.0)

        # Perfis específicos para criar cenários de decisão interessantes
        if hotel_id == "wish_foz":
            return [
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_search_brand_{hotel_id}",
                    "campaign_name": f"Search - Institucional Marca {hotel_config['name']}",
                    "campaign_type": "SEARCH_BRAND",
                    "current_daily_budget_brl": 180.00,
                    "spend_7d_brl": 1260.00,
                    "revenue_7d_brl": 20160.00,
                    "roas": 16.0,
                    "cpa_brl": 63.00,
                    "bookings": 20,
                    "lost_is_budget": 0.22,
                    "lost_is_rank": 0.04
                },
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_pmax_{hotel_id}",
                    "campaign_name": f"PMax - {hotel_config['destination']} & Lazer",
                    "campaign_type": "PMAX",
                    "current_daily_budget_brl": 450.00,
                    "spend_7d_brl": 3150.00,
                    "revenue_7d_brl": 37800.00,
                    "roas": 12.0,
                    "cpa_brl": 105.00,
                    "bookings": 30,
                    "lost_is_budget": 0.28,
                    "lost_is_rank": 0.08
                },
                {
                    "platform": "meta_ads",
                    "campaign_id": f"meta_conv_{hotel_id}",
                    "campaign_name": f"Meta - Família & Férias {hotel_config['name']}",
                    "campaign_type": "META_CONVERSION",
                    "current_daily_budget_brl": 350.00,
                    "spend_7d_brl": 2450.00,
                    "revenue_7d_brl": 11025.00,
                    "roas": 4.5,
                    "cpa_brl": 272.22,
                    "bookings": 9,
                    "frequency": 3.6,
                    "cpm_brl": 38.50
                },
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_display_{hotel_id}",
                    "campaign_name": f"Display - Remarketing Dinâmico {hotel_config['name']}",
                    "campaign_type": "DISPLAY",
                    "current_daily_budget_brl": 100.00,
                    "spend_7d_brl": 700.00,
                    "revenue_7d_brl": 2450.00,
                    "roas": 3.5,
                    "cpa_brl": 350.00,
                    "bookings": 2,
                    "lost_is_budget": 0.05
                }
            ]
        elif hotel_id == "wish_serrano":
            return [
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_search_brand_{hotel_id}",
                    "campaign_name": f"Search - Brand {hotel_config['name']}",
                    "campaign_type": "SEARCH_BRAND",
                    "current_daily_budget_brl": 250.00,
                    "spend_7d_brl": 1750.00,
                    "revenue_7d_brl": 31500.00,
                    "roas": 18.0,
                    "cpa_brl": 70.00,
                    "bookings": 25,
                    "lost_is_budget": 0.12,
                    "lost_is_rank": 0.02
                },
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_pmax_{hotel_id}",
                    "campaign_name": f"PMax - Inverno & Gastronomia Gramado",
                    "campaign_type": "PMAX",
                    "current_daily_budget_brl": 600.00,
                    "spend_7d_brl": 4200.00,
                    "revenue_7d_brl": 46200.00,
                    "roas": 11.0,
                    "cpa_brl": 120.00,
                    "bookings": 35,
                    "lost_is_budget": 0.32,
                    "lost_is_rank": 0.06
                },
                {
                    "platform": "meta_ads",
                    "campaign_id": f"meta_conv_{hotel_id}",
                    "campaign_name": f"Meta - Casais & Lua de Mel Gramado",
                    "campaign_type": "META_CONVERSION",
                    "current_daily_budget_brl": 350.00,
                    "spend_7d_brl": 2450.00,
                    "revenue_7d_brl": 22050.00,
                    "roas": 9.0,
                    "cpa_brl": 175.00,
                    "bookings": 14,
                    "frequency": 2.1,
                    "cpm_brl": 32.00
                }
            ]
        else:
            # Geração parametrizada e realista para os demais hotéis
            brand_daily = weekly_budget * 0.30 / 7
            pmax_daily = weekly_budget * 0.45 / 7
            meta_daily = weekly_budget * 0.25 / 7

            brand_roas = random.uniform(13.0, 17.5)
            pmax_roas = random.uniform(target_roas - 0.5, target_roas + 2.5)
            meta_roas = random.uniform(target_roas - 2.5, target_roas + 0.8)

            brand_spend = brand_daily * 7
            pmax_spend = pmax_daily * 7
            meta_spend = meta_daily * 7

            return [
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_search_brand_{hotel_id}",
                    "campaign_name": f"Search - Brand {hotel_config['name']}",
                    "campaign_type": "SEARCH_BRAND",
                    "current_daily_budget_brl": round(brand_daily, 2),
                    "spend_7d_brl": round(brand_spend, 2),
                    "revenue_7d_brl": round(brand_spend * brand_roas, 2),
                    "roas": round(brand_roas, 1),
                    "cpa_brl": round(brand_spend / max(1, int(brand_spend / 75)), 2),
                    "bookings": int(brand_spend / 75),
                    "lost_is_budget": round(random.uniform(0.08, 0.25), 2),
                    "lost_is_rank": 0.03
                },
                {
                    "platform": "google_ads",
                    "campaign_id": f"g_pmax_{hotel_id}",
                    "campaign_name": f"PMax - {hotel_config['destination']}",
                    "campaign_type": "PMAX",
                    "current_daily_budget_brl": round(pmax_daily, 2),
                    "spend_7d_brl": round(pmax_spend, 2),
                    "revenue_7d_brl": round(pmax_spend * pmax_roas, 2),
                    "roas": round(pmax_roas, 1),
                    "cpa_brl": round(pmax_spend / max(1, int(pmax_spend / max_cpa)), 2),
                    "bookings": int(pmax_spend / max_cpa),
                    "lost_is_budget": round(random.uniform(0.15, 0.35), 2),
                    "lost_is_rank": 0.05
                },
                {
                    "platform": "meta_ads",
                    "campaign_id": f"meta_conv_{hotel_id}",
                    "campaign_name": f"Meta - Reservas Diretas {hotel_config['name']}",
                    "campaign_type": "META_CONVERSION",
                    "current_daily_budget_brl": round(meta_daily, 2),
                    "spend_7d_brl": round(meta_spend, 2),
                    "revenue_7d_brl": round(meta_spend * meta_roas, 2),
                    "roas": round(meta_roas, 1),
                    "cpa_brl": round(meta_spend / max(1, int(meta_spend / (max_cpa * 1.15))), 2),
                    "bookings": int(meta_spend / (max_cpa * 1.15)),
                    "frequency": round(random.uniform(1.8, 3.4), 1),
                    "cpm_brl": 34.00
                }
            ]

    def update_campaign_daily_budget(
        self,
        customer_id_or_account_id: str,
        campaign_id: str,
        new_daily_budget_brl: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "mode": "DRY_RUN" if dry_run else "LIVE",
            "account_id": customer_id_or_account_id,
            "campaign_id": campaign_id,
            "new_daily_budget_brl": new_daily_budget_brl,
            "message": f"[Mock] Orçamento diário da campanha {campaign_id} ajustado para R$ {new_daily_budget_brl:.2f}"
        }
