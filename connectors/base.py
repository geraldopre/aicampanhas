from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAdConnector(ABC):
    """Interface abstrata para conectores de dados de plataformas de mídia."""

    @abstractmethod
    def fetch_weekly_performance(self, hotel_config: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        """Extrai as métricas de performance da semana para o hotel."""
        pass

    @abstractmethod
    def update_campaign_daily_budget(
        self,
        customer_id_or_account_id: str,
        campaign_id: str,
        new_daily_budget_brl: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """Altera o orçamento diário da campanha na plataforma."""
        pass
