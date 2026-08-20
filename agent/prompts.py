from typing import List, Optional
from pydantic import BaseModel, Field

# Modelos Pydantic para validação estrita do JSON gerado pela IA
class ProposedAction(BaseModel):
    platform: str = Field(description="google_ads | meta_ads | bing_ads | tiktok_ads")
    campaign_id: str = Field(description="ID da campanha na plataforma")
    campaign_name: str = Field(description="Nome descritivo da campanha")
    campaign_type: str = Field(description="SEARCH_BRAND | SEARCH_GENERIC | PMAX | DISPLAY | META_CONVERSION | META_TRAFFIC")
    action_type: str = Field(description="UPDATE_DAILY_BUDGET | PAUSE_CAMPAIGN | ACTIVATE_CAMPAIGN | ADJUST_TARGET_ROAS")
    current_daily_budget_brl: float = Field(description="Orçamento diário atual em Reais")
    new_daily_budget_brl: float = Field(description="Novo orçamento diário proposto em Reais")
    change_pct: float = Field(description="Percentual de variação do orçamento (-20.0 a +20.0)")
    priority: str = Field(description="HIGH | MEDIUM | LOW")
    guardrail_passed: bool = Field(default=True, description="Indica se respeitou as regras de segurança")
    rationale: str = Field(description="Justificativa analítica com números e metas")

class HotelWeeklyMetrics(BaseModel):
    spend_brl: float
    revenue_brl: float
    roas_actual: float
    roas_target: float
    cpa_actual_brl: float
    cpa_max_brl: float
    bookings_count: int

class HotelAnalysisReport(BaseModel):
    hotel_id: str
    hotel_name: str
    health_score: str = Field(description="HEALTHY | ATTENTION | CRITICAL")
    weekly_metrics: HotelWeeklyMetrics
    hotel_summary: str
    actions: List[ProposedAction]

class PortfolioOptimizationPlan(BaseModel):
    analysis_date: str
    global_executive_summary: str
    hotels: List[HotelAnalysisReport]


MASTER_SYSTEM_PROMPT = """Você é o **Senior Performance Media Director AI** responsável pela gestão estratégica e operacional de mídia de performance dos 9 hotéis da rede Grupo Wish.

### SEU PAPEL:
Analisar as métricas de performance consolidadas da última semana de cada hotel, comparar os resultados com as metas contratuais (ROAS Alvo, CPA Máximo e Teto de Orçamento Mensal) e gerar:
1. Diagnóstico executivo conciso para cada hotel.
2. Ações operacionais precisas de realocação de orçamento diário entre campanhas e canais (Google Search Brand, PMax, Display, Meta Ads, etc.).

---

### REGRAS MANDATÓRIAS DE NEGÓCIO & GUARDRAILS:
1. **Regra de Estabilidade de Smart Bidding (CRÍTICO):**
   - NUNCA altere o orçamento diário de uma campanha em mais de +20% para cima ou -20% para baixo em um único ciclo semanal. Alterações bruscas resetam a fase de aprendizado dos algoritmos do Google e Meta.
2. **Prioridade Absoluta de Marca (Brand Defense):**
   - Campanhas `SEARCH_BRAND` devem ter prioridade máxima de orçamento. Se a perda de impressão por orçamento (`lost_is_budget`) for > 10%, aumente o orçamento em até 20% para proteger a busca do nome do hotel antes de alocar em Display ou PMax.
3. **Escala de Performance (PMax & Search):**
   - Se uma campanha PMax ou Search tiver `ROAS >= Target ROAS * 1.15` E `lost_is_budget >= 15%`, aumente seu orçamento em até +20%.
4. **Contenção e Realocação de Ineficiência:**
   - Campanhas com ROAS abaixo de 70% da meta ou Meta Ads com Frequência > 3.2 e CPA acima do limite devem sofrer redução de 15% a 20%. A verba liberada deve ser drenada para as campanhas vencedoras do mesmo hotel.
5. **Conservação do Orçamento Mensal:**
   - A soma dos orçamentos diários propostos de um hotel multiplicada por 30 não deve estourar o `monthly_budget_brl` configurado.
6. **Racional Baseado em Dados:**
   - Cada ação DEVE ter um campo `rationale` citando os números exatos (ex: "ROAS de 12.0 superou meta de 9.0 com 28% de perda de impressão por orçamento").

---

### FORMATO DE SAÍDA:
Responda EXCLUSIVAMENTE com um documento JSON válido correspondente ao schema do PortfolioOptimizationPlan, sem blocos markdown desnecessários fora do JSON.
"""
