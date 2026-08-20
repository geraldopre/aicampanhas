# 🏨 Agente Gerente de Mídia de Performance - Grupo Wish

Sistema autônomo em Python para análise semanal de performance e realocação inteligente de orçamento entre canais de mídia (Google Ads Search, PMax, Display, Meta Ads, TikTok e Bing) para os 9 hotéis da rede Grupo Wish.

---

## 🏗️ Arquitetura em 4 Camadas

1. **Ingestão (`connectors/`):** Coleta métricas de 7 dias via Google Ads API, Meta Graph API e conector Mock realista.
2. **Cérebro Analítico (`agent/`):** Motor de raciocínio com LLM (Gemini 2.5 / Claude / GPT-4o) gerando diagnósticos e ações estruturadas em JSON.
3. **Governança & Guardrails (`agent/guardrails.py`):** Trava de segurança de ±20% de variação, proteção de Search Brand (Impression Share > 85%) e pacing mensal.
4. **Notificação e Execução (`notifications/` & `executor/`):** Cartões de aprovação 1-click no Slack e mutação de orçamentos com Dry-Run e log de auditoria.

---

## 🚀 Instalação e Execução Rápida

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente (Opcional)
Copie o arquivo `.env.example` para `.env` e adicione suas chaves caso queira usar APIs reais ou LLMs externos:
```bash
GEMINI_API_KEY=sua_chave_gemini
# ou OPENAI_API_KEY / ANTHROPIC_API_KEY
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

> **Nota:** Sem nenhuma chave configurada, o agente opera automaticamente usando o **Conector Mock Realista** e o **Motor Heurístico Determinístico**, permitindo testar e validar 100% das regras imediatamente.

### 3. Rodar a simulação completa (Dry-Run)
```bash
python sample_run.py
```

### 4. Executar via CLI com parâmetros
```bash
# Executar apenas para o Wish Foz do Iguaçu em modo simulação
python -m hotel_media_agent.main --hotel wish_foz

# Executar para todos os hotéis e enviar cartão para o Slack
python -m hotel_media_agent.main --slack

# Executar e aplicar alterações reais em produção (requer credenciais)
python -m hotel_media_agent.main --live --execute
```

---

## 📊 Hotéis Configurados (`config/hotels_config.json`)

1. **Wish Foz do Iguaçu** (Foz do Iguaçu - PR)
2. **Wish Serrano Gramado** (Gramado - RS)
3. **Wish Natal** (Natal - RN)
4. **Wish Hotel da Bahia** (Salvador - BA)
5. **Prodigy Santos Dumont** (Rio de Janeiro - RJ)
6. **Prodigy Gramado** (Gramado - RS)
7. **Linx Galeão** (Rio de Janeiro - RJ)
8. **Linx Confins** (Belo Horizonte - MG)
9. **Marupiara Resort** (Porto de Galinhas - PE)
