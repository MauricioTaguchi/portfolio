# Sales CSV validation / Validação de vendas

Exemplo didático com dados sintéticos, sem dependências externas. Python 3.11+; verificado localmente com Python 3.13.5. Não usa dados de empresas ou clientes.

## Executar

Abra o terminal nesta pasta. No Windows, use `py` no lugar de `python` caso necessário.

```sh
python -m unittest -v
python validate_sales.py sales_valid.csv
python validate_sales.py sales_invalid.csv --output report.json
```

O arquivo válido retorna código 0. O arquivo inválido retorna código 1 **por projeto**: são 6 registros e 5 ocorrências de problemas, incluindo as duas ocorrências do ID repetido. Código 2 significa problema de entrada, configuração ou escrita. O comando não corrige o arquivo nem o regrava.

Contrato: colunas exatas `sale_id,date,amount_brl`, nesta ordem; ID não vazio e único; data real `YYYY-MM-DD`; valor positivo com até duas casas decimais. Não aceita separador de milhar, símbolo de moeda ou notação científica. Espaços externos são ignorados apenas na validação; zeros à esquerda do ID são preservados. A regra de valor positivo é específica deste exemplo de vendas pagas: devoluções exigem outro contrato.

Para CSV brasileiro com ponto e vírgula e vírgula decimal:

```sh
python validate_sales.py vendas.csv --delimiter ";" --decimal-separator ","
```

`record` conta registros sem o cabeçalho. `line_end` é a última linha física do registro, inclusive quando existem campos entre aspas com quebras de linha. `complete: false` indica interrupção estrutural ou limite; não trate o resultado como validação integral.

## Limitações

Amostra em memória, até 10 MiB de arquivo regular e 100.000 registros. O limite de tamanho é conferido antes da leitura; não é uma defesa contra arquivo alterado simultaneamente. Não valida existência da venda, total conciliado, CPF, integridade referencial, regras fiscais ou autorização de acesso. Não é ferramenta de segurança para arquivos hostis nem substitui requisitos de produção. A confirmação de tipo/data não prova a correção do negócio.

O relatório inclui nomes de campos e posições, mas não copia os valores brutos dos registros. Preserve acesso restrito ao CSV real. Não publique dados pessoais ao abrir uma issue.

Fontes técnicas: https://docs.python.org/3/library/csv.html e https://docs.python.org/3/library/decimal.html.
