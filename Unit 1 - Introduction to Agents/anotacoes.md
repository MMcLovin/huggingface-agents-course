# Unit 1 - Introduction to Agents (Anotações)

## Dia 02/11

Baixei o Ollama com `irm https://ollama.com/install.ps1 | iex`. Vou tentar rodar o `qwen2.5:7b` localmente em vez de usar a API deles.

A documentação do Hugging Face está um pouco diferente da do Ollama. No HF eles mandam dar um `pull` no modelo que a gente quer, depois dar um `ollama serve` para subir o Ollama e depois dar um `pip install 'smolagents[litellm]'` e daí a gente executa:

```python
from smolagents import LiteLLMModel

model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",  # Or try other Ollama-supported models
    api_base="http://127.0.0.1:11434",  # Default Ollama local server
    num_ctx=8192,
)
```

O problema é que na documentação do Ollama só fala do `ollama run <model>`. Segundo o Gemini, é isso aí mesmo: se eu der `ollama run qwen2:7b`, ele vai simplesmente abrir um chat para o modelo e já subir um servidor local. O `smolagents` é justamente a API de comunicação do Python com o modelo rodando no servidor local. Então o que eu vou fazer é dar o `ollama run qwen2:7b` e depois tentar rodar o código do `smolagents` pra ver se ele consegue se comunicar com o modelo.

---

## Dia 09/11

Olha, foi realmente interessante entender mais sobre como funciona uma LLM por debaixo dos panos. A interface e interação em modo de chat que nós vemos é uma abstração do que realmente acontece. Quando nós mandamos uma mensagem, tanto o prompt quanto a resposta são concatenados e enviados para o modelo no prompt seguinte, por isso que dizem que eles são *stateless*. O modelo não tem memória do que aconteceu antes, ele só recebe o prompt atual e gera uma resposta com base nele. A "memória" que vemos é construída pelo próprio usuário, que precisa manter o contexto das conversas. Por isso também que quanto maior for o seu chat, pior será a performance do modelo, pois ele terá que processar mais informações para gerar uma resposta, já que o contexto é usado no cálculo de probabilidade para escolha da resposta.

Prompts possuem tokens reservados que são usados para delimitar o início e o fim de uma conversa, e também para indicar instruções especiais para o modelo. Por exemplo, alguns modelos usam tokens específicos para indicar que a próxima entrada é uma pergunta ou uma instrução, enquanto outros podem usar tokens para separar diferentes partes do prompt.

---

## Dia 14/11

Cara, é interessante o porquê de usar linguagem de programação para definir uma *tool*: porque é muito expressiva, conseguimos dizer muito mais com muito menos verbosidade do que redigindo um texto, além de ser menos ambíguo. Exemplo:

```python
@tool
def calculator(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

print(calculator.to_string())
```

O `@tool` já diz que aquilo é uma *tool* que o agente pode usar. O nome da função já passa uma ideia do que ela faz. O *type hint* já nos diz o que ela espera como parâmetros e o que ela retorna. A *docstring* já nos dá uma descrição do que a função faz. E o retorno da função é o resultado da operação. Tudo isso é muito mais expressivo do que escrever um texto descrevendo a função. E o `to_string()` ainda pode nos gerar uma representação textual da função, que pode ser usada para documentação ou exibir informações de uma forma mais legível:

```python
print(calculator.to_string())
# Output:
# Tool Name: calculator, Description: Multiply two integers., Arguments: a: int, b: int, Outputs: int
```

Interessante, não lembrava que em Python a gente pode passar uma função como argumento. Aparentemente, funções possuem tipo de dado próprio (`callable`).

Na seção *"What are Tools?"*, eles mostram como podemos montar um decorator para automatizar a criação e descrição de uma *tool*, usando `inspect` do Python para inspecionar a função e extrair informações sobre ela como nome, *docstring*, *type hints* e etc. É tipo reflexão em Java.

