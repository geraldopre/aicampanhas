import argparse
import json
import logging
import sys
from pathlib import Path
from tabulate import tabulate

from hotel_media_agent.config import settings
from hotel_media_agent.connectors.google_ads_client import GoogleAdsClient
from hotel_media_agent.connectors.meta_ads_client import MetaAdsClient
from hotel_media_agent.connectors.mock_connector import MockAdConnector
from hotel_media_agent.agent.reasoning_engine import MediaReasoningEngine
from hotel_media_agent.notifications.slack_notifier import SlackNotifier
from hotel_media_agent.executor.mutation_executor import MutationExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("hotel_media_agent")

def load_hotels_config():
    config_path = Path(__file__).parent / "config" / "hotels_config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {h["hotel_id"]: h for h in data["hotels"]}, data["hotels"]

def run_pipeline(
    hotel_filter: str = None,
    dry_run: bool = True,
    send_slack: bool = False,
    auto_execute: bool = False
):
    print("\n" + "="*80)
    print(f"🏨 AGENTE GERENTE DE MÍDIA DE PERFORMANCE - GRUPO WISH")
    print(f"Modo: {'🔍 DRY-RUN (Simulação Segura)' if dry_run else '⚡ LIVE (Produção)'}")
    print("="*80 + "\n")

    hotels_map, hotels_list = load_hotels_config()

    if hotel_filter:
        if hotel_filter not in hotels_map:
            print(f"Erro: Hotel '{hotel_filter}' não encontrado na configuração.")
            sys.exit(1)
        target_hotels = [hotels_map[hotel_filter]]
    else:
        target_hotels = hotels_list

    # 1. Coleta de dados dos canais
    print(f"📊 1. Coletando dados dos últimos 7 dias de {len(target_hotels)} hotéis...")
    google_client = GoogleAdsClient()
    meta_client = MetaAdsClient()
    mock_client = MockAdConnector()

    hotels_performance_data = []

    for hotel in target_hotels:
        hotel_id = hotel["hotel_id"]
        # Se as APIs reais não estiverem configuradas, o conector usa mock automaticamente
        if google_client.initialized or meta_client.initialized:
            g_camps = google_client.fetch_weekly_performance(hotel)
            m_camps = meta_client.fetch_weekly_performance(hotel)
            campaigns = g_camps + m_camps
        else:
            campaigns = mock_client.fetch_weekly_performance(hotel)

        hotels_performance_data.append({
            "hotel_id": hotel_id,
            "hotel_name": hotel["name"],
            "destination": hotel["destination"],
            "targets": {
                "target_roas": hotel["target_roas"],
                "max_cpa_brl": hotel["max_cpa_brl"],
                "monthly_budget_brl": hotel["monthly_budget_brl"]
            },
            "campaigns": campaigns
        })

    # 2. Cérebro do Agente (Raciocínio & Guardrails)
    print("🧠 2. Processando insights e aplicando matriz de heurísticas + guardrails...")
    engine = MediaReasoningEngine()
    plan = engine.analyze_portfolio(hotels_performance_data, hotels_map)

    # 3. Exibir Resumo Executivo no Terminal
    print("\n" + "-"*80)
    print("📋 RESUMO EXECUTIVO DO PORTFÓLIO:")
    print(plan.global_executive_summary)
    print("-"*80 + "\n")

    # Tabela de Performance dos Hotéis
    table_hotels = []
    for h in plan.hotels:
        m = h.weekly_metrics
        status_icon = "🟢" if h.health_score == "HEALTHY" else ("🟡" if h.health_score == "ATTENTION" else "🔴")
        table_hotels.append([
            f"{status_icon} {h.hotel_name}",
            f"R$ {m.spend_brl:,.2f}",
            f"R$ {m.revenue_brl:,.2f}",
            f"{m.roas_actual:.1f}x",
            f"{m.roas_target:.1f}x",
            f"R$ {m.cpa_actual_brl:.2f}",
            f"R$ {m.cpa_max_brl:.2f}",
            m.bookings_count,
            len(h.actions)
        ])

    headers_hotels = ["Hotel", "Gasto (7d)", "Receita (7d)", "ROAS", "Meta ROAS", "CPA", "Max CPA", "Reservas", "Ações"]
    print(tabulate(table_hotels, headers=headers_hotels, tablefmt="fancy_grid"))

    # Tabela de Ações Propostas
    table_actions = []
    for h in plan.hotels:
        for a in h.actions:
            change_str = f"+{a.change_pct:.1f}%" if a.change_pct > 0 else f"{a.change_pct:.1f}%"
            table_actions.append([
                h.hotel_name[:18],
                a.platform.upper(),
                a.campaign_name[:30],
                f"R$ {a.current_daily_budget_brl:.2f}",
                f"R$ {a.new_daily_budget_brl:.2f}",
                change_str,
                a.priority,
                a.rationale[:60] + "..." if len(a.rationale) > 60 else a.rationale
            ])

    if table_actions:
        print("\n⚡ AÇÕES DE OTIMIZAÇÃO PROPOSTAS:")
        headers_actions = ["Hotel", "Canal", "Campanha", "Atual/dia", "Novo/dia", "Var (%)", "Prioridade", "Racional"]
        print(tabulate(table_actions, headers=headers_actions, tablefmt="grid"))
    else:
        print("\n✅ Nenhuma alteração de orçamento necessária na semana. Todas as campanhas estão operando no ponto ótimo.")

    # 4. Disparo de Notificações
    if send_slack:
        print("\n💬 4. Disparando cartão interativo para o Slack...")
        SlackNotifier.send_optimization_report(plan)

    # 5. Execução de Mutações
    if auto_execute:
        print(f"\n🚀 5. Executando {len(table_actions)} mutações de orçamento ({'MODO SIMULADO' if dry_run else 'PRODUÇÃO'})...")
        executor = MutationExecutor(dry_run=dry_run)
        results = executor.execute_plan(plan, hotels_map)
        print(f"✅ Execução concluída. {len(results)} registros salvos no log de auditoria em {settings.AUDIT_LOG_FILE}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente Gerente de Mídia de Performance - Grupo Wish")
    parser.add_argument("--hotel", type=str, help="Filtrar execução para um hotel específico (ex: wish_foz)")
    parser.add_argument("--live", action="store_true", help="Executa alterações em modo produção real (padrão é dry-run)")
    parser.add_argument("--slack", action="store_true", help="Envia o relatório para o webhook do Slack")
    parser.add_argument("--execute", action="store_true", help="Executa as alterações de orçamento propostas")

    args = parser.parse_args()
    run_pipeline(
        hotel_filter=args.hotel,
        dry_run=not args.live,
        send_slack=args.slack,
        auto_execute=args.execute
    )
