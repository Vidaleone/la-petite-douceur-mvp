# La Petite Douceur — MVP acadêmico

Aplicação web de pedidos para cafeteria/doceria, construída com **Python + Flask + SQLite**, organizada em camadas de rotas/controladores, autenticação, acesso a dados e templates (MVC simplificado).

## Requisitos
- Python 3.10 ou superior
- pip

## Como executar no Windows
1. Extraia o ZIP para uma pasta, por exemplo `C:\Projetos\la_petite_douceur_mvp`.
2. Abra o terminal nessa pasta.
3. Crie o ambiente virtual:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   ```
4. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
5. Inicie:
   ```powershell
   py run.py
   ```
6. Acesse `http://127.0.0.1:5000`.

O banco SQLite e os dados iniciais são criados automaticamente em `instance/cafeteria.sqlite3` na primeira execução.

## Acesso administrativo inicial
- E-mail: `admin@lapetitedouceur.com.br`
- Senha: `Admin123!`

Altere a senha e a chave secreta antes de qualquer implantação pública. Esta conta é apenas para demonstração acadêmica local.

## Fluxo recomendado de teste
1. Entre como administrador e abra **Painel > Produtos**. Cadastre/edite um produto.
2. Saia e crie uma conta de cliente em **Entrar > Cadastre-se**.
3. Abra o cardápio, personalize ingredientes e adicione itens.
4. Abra o carrinho, atualize quantidades e finalize com retirada/entrega e Pix/cartão demonstrativos.
5. Em outra aba, entre como administrador e abra **Pedidos / cozinha**. Mude o status.
6. Volte ao cliente: a tela de acompanhamento atualiza o status automaticamente.
7. Marque favoritos, consulte histórico, finalize o pedido e envie avaliação.
8. No painel admin, teste cupons, horários e relatórios.

## Funcionalidades implementadas
- US01 cardápio com categorias, descrição e preço.
- US02 personalização de ingredientes disponíveis (adicional demonstrativo de R$ 1 por ingrediente).
- US03 carrinho com quantidades e remoção.
- US04 retirada ou entrega com endereço obrigatório para entrega.
- US05 escolha de Pix ou cartão em modo simulado; não há gateway nem cobrança.
- US06 acompanhamento de status com atualização automática a cada 5 segundos.
- US07 fila de pedidos para a equipe da cozinha.
- US08 cadastro, edição, preço e desativação de produtos.
- US09 favoritos por conta.
- US10 histórico de pedidos por conta.
- US11 atualização do status pela equipe.
- US12 relatório diário, produtos mais vendidos e média de avaliações.
- US13 cupons percentuais ou de valor fixo, mínimo e validade.
- US14 avaliação de pedidos finalizados.
- US15 configuração de horários de funcionamento.

## Perfis
- `admin`: acesso completo ao painel.
- `staff`: fila da cozinha, atualização de status e consulta de avaliações.
- `customer`: cardápio, pedidos, favoritos, histórico e avaliações.

## Observações importantes
- A aplicação é um MVP acadêmico local, não um sistema pronto para operação comercial.
- Pix/cartão são apenas opções registradas no pedido; não existe integração bancária.
- A atualização de status usa consulta periódica (polling), suficiente para demonstração acadêmica.
- O cadastro de atendentes e recuperação de senha ainda não têm telas administrativas.
- Para uso público real, adicionar proteção CSRF, limitação de tentativas de login, configuração segura de `SECRET_KEY`, HTTPS, política de privacidade, testes automatizados e revisão de segurança.
- O horário de funcionamento é configurável e exibido ao cliente; o MVP não bloqueia a finalização fora do horário, para permitir testes acadêmicos a qualquer momento.


## Temas visuais
A interface oferece tema claro e tema escuro por meio do botão minimalista ao lado da marca no cabeçalho. O tema claro combina creme, terracota, azul-bebê e amarelo banana; o tema escuro utiliza marrom chocolate, terracota, creme, azul-bebê e amarelo banana. A escolha é salva no navegador e aplicada em todas as páginas, incluindo autenticação, pedidos e administração. O registro acadêmico da melhoria sugerida por usuário-teste e o roteiro do segundo vídeo estão em `docs/REGISTRO_MELHORIA_AVALIADOR.md`.