Acho que é a melhor explicação que vi até agora sobre **Model Context Protocol (MCP)**. É um protocolo de especificação de *tools* para um modelo, ficando agnóstico de linguagem de programação, framework ou modelo. Ele define como as *tools* devem ser descritas e como o modelo deve interagir com elas.

> Curiosidade: o protocolo MCP foi criado por engenheiros da Anthropic (Cláudin) e o projeto foi doado/entregue para a comunidade open source Linux Foundation no final de 2025.

Eu achei a nomenclatura **ReAct** muito ruim, ela vem de *Reasoning + Acting*, mas o "Re" fica parecendo de *"repeat"*, como se fosse agir de novo ou mais de uma vez. Mas é interessante, eles mostram um exemplo de um mesmo prompt e o output gerado por diferentes estratégias como **CoT (*Chain of Thought*)** e **ReAct**.

A principal diferença que eles mostram entre essas estratégias é de que o CoT não utiliza *tools* no processo, enquanto o ReAct utiliza.

| Feature | Chain-of-Thought (CoT) | ReAct |
| :--- | :---: | :---: |
| **Step-by-step logic** | ✅ Yes | ✅ Yes |
| **External tools** | ❌ No | ✅ Yes (Actions + Observations) |
| **Best suited for** | Logic, math, internal tasks | Info-seeking, dynamic multi-step tasks |

É muito engraçado que meio que apenas calhou de programação ser a ferramenta/meio mais útil para LLMs. Na seção de *"Actions: Enabling the Agent to Engage with Its Environment"*, eles mostram o processo de um agente executando uma tarefa com `Text/JSON` e *Tools*, só que a gente acaba percebendo que é apenas um processo bem estruturado para a resolução de um problema, ou seja: literalmente a definição de algoritmo. Daí eles mostram um agente de código usando Python para resolver o mesmo problema, mas com uma linguagem de programação de alto nível. E isso torna tudo mais fácil: melhor para debugar, mais expressividade, mais reusabilidade e etc.

Os modelos de inferência que eles sugerem que a gente use agora são todos pagos aparentemente, então eu adaptei a chamada à Serverless API para o meu Ollama local que baixei lá no início, pô achei legal demais isso kkkkkk.

No exemplo do *Dummy Agent*, surgiu uma dúvida porque o tutorial interrompe a geração do modelo com `stop=["Observation:"]` e, logo em seguida, chama a função `get_weather("London")` de forma *hardcoded* no prompt da segunda mensagem, dando a impressão de que a LLM não tomou a decisão da *tool* sozinha. Na prática, a parada forçada no `stop` serve para frear o modelo assim que ele escreve o JSON da *Action* (impedindo que ele continue escrevendo e alucine a *Observation* por conta própria), mas o tutorial pulou todo o processo de *parsing* que deveria existir entre as duas chamadas: o código Python deveria ler a string gerada na primeira requisição, extrair via código o JSON com a ferramenta (`get_weather`) e o argumento (`London`) que o próprio modelo escolheu, executar a função dinamicamente e só então concatenar o retorno real no histórico para a segunda chamada gerar a *Final Answer*.

> **Como a Lista `messages` Vira um Único Prompt (Chat Template)**  
> Passar uma lista `messages` com vários dicionários (`system`, `user`, `assistant`) não faz uma chamada ao modelo para cada item: cada execução de `client.chat.completions.create` realiza apenas uma requisição à API. Antes do envio, o método `chat` aplica um *chat template* que concatena todos os dicionários da lista em uma única string contínua, inserindo *special tokens* para marcar onde começa o texto de cada papel (`<|start_header_id|>`) e onde termina aquele turno de fala (`<|eot_id|>`). É por isso que o agente só faz duas chamadas no exemplo do curso: a primeira envia `system` + `user` juntos em um único prompt até esbarrar no `stop=["Observation:"]`, e a segunda envia `system` + `user` + `assistant` (já com o *Thought*, a *Action* e a *Observation* concatenados) em um novo prompt único para o modelo apenas terminar de escrever a *Final Answer*.
