# Registro de sugestão de usuário-teste e melhoria implementada

**Projeto:** La Petite Douceur — MVP acadêmico (PIT2)  
**Origem:** sugestão atribuída a usuário-teste, a ser consolidada na etapa de validação prevista na PIT2.  
**Melhoria implementada:** alternância global entre tema claro e tema escuro.

## Sugestão recebida

O usuário-teste sugeriu oferecer uma opção de tema escuro sem perder a identidade visual acolhedora da cafeteria. A proposta solicita manter o vermelho terroso/terracota como cor de destaque, adotar marrom chocolate escuro como base do tema noturno e harmonizar a interface com creme, azul-bebê e amarelo pastel (banana). Também foi solicitado um controle minimalista, sem texto, ao lado da marca no cabeçalho para alternar entre os temas.

## Implementação realizada

- Botão circular minimalista ao lado da logo, com ícone de lua/sol, sem texto visível e com rótulos acessíveis (`aria-label`, `title` e `aria-pressed`).
- Tema claro com fundo creme, superfícies claras, azul-bebê em áreas de apoio, amarelo banana em realces e terracota em botões, links e destaques.
- Tema escuro com fundo marrom chocolate, superfícies em tons de cacau, terracota em destaques, creme para textos, azul-bebê em áreas secundárias e amarelo banana em realces.
- Alternância aplicada globalmente por variáveis CSS, incluindo cabeçalho, navegação, botões, formulários, campos, tabelas, mensagens, cartões, filtros, menus administrativos, pedidos, login/cadastro, rodapé e demais páginas.
- Preferência armazenada no `localStorage` e restaurada ao navegar entre as telas e ao reabrir o sistema no mesmo navegador.
- Tema aplicado no início do carregamento da página para reduzir o clarão de troca visual.
- A melhoria não altera regras de negócio, dados, autenticação ou fluxo dos pedidos.

## Roteiro de evidência — segundo vídeo da PIT2

Esta melhoria será demonstrada no **segundo vídeo solicitado na PIT2**, dedicado às melhorias implementadas após a avaliação por usuários-teste. Sugestão de sequência para a gravação:

1. Apresentar a sugestão recebida do usuário-teste.
2. Mostrar o controle de tema ao lado da logo.
3. Alternar do tema claro para o escuro e destacar a paleta chocolate, terracota, creme, azul-bebê e amarelo banana.
4. Navegar entre início, cardápio, carrinho e login, mostrando que a preferência permanece.
5. Entrar na administração e demonstrar menus, tabelas, formulários e atualização de pedidos nos dois temas.
6. Retornar ao tema claro e encerrar mostrando a persistência da preferência.

> **Registro acadêmico:** preencher com os dados reais do avaliador, data da avaliação e evidência original da sugestão após a aplicação do teste. Não inventar nome, data, resposta ou resultado de participante.

## Critérios de validação da melhoria

- O botão alterna os temas sem recarregar a página.
- O tema selecionado permanece ao navegar para outras rotas.
- O tema selecionado é restaurado ao reabrir o navegador.
- Texto, botões, campos, menus, tabelas e mensagens permanecem legíveis nos dois temas.
- A alternância funciona nas páginas públicas, autenticação, pedidos e administração.
