# Plano de execução e ordem de desenvolvimento

1. **Fundação do projeto** — criar ambiente Python, dependência Flask, inicialização e configuração.
2. **Persistência** — criar banco SQLite, tabelas, chaves estrangeiras, dados iniciais e configurações.
3. **Autenticação e perfis** — cadastro/login, sessão e autorização de cliente, atendente e administrador.
4. **Catálogo** — cardápio, categorias, produtos e preços.
5. **Carrinho e personalização** — ingredientes opcionais, quantidade, atualização e remoção.
6. **Checkout** — retirada/entrega, dados de contato, pagamento simulado e cupons.
7. **Operação da cafeteria** — fila central, detalhes do pedido e atualização de status.
8. **Experiência do cliente** — acompanhamento periódico, favoritos, histórico e avaliação.
9. **Administração** — CRUD de produtos, cupons, relatórios e horários.
10. **Interface e responsividade** — identidade visual La Petite Douceur, navegação e telas adaptáveis.
11. **Documentação** — README, mapeamento das US, dicionário de dados e roteiro de testes.
12. **Validação** — executar testes manuais, registrar evidências e corrigir problemas encontrados.

## Organização arquitetural
- `app/routes.py`: controladores HTTP e fluxo de aplicação (MVP compacto).
- `app/auth.py`: autenticação/autorização.
- `app/db.py`: conexão, esquema e inicialização do banco.
- `app/templates/`: camada de apresentação (templates Jinja).
- `app/static/`: CSS e JavaScript do navegador.
- `instance/`: banco local gerado automaticamente.

A arquitetura segue separação MVC simplificada: templates como View, rotas como Controller e SQLite/acesso a dados como Model. Para a entrega acadêmica, complementar com diagrama UML de classes/casos de uso e diagrama entidade-relacionamento.
