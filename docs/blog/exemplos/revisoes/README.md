# Content is not revision / Conteúdo não é revisão

Modelo didático em memória, separado da implementação do DataFlow. Python 3.11+, sem dependências.

```sh
python -m unittest -v
python revision_demo.py
```

Saída esperada: `Restored original content as revision 3; replay kept head at revision 4.`

A sequência cria revisão 1, aplica revisão 2 e restaura o conteúdo da 1 como revisão 3. Após outra alteração, a repetição da mesma solicitação retorna o recibo anterior sem alterar a revisão 4.

Os oito testes verificam avanço de revisão, repetição, conflito de chave, versão antiga, alvo inexistente, chave vazia e identidade de conteúdo. NÃO validam transações, múltiplos processos, persistência, autorização, recuperação após falha, retenção ou corrupção de arquivos. As chaves deste exemplo pertencem a uma única instância; produção precisa definir o escopo por usuário, recurso e operação.

Referência do projeto: https://github.com/MauricioTaguchi/data-analytics-platform/blob/main/docs/AUDIT_RECEIPTS.md
