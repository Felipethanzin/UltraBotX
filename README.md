# Prompt — Bot do Telegram com Sistema de Login

Crie uma aplicação completa de **Bot para Telegram**, com visual moderno e sistema de autenticação.

## Objetivo

Desenvolver um bot integrado ao Telegram que permita aos usuários criar uma conta, fazer login e acessar funcionalidades através de comandos e botões interativos.

## Tecnologias

Utilize:

* **Node.js**
* **JavaScript**
* **Telegram Bot API**
* **Express.js**
* **PostgreSQL**
* **JWT para autenticação**
* **bcrypt para criptografia de senhas**
* **HTML, CSS e JavaScript** para o painel web
* Interface moderna e responsiva

## Sistema de Cadastro

O usuário deverá conseguir criar uma conta informando:

* Nome completo
* Nome de usuário
* E-mail
* Senha
* Confirmação de senha

### Regras da senha

A senha deve possuir:

* Mínimo de 8 caracteres
* Pelo menos uma letra maiúscula
* Pelo menos uma letra minúscula
* Pelo menos um número
* Pelo menos um caractere especial

As senhas nunca devem ser armazenadas em texto puro. Utilize **bcrypt** para gerar o hash.

## Sistema de Login

O usuário poderá fazer login utilizando:

* E-mail ou nome de usuário
* Senha

Após a autenticação:

1. Validar os dados no banco de dados.
2. Gerar um token JWT.
3. Criar uma sessão segura.
4. Associar, quando necessário, a conta ao ID do Telegram.
5. Exibir uma mensagem de boas-vindas.

Exemplo:

> 👋 Olá, Felipe!
>
> Você entrou na sua conta com sucesso.
>
> Escolha uma opção abaixo:

Botões:

* 👤 Meu Perfil
* ⚙️ Configurações
* 📊 Dashboard
* 🔐 Segurança
* 🚪 Sair

## Comandos do Bot

Implementar os seguintes comandos:

`/start`
Inicia o bot e verifica se o usuário possui uma conta vinculada.

`/cadastro`
Inicia o processo de criação de conta.

`/login`
Permite autenticar a conta.

`/perfil`
Mostra as informações do usuário.

`/dashboard`
Abre ou envia acesso ao painel do usuário.

`/logout`
Encerra a sessão.

`/ajuda`
Mostra todos os comandos disponíveis.

## Fluxo do /start

Quando o usuário iniciar o bot:

Se não possuir conta:

> 🤖 Bem-vindo!
>
> Para utilizar o sistema, você precisa criar uma conta ou entrar em uma conta existente.

Botões:

* 📝 Criar conta
* 🔐 Fazer login

Se já estiver autenticado:

> 👋 Bem-vindo de volta, {nome}!
>
> Sua conta está conectada com sucesso.

Botões:

* 👤 Perfil
* 📊 Dashboard
* ⚙️ Configurações
* 🚪 Sair

## Banco de Dados

Criar uma tabela `usuarios` com:

* id
* nome
* username
* email
* senha_hash
* telegram_id
* foto_perfil
* criado_em
* atualizado_em
* ultimo_login
* status

O campo `telegram_id` deve ser único para evitar que uma mesma conta do Telegram seja vinculada incorretamente.

## Segurança

Implementar:

* Hash de senha com bcrypt.
* JWT com tempo de expiração.
* Validação de todos os campos.
* Proteção contra SQL Injection.
* Rate limit nas rotas de login.
* Expiração de sessão.
* Verificação de e-mail opcional.
* Sistema seguro de recuperação de senha.
* Nunca enviar senhas pelo Telegram ou armazená-las em texto puro.

## Painel Web

Criar também um painel administrativo e um painel do usuário.

### Dashboard do usuário

Exibir:

* Foto de perfil
* Nome
* Username
* E-mail
* ID da conta
* Data de criação
* Último login
* Status da conta

Menu lateral:

* 🏠 Início
* 👤 Meu Perfil
* 🔐 Segurança
* ⚙️ Configurações
* 🔗 Telegram
* 🚪 Sair

## Painel Administrativo

Criar uma área protegida para administradores.

Funções:

* Visualizar usuários cadastrados.
* Pesquisar usuários.
* Bloquear ou desbloquear contas.
* Visualizar quantidade de usuários.
* Visualizar usuários online.
* Visualizar últimos logins.
* Gerenciar administradores.
* Visualizar logs do sistema.

## Estrutura do Projeto

```text
telegram-bot/
│
├── src/
│   ├── bot/
│   │   ├── commands/
│   │   ├── handlers/
│   │   └── keyboards/
│   │
│   ├── controllers/
│   ├── routes/
│   ├── middleware/
│   ├── services/
│   ├── database/
│   └── config/
│
├── public/
│   ├── css/
│   ├── js/
│   └── images/
│
├── views/
│   ├── login
│   ├── cadastro
│   ├── dashboard
│   ├── perfil
│   └── admin
│
├── .env
├── package.json
└── server.js
```

## Interface

O design deve ser moderno, tecnológico e profissional.

Características:

* Tema escuro.
* Detalhes em azul elétrico.
* Efeito glassmorphism.
* Cards modernos.
* Animações suaves.
* Layout responsivo para computador e celular.
* Ícones intuitivos.
* Feedback visual para login, erro e sucesso.
* Loading durante requisições.

## Arquivo .env

Utilizar variáveis de ambiente:

```env
PORT=3000

TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI

DATABASE_URL=SUA_DATABASE_URL

JWT_SECRET=UMA_CHAVE_FORTE_E_SECRETA

NODE_ENV=development
```

## Resultado esperado

Entregar um projeto funcional e organizado, incluindo:

1. Backend completo em Node.js.
2. Integração com Telegram Bot API.
3. Cadastro de usuários.
4. Login seguro.
5. JWT.
6. PostgreSQL.
7. Vinculação da conta com o Telegram.
8. Painel web responsivo.
9. Dashboard do usuário.
10. Painel administrativo.
11. Sistema de logout.
12. Middleware de autenticação.
13. Tratamento de erros.
14. Código organizado e comentado.
15. Arquivo README explicando como instalar e executar o projeto.

O sistema deve estar pronto para rodar localmente e ser facilmente preparado para deploy.
