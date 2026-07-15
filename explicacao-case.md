Para construir o projeto, usei Python com FastAPI, coloquei tudo no Docker para facilitar a execução em qualquer máquina, e integrei com o modelo de LLM LLaMA 3.1 8b. Fiz uma interface simples e intuitiva usando HTML. Usei a API da Groq para garantir que as respostas fossem mais rápidas e no formato correto. No `README` do projeto eu explico o passo a passo de como rodar.

Como o tempo era curto, foquei em deixar a base do sistema funcionando bem. Mas, pensando em como isso funcionaria no mundo real da empresa, eu faria as seguintes melhorias se tivesse mais tempo:

1. Interface mais interativa: Hoje o teste usa mensagens prontas (mockadas) com exemplos de mensagens para testar o funcionamento da LLM. O primeiro passo seria criar um campo de texto no frontend para que qualquer pessoa pudesse digitar uma mensagem na hora e ver a IA trabalhando.
2. Salvar o histórico: Conectar a aplicação a um banco de dados como PostgreSQL para não perdermos o registro de tudo o que a IA leu e classificou.
3. Revisão Humana: Criaria uma tela onde as mensagens com confiança "Baixa" caíssem para a revisão de um atendente humano, evitando erros em casos duvidosos.
4. Fila de mensagens: Pensando em um volume muito alto de clientes mandando mensagem ao mesmo tempo, seria legal colocar um sistema de filas no servidor para garantir que ele não trave com o excesso de acessos.
5. Segurança e LGPD: Faria um filtro simples no código para "esconder" ou apagar dados sensíveis (como CPFs e valores) da mensagem original antes de mandar o texto para a IA, garantindo a privacidade dos clientes.
