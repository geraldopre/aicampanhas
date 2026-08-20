import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from hotel_media_agent.main import run_pipeline

if __name__ == "__main__":
    print("Iniciando demonstração do Agente de Mídia de Performance para o Grupo Wish...")
    run_pipeline(
        hotel_filter=None,       # Executa para todos os 9 hotéis
        dry_run=True,            # Modo Simulado seguro
        send_slack=False,        # Sem envio real de webhook por padrão
        auto_execute=True        # Registra as ações no log de auditoria
    )
