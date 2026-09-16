# Análise v3 — Geraldo Prezoto (`geraldopre`)

**Projeto:** Agente de gestão de mídia paga para 9 hotéis (LLM Gemini/GPT-4o/Claude + fallback heurístico determinístico)
**Repositório:** [geraldopre/aicampanhas](https://github.com/geraldopre/aicampanhas)
**Commit analisado:** `cd78e50` (16/09)
**Nota v1:** 5,2/10 → v2: 6,5/10 → **Nota v3: 7,0/10**

*Nota: rubrica adaptada — critérios 3, 4, 5, 7 e 9 têm sub-itens N/A onde a lógica de "modelo treinado" não se aplica a este projeto (agente de software, não rede neural).*

---

## 1. Abertura

Geraldo, esta rodada — como a v2 — trouxe só um arquivo novo (`proposta_agente_midia_wish_v2_revisada.pptx`), zero linhas de código tocadas. Comparei `ca0a37b...cd78e50` via `gh api compare` e confirmei: 0 additions/deletions em qualquer arquivo de código. Isso já é a segunda rodada seguida nesse padrão.

A boa notícia: o achado mais grave e recorrente das duas rodadas anteriores foi finalmente resolvido — mas na comunicação, não no código.

## 2. O achado mais crítico — LLM invocado ou não — finalmente admitido no deck

Confirmei de novo, com ambiente isolado (sem nenhuma API key configurada, reproduzindo o que qualquer avaliador teria): **a "IA" de fato demonstrada continua sendo 100% o motor heurístico determinístico.** `_call_llm` em `reasoning_engine.py` só tenta Gemini/OpenAI/Anthropic dentro de `if settings.GEMINI_API_KEY:` etc.; sem `.env`, as três chaves são string vazia, nenhuma chamada é sequer construída, e o log mostra diretamente "Executando motor heurístico determinístico de fallback."

O que mudou agora: pela primeira vez, o próprio deck diz isso com todas as letras — slide 11: *"A demonstração atual roda 100% no motor heurístico determinístico — nenhuma chamada real a LLM foi realizada até o momento."* E o roadmap (slide 15) reclassifica "Fase 1 — Concluída" como sendo apenas motor heurístico + guardrails + dashboard, sem alegar a camada de IA como pronta. Isso resolve diretamente o problema apontado nas duas rodadas anteriores (o README dizia uma coisa, o deck deixava outra impressão para quem decide investimento).

Vale reconhecer: é uma correção de honestidade genuína e bem-vinda — mas é comunicação, não engenharia. O software é idêntico ao da v1.

## 3. Os dois bugs técnicos da v1 — ainda não corrigidos, por duas rodadas seguidas

**Seed não fixada em `mock_connector.py`:** continua sem `random.seed(...)` em nenhum lugar do repositório. Duas execuções idênticas (mesmo input, mesma config) me deram resultados diferentes: receita do Marupiara Resort variando de R$92.550 para R$102.307, ROAS do Wish Natal de 10,8x para 10,6x, e até o número de ações propostas mudando (0 vs. 3) para o mesmo hotel.

**Guardrail "fantasma" em `guardrails.py`:** também não corrigido, e consegui isolar a causa exata desta vez. O motor calcula `new_b = round(current_b * 1.20, 2)`, e o guardrail recalcula independentemente o percentual de mudança sem tolerância a ponto flutuante — o arredondamento intermediário empurra o valor para algo como 20,0007%, sempre acima do limiar. Numa rodada limpa, **5 das 17 ações do log de auditoria (~29%) carregam a marca "[Guardrail: limitado a ±20%]" sem que nenhuma intervenção real tenha ocorrido** — o valor "clampado" é matematicamente idêntico ao já proposto. Além disso, as outras duas regras de guardrail (piso de orçamento, teto de pacing) nunca dispararam em nenhuma das minhas execuções — ou seja, 100% dos disparos já observados neste projeto (v1 e agora) são esse falso-positivo.

Os dois bugs são baratos de corrigir (uma linha de `random.seed()`; ajustar a ordem/tolerância do arredondamento) e foram sinalizados nominalmente nas duas rodadas anteriores sem nenhum código tocado.

## 4. O que mais mudou no pptx

- ROI recalibrado com mais rigor: orçamento de mídia baixou de "R$300 mil/mês" (v2, que a própria v3 reconhece como superestimado) para "R$265.000/mês" — número plausível frente à soma real de `monthly_budget_brl` em `hotels_config.json` (R$260.000/mês). O ROAS usado para payback também ficou mais conservador (3,05x, em vez do ROAS otimista de simulação).
- Slide de objeções antecipadas (orçamento, ROAS, promessa de crescimento, custo de IA, sazonalidade, confiança) com respostas específicas e coerentes com o resto do deck.
- Detalhe organizacional: o arquivo foi salvo em `revisao-professor/` em vez da raiz do repo (onde está o pptx da v2) — não afeta a nota, mas vale corrigir a organização.

## 5. Nota final

**7,0 / 10** *(v2: 6,5/10)* — incremento moderado, não equivalente ao salto da v2. A honestidade sobre o LLM — o achado mais grave e repetido duas vezes — foi finalmente corrigida, e o ROI ficou mais defensável. Mas isso é a segunda rodada seguida com zero esforço de engenharia: os dois bugs concretos e baratos de corrigir, sinalizados desde a v1, continuam intocados. Esta nota é um teto até que eles sejam corrigidos — não dá para continuar subindo só com ajuste de slide enquanto o código para.

## 6. O que preciso que você corrija para a próxima rodada

1. Fixe uma seed em `mock_connector.py` (`random.seed(...)` ou `np.random.seed(...)`, conforme o gerador usado) — sem isso, nenhum número deste projeto é reprodutível.
2. Corrija a tolerância de ponto flutuante em `guardrails.py` (ex.: comparar com uma margem de 1e-6, ou recalcular o percentual a partir dos mesmos valores não arredondados usados no motor) — o log de auditoria não pode inventar intervenções que não ocorreram.
3. Depois de corrigir os dois pontos acima, rode novamente e confirme que os disparos de guardrail refletem casos reais.
