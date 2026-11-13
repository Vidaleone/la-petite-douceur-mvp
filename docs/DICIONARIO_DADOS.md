# Dicionário de dados — SQLite

| Tabela | Campo | Tipo | Regra / finalidade |
|---|---|---|---|
| users | id | INTEGER PK | Identificador |
| users | name | TEXT | Nome |
| users | email | TEXT UNIQUE | Login |
| users | password_hash | TEXT | Hash seguro da senha |
| users | role | TEXT | customer, staff ou admin |
| products | id | INTEGER PK | Identificador |
| products | name/category/description | TEXT | Dados do produto |
| products | price | REAL | Preço não negativo |
| products | active | INTEGER | 1 ativo / 0 desativado |
| products | ingredients | TEXT JSON | Ingredientes selecionáveis |
| orders | id | INTEGER PK | Identificador |
| orders | user_id | INTEGER FK | Cliente que fez o pedido |
| orders | fulfillment | TEXT | retirada ou entrega |
| orders | payment | TEXT | pix ou cartao (simulado) |
| orders | status | TEXT | Etapa operacional |
| orders | subtotal/discount/total | REAL | Valores do pedido |
| order_items | order_id | INTEGER FK | Pedido relacionado |
| order_items | product_id | INTEGER FK | Produto, pode ficar nulo se removido |
| order_items | product_name | TEXT | Cópia do nome no momento da compra |
| order_items | quantity/unit_price | INTEGER/REAL | Quantidade e preço congelado |
| order_items | customizations | TEXT JSON | Ingredientes escolhidos |
| favorites | user_id/product_id | INTEGER FK | Relação cliente-produto |
| coupons | code | TEXT UNIQUE | Código do cupom |
| coupons | kind/value | TEXT/REAL | Percentual ou valor fixo |
| reviews | order_id/user_id | INTEGER FK | Pedido avaliado e autor |
| reviews | rating/comment | INTEGER/TEXT | Nota de 1 a 5 e comentário |
| settings | key/value | TEXT | Configurações, incluindo horários |

As datas são armazenadas como texto ISO gerado pelo SQLite (`CURRENT_TIMESTAMP`). Valores monetários usam REAL para manter o MVP simples; em produção, preferir centavos inteiros ou DECIMAL.
