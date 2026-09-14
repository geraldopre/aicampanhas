# Análise v2 — Geraldo Prezoto (`geraldopre`)

**Projeto:** Agente Gerente de Mídia de Performance — Grupo Wish (9 hotéis)
**Repositório:** [geraldopre/aicampanhas](https://github.com/geraldopre/aicampanhas)
**Arquivo novo analisado:** `proposta_agente_midia_wish_v2.pptx` (commit `ca0a37bf`, 14/09) — 16 slides
**Nota v1:** 5,2/10 → **Nota v2: 6,5/10**

---

## 1. Abertura

Geraldo, esta atualização é só um documento novo — nenhum arquivo de código foi tocado (confirmei via diff do commit: só o pptx foi adicionado). Mas é um documento substancialmente melhor no ponto que mais pesava contra você na v1: viabilidade econômica, que estava praticamente ausente, agora tem uma modelagem de custo e retorno das mais rigorosas que vi nesta turma — inclusive com defesa proativa contra objeções ("antecipando as perguntas do comitê"). Isso justifica uma subida real de nota.

O que não mudou — porque não podia mudar, já que nenhum código foi alterado — é a lacuna mais séria da v1: o deck continua descrevendo o "Cérebro Analítico com IA" como componente operacional ("Fase 1 — Concluída"), sem nunca mencionar que a demonstração entregue roda 100% no motor heurístico determinístico, nunca invocando de fato nenhum LLM. Isso é o mesmo ponto da v1, agora reforçado por um material ainda mais detalhado.

## 2. O que este novo material traz

### 2.1 Viabilidade econômica — de ausente para uma das mais rigorosas da turma

Três slides novos constroem o caso de negócio que faltava por completo na v1:

- **Slide 11 (Transparência de custo de IA)**: modela consumo real de tokens (~540 mil de entrada, ~240 mil de saída/mês, mix Haiku 4.5/Sonnet 5 via Batch API), com preços de referência por milhão de tokens e câmbio explícito — chegando a R$100-200/mês mesmo com "erro de 10x" de margem de segurança. É uma estimativa de custo recorrente genuína, algo que a v1 não tinha em lugar nenhum.
- **Slide 12 (Payback e ROI)**: ancorado no investimento real de mídia (R$265 mil/mês, "a média dos reports semanais, não R$300 mil") e no ROAS consolidado real (3,05), não nos 9-12x das campanhas de topo — uma escolha deliberadamente conservadora que blinda a conta contra contestação.
- **Slide 13 (Antecipando objeções)**: lista e responde preventivamente as 6 perguntas mais prováveis de um comitê de aprovação, incluindo "o ROAS de 9-12x é otimista?" e "o +25% é promessa?" — o deck já assume o ônus da prova, em vez de deixar isso para depois.

Uma ressalva: a memória de cálculo exata do payback ("~1,5 mês com receita incremental; ~4 meses no cenário só-economia") não é totalmente reconstituível a partir só dos números do slide — vale pedir a planilha/fórmula por trás, para conferir com precisão.

### 2.2 O que continua sem resposta — e agora com um material mais elaborado ao redor

O slide 15 (Roadmap) declara "Fase 1 — Concluída: Motor analítico, guardrails, dashboard web e simulador Dry-Run operacionais". Isso é impreciso da mesma forma que a v1 já apontava: o "motor analítico" com LLM nunca é de fato exercitado na demonstração entregue (confirmado na v1: sem chave de API configurada, o sistema opera inteiramente via `_heuristic_fallback`) — e nenhum código mudou desde então para alterar isso. O slide 11, inclusive, aprofunda esse ponto: ao modelar custos de tokens de Haiku/Sonnet como se fossem consumo real mensal, o deck reforça implicitamente a impressão de que o LLM já opera em produção, sem a mesma ressalva que o `README.md` já fazia honestamente.

Isso não é fabricação de números (a modelagem de custo em si é bem feita, caso o LLM de fato rodasse) — é a mesma omissão da v1, agora dentro de um material mais sofisticado e mais próximo de decisão de investimento real, o que a torna mais relevante, não menos.

## 3. Nota por critério (apenas os itens que mudaram)

### Critérios de negócio (peso maior)

**1. Aderência ao negócio — 8,7/10** *(v1: 8,3/10)*
1.3. Conexão entre métrica técnica e impacto de negócio: **4** *(v1: 3)* — o "+15% a +25%" continua sendo uma expectativa, mas agora explicitamente rotulada como "potencial... medido nos 15 dias de Dry-Run antes de qualquer cobrança de sucesso" (slide 9) — uma forma honesta de apresentar uma projeção não validada, melhor que a v1, que não tinha essa ressalva.

**2. Viabilidade econômica (ROI) — 8,0/10** *(v1: 1,9/10)*
2.1. Custo de construção: **4** *(v1: 1)* — setup de R$12.000-20.000 conforme o modelo de contratação (slide 14), com "total no primeiro ano" quantificado (slide 10).
2.2. Custo de sustentação: **5** *(v1: 1)* — modelagem de custo de tokens de IA bem fundamentada e com margem de segurança explícita (slide 11) — melhor prática de estimativa de custo recorrente vista nesta turma.
2.3. Retorno esperado: **4** *(v1: 4, mantido)* — agora com número em R$ (economia R$13,25 mil/mês, receita incremental ~R$39,75 mil/mês), ancorado em dados reais de mídia, não só % operacional.
2.4. Comparação custo vs. retorno: **4** *(v1: 1)* — payback e ROI apresentados e defendidos proativamente contra objeções, ainda que a memória de cálculo exata não seja totalmente reconstituível (seção 2.1 acima).

### Critérios técnicos — sem mudança (nenhum código foi alterado)

**3 a 9.** Mantidos exatamente como na v1 — os achados de código (motor heurístico como único caminho realmente executado, ausência de seed no `mock_connector.py`, bug de arredondamento no guardrail, dashboard estático) não foram tocados nesta rodada, pois nenhum arquivo de código mudou.

**9.1. Honestidade sobre o modo de operação real:** mantido em 3/5 — o README já era honesto; o deck (agora ainda mais elaborado) continua sem a mesma ressalva, e o slide 15 ("Fase 1 — Concluída") e o slide 11 (custo de tokens como se fosse consumo real) tornam essa omissão mais visível, não menos, num material agora mais próximo de decisão de investimento real.

## 4. Nota final

**6,5 / 10** *(v1: 5,2/10)* — O maior buraco da v1 — viabilidade econômica praticamente ausente — foi preenchido com um dos casos de negócio mais rigorosos que vi nesta turma: custo de IA modelado por token, ROI ancorado em dados reais de mídia (não nas campanhas de topo), e defesa proativa contra objeções de comitê. Isso justifica a subida de nota.

A nota não sobe mais porque a lacuna mais séria da v1 — o deck tratar o "Cérebro Analítico com IA" como componente operacional sem nunca mencionar que a demonstração entregue roda 100% no motor heurístico — não apenas persiste, como agora aparece dentro de um material mais elaborado e mais próximo de uma decisão real de investimento, o que a torna mais relevante de corrigir, não menos.

**Nível de maturidade: PoC/protótipo avançado, com um caso de negócio agora pronto para comitê.** Falta ainda o mesmo passo que faltava na v1: uma execução real, mesmo que limitada, comparando decisão do LLM vs. decisão heurística — e, agora que o deck está pronto para ser apresentado a investidores/comitê, é ainda mais importante que ele diga com todas as letras que isso ainda não foi testado.

## 5. O que falta para uma v3

1. **Adicione ao deck (não precisa ser um slide inteiro, uma nota de rodapé já resolve) a mesma ressalva que o README já tem**: a demonstração atual roda 100% no motor heurístico, sem nenhuma chamada real ao LLM.
2. **Mostre a memória de cálculo do payback** (slide 12) — hoje o "~1,5 mês" e "~4 meses" não são totalmente reconstituíveis a partir dos números apresentados.
3. Os itens de código da v1 (seed do mock connector, bug do guardrail, dashboard estático) seguem de pé — ver task list da análise original.
