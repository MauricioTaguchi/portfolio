# Maurício Taguchi — Portfólio

Portfólio pessoal com projetos em análise de dados, automação, engenharia e desenvolvimento.

## Desenvolvimento

Requisitos: Node.js 22.13 ou superior e pnpm 11.19.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

## Build e publicação

```sh
pnpm typecheck
pnpm build
pnpm preview
```

O build gera o site estático em `docs/`. Para publicar no GitHub Pages, selecione a branch `main` e a pasta `/docs` em Settings → Pages. Atualizações no código exigem um novo build e um commit dos arquivos gerados.

Os caminhos de recursos são relativos: o mesmo build funciona em um endereço de projeto e na raiz de um domínio próprio. O domínio canônico é `mauriciotaguchi.com.br`.

## Estrutura

- `src/portfolio.tsx`: seções e interações do portfólio.
- `src/portrait.tsx`: retrato e suporte opcional a uma sequência de imagens.
- `src/components/ui`: controles acessíveis baseados em Radix UI.
- `src/globals.css`: layout responsivo, estilos e preferência por movimento reduzido.
- `public/`: imagens locais e favicon.
- `vendor/`: estilos auxiliares com a licença original.

React, TypeScript e Vite compõem a aplicação. Tailwind CSS dá suporte aos controles da interface; GSAP e Lenis implementam animações e rolagem.

O formulário prepara uma mensagem localmente, permite copiá-la e abre o LinkedIn. Não envia e-mails nem grava os dados em um servidor. As interfaces dos projetos exibem dados demonstrativos. A sequência de retrato permanece opcional; com o manifesto vazio, é usada a imagem estática.

As licenças dos componentes e bibliotecas de terceiros continuam aplicáveis.
