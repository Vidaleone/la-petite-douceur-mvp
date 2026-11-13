# Mapeamento das histórias de usuário — PIT1 → MVP PIT2

| ID | História de usuário preservada | Implementação no MVP | Evidência para teste |
|---|---|---|---|
| US01 | Cliente visualiza cardápio com fotos/preços | Página `/cardapio`, categorias, descrição, preço e emoji ilustrativo | Abrir cardápio |
| US02 | Cliente personaliza ingredientes | Opções por produto; adicional demonstrativo de R$ 1 por ingrediente | Marcar ingredientes e adicionar |
| US03 | Cliente adiciona itens ao carrinho | Carrinho por sessão, quantidade, atualização e remoção | Adicionar dois produtos e alterar quantidade |
| US04 | Cliente escolhe retirada ou delivery | Checkout com retirada/entrega e endereço obrigatório | Finalizar um pedido em cada modalidade |
| US05 | Cliente escolhe cartão ou Pix | Opção armazenada no pedido; simulação sem cobrança | Finalizar com cada opção |
| US06 | Cliente acompanha status em tempo real | Tela de pedido consulta status a cada 5 segundos | Alterar status no admin e observar cliente |
| US07 | Atendente recebe pedidos em tela central | Fila `/admin/pedidos` | Criar pedido e abrir fila |
| US08 | Admin gerencia produtos/preços | CRUD simplificado: cadastrar, editar e desativar | Cadastrar e editar produto |
| US09 | Cliente salva favoritos | Favoritos vinculados à conta | Favoritar e consultar |
| US10 | Cliente consulta histórico | Histórico individual de pedidos | Consultar `/historico` |
| US11 | Atendente altera status | Atualização de status na fila | Alterar recebido → preparação → pronto |
| US12 | Admin consulta relatórios | Vendas por dia, produtos mais vendidos e avaliações | Abrir relatórios |
| US13 | Cliente usa cupons | Cupons percentuais/fixos, mínimo e validade | Criar cupom e aplicar no checkout |
| US14 | Cliente avalia pedido | Avaliação de 1 a 5 e comentário após finalização | Finalizar e avaliar |
| US15 | Admin define horário de funcionamento | Configuração semanal no painel | Alterar horário e verificar início |

## Regras de escopo
- US05 é simulação acadêmica, sem integração financeira.
- US06 usa polling de 5 segundos; não é WebSocket.
- US02 usa uma lista de ingredientes disponíveis por produto e valor adicional fixo ilustrativo.
- O status “Saiu para entrega” é utilizado em pedidos delivery; a equipe seleciona o status manualmente.
- A lista de US deve ser reavaliada depois da conclusão e dos testes, conforme combinado.
