import os
import re
import time
import asyncio
import sqlite3
from datetime import datetime

import aiohttp
import bcrypt

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# =========================================================
# ⚙️ CONFIGURAÇÕES
# =========================================================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY")

DB_NAME = "ultrabotx.db"

if not TOKEN:
    raise RuntimeError(
        "❌ TELEGRAM_BOT_TOKEN não encontrado no .env"
    )


# =========================================================
# 🔢 ESTADOS DAS CONVERSAS
# =========================================================

(
    CAD_EMAIL,
    CAD_SENHA,
    CAD_NASCIMENTO,

    LOGIN_EMAIL,
    LOGIN_SENHA,

    BUSCAR_CNPJ,
    BUSCAR_PROCESSO

) = range(7)


# =========================================================
# 🏛️ TRIBUNAIS
# =========================================================

TRIBUNAIS = {

    # ==========================================
    # ⚖️ JUSTIÇA ESTADUAL
    # ==========================================

    "TJAC": "api_publica_tjac",
    "TJAL": "api_publica_tjal",
    "TJAP": "api_publica_tjap",
    "TJAM": "api_publica_tjam",
    "TJBA": "api_publica_tjba",
    "TJCE": "api_publica_tjce",
    "TJDFT": "api_publica_tjdft",
    "TJES": "api_publica_tjes",
    "TJGO": "api_publica_tjgo",
    "TJMA": "api_publica_tjma",
    "TJMT": "api_publica_tjmt",
    "TJMS": "api_publica_tjms",
    "TJMG": "api_publica_tjmg",
    "TJPA": "api_publica_tjpa",
    "TJPB": "api_publica_tjpb",
    "TJPR": "api_publica_tjpr",
    "TJPE": "api_publica_tjpe",
    "TJPI": "api_publica_tjpi",
    "TJRJ": "api_publica_tjrj",
    "TJRN": "api_publica_tjrn",
    "TJRS": "api_publica_tjrs",
    "TJRO": "api_publica_tjro",
    "TJRR": "api_publica_tjrr",
    "TJSC": "api_publica_tjsc",
    "TJSE": "api_publica_tjse",
    "TJSP": "api_publica_tjsp",
    "TJTO": "api_publica_tjto",


    # ==========================================
    # 🏛️ JUSTIÇA FEDERAL
    # ==========================================

    "TRF1": "api_publica_trf1",
    "TRF2": "api_publica_trf2",
    "TRF3": "api_publica_trf3",
    "TRF4": "api_publica_trf4",
    "TRF5": "api_publica_trf5",
    "TRF6": "api_publica_trf6",


    # ==========================================
    # 👷 JUSTIÇA DO TRABALHO
    # ==========================================

    "TRT1": "api_publica_trt1",
    "TRT2": "api_publica_trt2",
    "TRT3": "api_publica_trt3",
    "TRT4": "api_publica_trt4",
    "TRT5": "api_publica_trt5",
    "TRT6": "api_publica_trt6",
    "TRT7": "api_publica_trt7",
    "TRT8": "api_publica_trt8",
    "TRT9": "api_publica_trt9",
    "TRT10": "api_publica_trt10",
    "TRT11": "api_publica_trt11",
    "TRT12": "api_publica_trt12",
    "TRT13": "api_publica_trt13",
    "TRT14": "api_publica_trt14",
    "TRT15": "api_publica_trt15",
    "TRT16": "api_publica_trt16",
    "TRT17": "api_publica_trt17",
    "TRT18": "api_publica_trt18",
    "TRT19": "api_publica_trt19",
    "TRT20": "api_publica_trt20",
    "TRT21": "api_publica_trt21",
    "TRT22": "api_publica_trt22",
    "TRT23": "api_publica_trt23",
    "TRT24": "api_publica_trt24",


    # ==========================================
    # ⭐ TRIBUNAIS SUPERIORES
    # ==========================================

    "STF": "api_publica_stf",
    "STJ": "api_publica_stj",
    "TST": "api_publica_tst",
    "STM": "api_publica_stm",


    # ==========================================
    # 🗳️ JUSTIÇA ELEITORAL
    # ==========================================

    "TSE": "api_publica_tse",

    "TRE-AC": "api_publica_tre-ac",
    "TRE-AL": "api_publica_tre-al",
    "TRE-AP": "api_publica_tre-ap",
    "TRE-AM": "api_publica_tre-am",
    "TRE-BA": "api_publica_tre-ba",
    "TRE-CE": "api_publica_tre-ce",
    "TRE-DF": "api_publica_tre-df",
    "TRE-ES": "api_publica_tre-es",
    "TRE-GO": "api_publica_tre-go",
    "TRE-MA": "api_publica_tre-ma",
    "TRE-MT": "api_publica_tre-mt",
    "TRE-MS": "api_publica_tre-ms",
    "TRE-MG": "api_publica_tre-mg",
    "TRE-PA": "api_publica_tre-pa",
    "TRE-PB": "api_publica_tre-pb",
    "TRE-PR": "api_publica_tre-pr",
    "TRE-PE": "api_publica_tre-pe",
    "TRE-PI": "api_publica_tre-pi",
    "TRE-RJ": "api_publica_tre-rj",
    "TRE-RN": "api_publica_tre-rn",
    "TRE-RS": "api_publica_tre-rs",
    "TRE-RO": "api_publica_tre-ro",
    "TRE-RR": "api_publica_tre-rr",
    "TRE-SC": "api_publica_tre-sc",
    "TRE-SE": "api_publica_tre-se",
    "TRE-SP": "api_publica_tre-sp",
    "TRE-TO": "api_publica_tre-to",
}


# =========================================================
# 🗄️ BANCO DE DADOS
# =========================================================

def conectar_banco():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    return conn


def criar_tabelas():

    conn = conectar_banco()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            telegram_id INTEGER PRIMARY KEY,

            email TEXT UNIQUE NOT NULL,

            senha_hash TEXT NOT NULL,

            nascimento TEXT NOT NULL,

            idade INTEGER NOT NULL,

            criado_em TEXT NOT NULL

        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# 🛡️ RATE LIMIT
# =========================================================

consultas_usuario = {}

LIMITE_CONSULTAS = 10
JANELA_SEGUNDOS = 60


def pode_consultar(user_id):

    agora = time.time()

    if user_id not in consultas_usuario:

        consultas_usuario[user_id] = []


    consultas_usuario[user_id] = [

        consulta

        for consulta in consultas_usuario[user_id]

        if agora - consulta < JANELA_SEGUNDOS

    ]


    if len(
        consultas_usuario[user_id]
    ) >= LIMITE_CONSULTAS:

        return False


    consultas_usuario[user_id].append(
        agora
    )

    return True


# =========================================================
# 🔐 VERIFICAR LOGIN
# =========================================================

def usuario_logado(context):

    return context.user_data.get(
        "logado",
        False
    )


# =========================================================
# 🔐 VALIDAR SENHA
# =========================================================

def senha_valida(senha):

    if len(senha) < 8:

        return False, (
            "❌ A senha precisa ter pelo menos 8 caracteres."
        )


    if not any(
        letra.isupper()
        for letra in senha
    ):

        return False, (
            "❌ A senha precisa ter uma letra MAIÚSCULA."
        )


    if not any(
        letra.islower()
        for letra in senha
    ):

        return False, (
            "❌ A senha precisa ter uma letra minúscula."
        )


    if not any(
        numero.isdigit()
        for numero in senha
    ):

        return False, (
            "❌ A senha precisa ter pelo menos um número."
        )


    if not re.search(
        r"[!@#$%&*]",
        senha
    ):

        return False, (
            "❌ A senha precisa ter um caractere especial."
        )


    return True, "Senha válida."


# =========================================================
# ⬅️ TECLADOS
# =========================================================

def teclado_voltar_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⬅️ Voltar ao Menu",
                callback_data="menu"
            )
        ]

    ])


def teclado_inicio():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🔐 Fazer Login",
                callback_data="login"
            )
        ],

        [
            InlineKeyboardButton(
                "📝 Criar Conta",
                callback_data="cadastro"
            )
        ]

    ])


# =========================================================
# 🏠 TELA INICIAL
# =========================================================

async def tela_inicial(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    texto = """
╔══════════════════════════════╗
        🤖 ULTRABOTX
╚══════════════════════════════╝

🚀 Bem-vindo!

🔒 Para acessar as ferramentas,
faça login ou crie sua conta.

━━━━━━━━━━━━━━━━━━━━

👇 Escolha uma opção:
"""


    if update.message:

        await update.message.reply_text(
            texto,
            reply_markup=teclado_inicio()
        )


    elif update.callback_query:

        await update.callback_query.edit_message_text(
            texto,
            reply_markup=teclado_inicio()
        )


# =========================================================
# 📋 MENU PRINCIPAL
# =========================================================

async def mostrar_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return


    email = context.user_data.get(
        "email",
        "Usuário"
    )


    teclado = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🏢 Consultar CNPJ",
                callback_data="consultar_cnpj"
            )
        ],

        [
            InlineKeyboardButton(
                "⚖️ Consultar Processo",
                callback_data="consultar_processo"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 Minha Conta",
                callback_data="minha_conta"
            )
        ],

        [
            InlineKeyboardButton(
                "🚪 Sair da Conta",
                callback_data="logout"
            )
        ]

    ])


    texto = f"""
╔══════════════════════════════╗
        🤖 ULTRABOTX
╚══════════════════════════════╝

🟢 USUÁRIO AUTENTICADO

📧 {email}

━━━━━━━━━━━━━━━━━━━━

🏢 CONSULTAR CNPJ
Consulte informações de empresas.

⚖️ CONSULTAR PROCESSO
Busca processual.

👤 MINHA CONTA
Visualize seus dados.

━━━━━━━━━━━━━━━━━━━━

🔒 Sistema protegido
"""


    if update.message:

        await update.message.reply_text(
            texto,
            reply_markup=teclado
        )


    elif update.callback_query:

        await update.callback_query.answer()

        await update.callback_query.edit_message_text(
            texto,
            reply_markup=teclado
        )


# =========================================================
# 💬 QUALQUER MENSAGEM
# =========================================================

async def iniciar_por_mensagem(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return


    await mostrar_menu(
        update,
        context
    )


# =========================================================
# 📝 CADASTRO - INICIAR
# =========================================================

async def iniciar_cadastro(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        """
📝 CRIAR CONTA

━━━━━━━━━━━━━━━━━━━━

📧 Digite seu e-mail:

💡 Exemplo:

nome@gmail.com
""",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "❌ Cancelar",
                    callback_data="voltar_inicio"
                )
            ]

        ])
    )

    return CAD_EMAIL


# =========================================================
# 📧 CADASTRO EMAIL
# =========================================================

async def receber_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    email = update.message.text.strip().lower()


    padrao = (
        r"^[a-zA-Z0-9._%+-]+"
        r"@[a-zA-Z0-9.-]+"
        r"\.[a-zA-Z]{2,}$"
    )


    if not re.match(
        padrao,
        email
    ):

        await update.message.reply_text(
            """
❌ E-mail inválido!

Digite novamente.
""",
            reply_markup=teclado_voltar_menu()
        )

        return CAD_EMAIL


    conn = conectar_banco()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    existe = cursor.fetchone()

    conn.close()


    if existe:

        await update.message.reply_text(
            """
⚠️ Este e-mail já está cadastrado.

Use a opção:

🔐 Fazer Login
"""
        )

        return ConversationHandler.END


    context.user_data[
        "email_cadastro"
    ] = email


    await update.message.reply_text(
        """
✅ E-mail válido!

━━━━━━━━━━━━━━━━━━━━

🔐 Agora crie uma senha.

A senha precisa ter:

• 🔢 8 caracteres
• 🔠 Letra MAIÚSCULA
• 🔡 Letra minúscula
• 1️⃣ Um número
• 🔐 Caractere especial

Exemplo:

UltraBot@123
"""
    )

    return CAD_SENHA


# =========================================================
# 🔐 CADASTRO SENHA
# =========================================================

async def receber_senha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    senha = update.message.text


    valida, mensagem = senha_valida(
        senha
    )


    if not valida:

        await update.message.reply_text(
            mensagem
        )

        return CAD_SENHA


    senha_hash = bcrypt.hashpw(

        senha.encode("utf-8"),

        bcrypt.gensalt()

    ).decode("utf-8")


    context.user_data[
        "senha_hash"
    ] = senha_hash


    await update.message.reply_text(
        """
✅ Senha criada com segurança!

━━━━━━━━━━━━━━━━━━━━

🎂 Digite sua data de nascimento.

Formato:

DD/MM/AAAA

Exemplo:

18/08/2007
"""
    )

    return CAD_NASCIMENTO


# =========================================================
# 🎂 FINALIZAR CADASTRO
# =========================================================

async def receber_nascimento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    nascimento = update.message.text.strip()


    try:

        data_nascimento = datetime.strptime(

            nascimento,

            "%d/%m/%Y"

        )


        hoje = datetime.today()


        idade = (

            hoje.year
            -
            data_nascimento.year

        )


        if (

            hoje.month,
            hoje.day

        ) < (

            data_nascimento.month,
            data_nascimento.day

        ):

            idade -= 1


        if idade < 16:

            await update.message.reply_text(
                """
🔞 ACESSO NÃO PERMITIDO

É necessário ter pelo menos
16 anos para criar uma conta.
"""
            )

            return CAD_NASCIMENTO


        telegram_id = update.effective_user.id

        email = context.user_data.get(
            "email_cadastro"
        )

        senha_hash = context.user_data.get(
            "senha_hash"
        )


        conn = conectar_banco()

        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO usuarios (

                telegram_id,
                email,
                senha_hash,
                nascimento,
                idade,
                criado_em

            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (

                telegram_id,
                email,
                senha_hash,
                nascimento,
                idade,

                datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

            )
        )


        conn.commit()

        conn.close()


        # 🔓 LOGIN AUTOMÁTICO

        context.user_data.clear()

        context.user_data[
            "logado"
        ] = True

        context.user_data[
            "email"
        ] = email


        await update.message.reply_text(
            f"""
🎉 CONTA CRIADA COM SUCESSO!

━━━━━━━━━━━━━━━━━━━━

📧 {email}

🎂 {idade} anos

🔓 Você já está conectado!
"""
        )


        await mostrar_menu(
            update,
            context
        )


        return ConversationHandler.END


    except ValueError:

        await update.message.reply_text(
            """
❌ DATA INVÁLIDA

Use o formato:

DD/MM/AAAA

Exemplo:

18/08/2007
"""
        )

        return CAD_NASCIMENTO


# =========================================================
# 🔐 LOGIN
# =========================================================

async def iniciar_login(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        """
🔐 FAZER LOGIN

━━━━━━━━━━━━━━━━━━━━

📧 Digite seu e-mail:
"""
    )

    return LOGIN_EMAIL


# =========================================================
# 📧 LOGIN EMAIL
# =========================================================

async def receber_login_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    email = update.message.text.strip().lower()


    conn = conectar_banco()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT email
        FROM usuarios
        WHERE email = ?
        """,

        (email,)
    )


    usuario = cursor.fetchone()

    conn.close()


    if not usuario:

        await update.message.reply_text(
            """
❌ CONTA NÃO ENCONTRADA

Verifique o e-mail ou
crie uma nova conta.
"""
        )

        return ConversationHandler.END


    context.user_data[
        "login_email"
    ] = email


    await update.message.reply_text(
        """
🔐 Digite sua senha:
"""
    )

    return LOGIN_SENHA


# =========================================================
# 🔑 LOGIN SENHA
# =========================================================

async def receber_login_senha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    senha = update.message.text

    email = context.user_data.get(
        "login_email"
    )


    if not email:

        return ConversationHandler.END


    conn = conectar_banco()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT senha_hash
        FROM usuarios
        WHERE email = ?
        """,

        (email,)
    )


    usuario = cursor.fetchone()

    conn.close()


    if not usuario:

        return ConversationHandler.END


    senha_hash = usuario[0]


    senha_correta = bcrypt.checkpw(

        senha.encode("utf-8"),

        senha_hash.encode("utf-8")

    )


    if not senha_correta:

        await update.message.reply_text(
            """
❌ SENHA INCORRETA

Tente novamente.
"""
        )

        return LOGIN_SENHA


    context.user_data.clear()

    context.user_data[
        "logado"
    ] = True

    context.user_data[
        "email"
    ] = email


    await update.message.reply_text(
        """
🎉 LOGIN REALIZADO!

🔓 Bem-vindo ao UltraBotX.
"""
    )


    await mostrar_menu(
        update,
        context
    )


    return ConversationHandler.END


# =========================================================
# 🏢 INICIAR CNPJ
# =========================================================

async def iniciar_cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return ConversationHandler.END


    teclado = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⬅️ Voltar",
                callback_data="menu"
            )
        ]

    ])


    await query.edit_message_text(
        """
🏢 CONSULTAR CNPJ

━━━━━━━━━━━━━━━━━━━━

Digite o CNPJ que deseja consultar.

Exemplo:

12.345.678/0001-90
""",

        reply_markup=teclado
    )


    return BUSCAR_CNPJ


# =========================================================
# 🔎 CONSULTAR CNPJ
# =========================================================

async def consultar_cnpj(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return ConversationHandler.END


    user_id = update.effective_user.id


    if not pode_consultar(user_id):

        await update.message.reply_text(
            """
⏳ LIMITE ATINGIDO

Você fez muitas consultas.

Aguarde alguns instantes.
""",

            reply_markup=teclado_voltar_menu()
        )

        return ConversationHandler.END


    cnpj = re.sub(
        r"\D",
        "",
        update.message.text
    )


    if len(cnpj) != 14:

        await update.message.reply_text(
            """
❌ CNPJ INVÁLIDO

Digite um CNPJ com 14 números.

Exemplo:

12.345.678/0001-90
""",

            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "⬅️ Voltar ao Menu",
                        callback_data="menu"
                    )
                ]

            ])
        )

        return BUSCAR_CNPJ


    mensagem = await update.message.reply_text(
        """
🔎 CONSULTANDO CNPJ...

⏳ Aguarde...
"""
    )


    url = (
        f"https://publica.cnpj.ws/cnpj/{cnpj}"
    )


    try:

        timeout = aiohttp.ClientTimeout(
            total=20
        )


        async with aiohttp.ClientSession(

            timeout=timeout

        ) as session:


            async with session.get(
                url
            ) as response:


                if response.status == 404:

                    await mensagem.edit_text(
                        """
❌ CNPJ NÃO ENCONTRADO

Verifique o número e
tente novamente.
""",

                        reply_markup=teclado_voltar_menu()
                    )

                    return ConversationHandler.END


                if response.status == 429:

                    await mensagem.edit_text(
                        """
⏳ LIMITE DA API ATINGIDO

Aguarde alguns instantes.
""",

                        reply_markup=teclado_voltar_menu()
                    )

                    return ConversationHandler.END


                if response.status != 200:

                    await mensagem.edit_text(
                        f"""
❌ ERRO NA CONSULTA

Código: {response.status}
""",

                        reply_markup=teclado_voltar_menu()
                    )

                    return ConversationHandler.END


                dados = await response.json()


    except Exception as erro:

        print(
            "ERRO CNPJ:",
            erro
        )


        await mensagem.edit_text(
            """
❌ ERRO DE CONEXÃO

Não foi possível consultar
o CNPJ neste momento.
""",

            reply_markup=teclado_voltar_menu()
        )

        return ConversationHandler.END


    estabelecimento = dados.get(
        "estabelecimento",
        {}
    )

    cidade = estabelecimento.get(
        "cidade",
        {}
    )

    estado = estabelecimento.get(
        "estado",
        {}
    )

    atividade = estabelecimento.get(
        "atividade_principal",
        {}
    )

    porte = dados.get(
        "porte",
        {}
    )


    resultado = f"""
🏢 EMPRESA ENCONTRADA

━━━━━━━━━━━━━━━━━━━━

🔢 CNPJ

{cnpj}

🏷️ RAZÃO SOCIAL

{dados.get("razao_social", "Não informado")}

🏪 NOME FANTASIA

{estabelecimento.get("nome_fantasia") or "Não informado"}

━━━━━━━━━━━━━━━━━━━━

📊 SITUAÇÃO

{estabelecimento.get("situacao_cadastral", "Não informado")}

📈 PORTE

{porte.get("descricao", "Não informado")}

💰 CAPITAL SOCIAL

R$ {dados.get("capital_social", "Não informado")}

━━━━━━━━━━━━━━━━━━━━

🎯 ATIVIDADE PRINCIPAL

{atividade.get("descricao", "Não informado")}

🔢 CNAE

{atividade.get("id", "Não informado")}

━━━━━━━━━━━━━━━━━━━━

📍 ENDEREÇO

{estabelecimento.get("logradouro", "Não informado")}

Nº {estabelecimento.get("numero", "S/N")}

🏘️ Bairro:
{estabelecimento.get("bairro", "Não informado")}

🏙️ Cidade:
{cidade.get("nome", "Não informado")}

🗺️ Estado:
{estado.get("sigla", "Não informado")}

📮 CEP:
{estabelecimento.get("cep", "Não informado")}

━━━━━━━━━━━━━━━━━━━━

📞 TELEFONE

{estabelecimento.get("telefone1") or "Não informado"}

📧 E-MAIL

{estabelecimento.get("email") or "Não informado"}
"""


    if len(resultado) > 4000:

        resultado = resultado[:3900]

        resultado += "\n\n⚠️ Resultado resumido."


    teclado = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🔎 Consultar outro CNPJ",
                callback_data="consultar_cnpj"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Menu Principal",
                callback_data="menu"
            )
        ]

    ])


    await mensagem.edit_text(

        resultado,

        reply_markup=teclado

    )


    return ConversationHandler.END


# =========================================================
# ⚖️ INICIAR PROCESSO
# =========================================================

async def iniciar_processo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return ConversationHandler.END


    await query.edit_message_text(
        """
⚖️ CONSULTA PROCESSUAL

━━━━━━━━━━━━━━━━━━━━

Digite o número do processo.

Exemplo:

0001234-56.2025.8.19.0001

🇧🇷 O sistema realizará uma busca
nos tribunais configurados.
""",

        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ Voltar",
                    callback_data="menu"
                )
            ]

        ])
    )


    return BUSCAR_PROCESSO


# =========================================================
# 🔍 BUSCAR EM UM TRIBUNAL
# =========================================================

async def buscar_em_tribunal(

    session,
    tribunal,
    alias,
    numero,
    headers,
    semaphore

):

    url = (
        "https://api-publica.datajud.cnj.jus.br/"
        f"{alias}/_search"
    )


    payload = {

        "query": {

            "term": {

                "numeroProcesso": numero

            }

        },

        "size": 1

    }


    try:

        async with semaphore:

            async with session.post(

                url,

                headers=headers,

                json=payload

            ) as response:


                if response.status != 200:

                    return None


                dados = await response.json()


                hits = (

                    dados

                    .get("hits", {})

                    .get("hits", [])

                )


                if hits:

                    print(
                        f"✅ Processo encontrado no {tribunal}"
                    )


                    return {

                        "tribunal": tribunal,

                        "processo": hits[0].get(
                            "_source",
                            {}
                        )

                    }


    except Exception as erro:

        print(
            f"⚠️ Erro no {tribunal}:",
            erro
        )


    return None


# =========================================================
# ⚖️ CONSULTAR PROCESSO
# =========================================================

async def consultar_processo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return ConversationHandler.END


    if not DATAJUD_API_KEY:

        await update.message.reply_text(
            """
❌ DATAJUD NÃO CONFIGURADO

Adicione sua chave no arquivo .env

DATAJUD_API_KEY=SUA_CHAVE
""",

            reply_markup=teclado_voltar_menu()
        )

        return ConversationHandler.END


    user_id = update.effective_user.id


    if not pode_consultar(user_id):

        await update.message.reply_text(
            """
⏳ LIMITE DE CONSULTAS ATINGIDO

Aguarde alguns instantes.
""",

            reply_markup=teclado_voltar_menu()
        )

        return ConversationHandler.END


    numero = re.sub(
        r"\D",
        "",
        update.message.text
    )


    if len(numero) != 20:

        await update.message.reply_text(
            """
❌ PROCESSO INVÁLIDO

Digite um número com 20 dígitos.

Exemplo:

0001234-56.2025.8.19.0001
""",

            reply_markup=teclado_voltar_menu()
        )

        return BUSCAR_PROCESSO


    mensagem = await update.message.reply_text(
        f"""
🇧🇷 BUSCA NACIONAL

━━━━━━━━━━━━━━━━━━━━

⚖️ Processo:

{numero}

🏛️ Consultando tribunais...

⏳ Aguarde...
"""
    )


    headers = {

        "Authorization":
            f"APIKey {DATAJUD_API_KEY}",

        "Content-Type":
            "application/json"

    }


    timeout = aiohttp.ClientTimeout(
        total=40
    )


    # Limita quantidade de conexões simultâneas
    # para evitar sobrecarga/rate limiting.
    semaphore = asyncio.Semaphore(8)


    try:

        connector = aiohttp.TCPConnector(
            limit=10
        )


        async with aiohttp.ClientSession(

            timeout=timeout,

            connector=connector

        ) as session:


            tarefas = []


            for tribunal, alias in TRIBUNAIS.items():

                tarefa = buscar_em_tribunal(

                    session,

                    tribunal,

                    alias,

                    numero,

                    headers,

                    semaphore

                )


                tarefas.append(
                    tarefa
                )


            resultados = await asyncio.gather(

                *tarefas,

                return_exceptions=True

            )


    except Exception as erro:

        print(
            "❌ ERRO GERAL:",
            erro
        )


        await mensagem.edit_text(
            """
❌ ERRO NA BUSCA

Não foi possível concluir
a consulta nacional.
""",

            reply_markup=teclado_voltar_menu()
        )

        return ConversationHandler.END


    processo_encontrado = None


    for resultado in resultados:

        if isinstance(
            resultado,
            dict
        ):

            processo_encontrado = resultado

            break


    # =====================================================
    # ❌ NÃO ENCONTRADO
    # =====================================================

    if not processo_encontrado:

        teclado = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🔎 Tentar outro processo",
                    callback_data="consultar_processo"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Menu Principal",
                    callback_data="menu"
                )
            ]

        ])


        await mensagem.edit_text(
            f"""
❌ PROCESSO NÃO ENCONTRADO

━━━━━━━━━━━━━━━━━━━━

⚖️ Número:

{numero}

━━━━━━━━━━━━━━━━━━━━

🇧🇷 A busca foi realizada nos
tribunais configurados.

⚠️ O processo pode:

🔒 Estar sob sigilo

📡 Não estar disponível no DataJud

❌ Possuir número incorreto

🏛️ Não ter dados públicos disponíveis
""",

            reply_markup=teclado
        )


        return ConversationHandler.END


    # =====================================================
    # ✅ PROCESSO ENCONTRADO
    # =====================================================

    tribunal = processo_encontrado[
        "tribunal"
    ]


    processo = processo_encontrado[
        "processo"
    ]


    await exibir_processo(

        mensagem,

        processo,

        tribunal

    )


    return ConversationHandler.END


# =========================================================
# 📄 EXIBIR PROCESSO
# =========================================================

async def exibir_processo(

    mensagem,

    processo,

    tribunal

):

    classe = processo.get(
        "classe",
        {}
    )

    orgao = processo.get(
        "orgaoJulgador",
        {}
    )

    assuntos = processo.get(
        "assuntos",
        []
    )

    movimentos = processo.get(
        "movimentos",
        []
    )


    assuntos_texto = "Não informado"


    if assuntos:

        lista = []


        for assunto in assuntos[:5]:

            nome = assunto.get(
                "nome",
                "Não informado"
            )

            lista.append(
                f"• {nome}"
            )


        assuntos_texto = "\n".join(
            lista
        )


    resultado = f"""
⚖️ PROCESSO ENCONTRADO

━━━━━━━━━━━━━━━━━━━━

🔢 PROCESSO

{processo.get("numeroProcesso", "Não informado")}

🏛️ TRIBUNAL

{tribunal}

━━━━━━━━━━━━━━━━━━━━

📂 CLASSE

{classe.get("nome", "Não informado")}

🏢 ÓRGÃO JULGADOR

{orgao.get("nome", "Não informado")}

📅 DATA DE AJUIZAMENTO

{processo.get("dataAjuizamento", "Não informado")}

━━━━━━━━━━━━━━━━━━━━

📌 ASSUNTOS

{assuntos_texto}

━━━━━━━━━━━━━━━━━━━━

🔄 ÚLTIMAS MOVIMENTAÇÕES
"""


    if movimentos:

        for movimento in movimentos[-5:]:

            data = movimento.get(
                "dataHora",
                "Não informado"
            )

            codigo = movimento.get(
                "codigo",
                "Não informado"
            )


            resultado += f"""

📌 Código: {codigo}

📅 {data}
"""


    else:

        resultado += """

Nenhuma movimentação disponível.
"""


    if len(resultado) > 4000:

        resultado = resultado[:3900]

        resultado += "\n\n⚠️ Resultado resumido."


    teclado = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🔎 Consultar outro processo",
                callback_data="consultar_processo"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Menu Principal",
                callback_data="menu"
            )
        ]

    ])


    await mensagem.edit_text(

        resultado,

        reply_markup=teclado

    )


# =========================================================
# 👤 MINHA CONTA
# =========================================================

async def minha_conta(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if not usuario_logado(context):

        await tela_inicial(
            update,
            context
        )

        return


    telegram_id = query.from_user.id


    conn = conectar_banco()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            email,
            idade,
            criado_em

        FROM usuarios

        WHERE telegram_id = ?
        """,

        (telegram_id,)
    )


    usuario = cursor.fetchone()

    conn.close()


    if not usuario:

        await query.edit_message_text(
            "❌ Conta não encontrada."
        )

        return


    email, idade, criado_em = usuario


    await query.edit_message_text(
        f"""
👤 MINHA CONTA

━━━━━━━━━━━━━━━━━━━━

📧 E-MAIL

{email}

🎂 IDADE

{idade} anos

📅 CONTA CRIADA EM

{criado_em}

━━━━━━━━━━━━━━━━━━━━

🔒 Sua senha está armazenada
com proteção por hash.
""",

        reply_markup=teclado_voltar_menu()
    )


# =========================================================
# 🚪 LOGOUT
# =========================================================

async def logout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    context.user_data.clear()


    await query.edit_message_text(
        """
🚪 LOGOUT REALIZADO

━━━━━━━━━━━━━━━━━━━━

🔒 Sua sessão foi encerrada.

💬 Envie qualquer mensagem
para iniciar novamente.
"""
    )


# =========================================================
# 🏠 VOLTAR AO INÍCIO
# =========================================================

async def voltar_inicio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    context.user_data.clear()


    await tela_inicial(
        update,
        context
    )


    return ConversationHandler.END


# =========================================================
# ❌ CANCELAR
# =========================================================

async def cancelar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.pop(
        "email_cadastro",
        None
    )

    context.user_data.pop(
        "senha_hash",
        None
    )

    context.user_data.pop(
        "login_email",
        None
    )


    await update.message.reply_text(
        """
❌ OPERAÇÃO CANCELADA

Voltando ao menu...
"""
    )


    await mostrar_menu(
        update,
        context
    )


    return ConversationHandler.END


# =========================================================
# 🚀 MAIN
# =========================================================

def main():

    criar_tabelas()


    app = (

        Application.builder()

        .token(TOKEN)

        .build()

    )


    # =====================================================
    # 📝 CADASTRO
    # =====================================================

    cadastro_handler = ConversationHandler(

        entry_points=[

            CallbackQueryHandler(
                iniciar_cadastro,
                pattern="^cadastro$"
            )

        ],


        states={

            CAD_EMAIL: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_email
                )

            ],


            CAD_SENHA: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_senha
                )

            ],


            CAD_NASCIMENTO: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_nascimento
                )

            ]

        },


        fallbacks=[

            CallbackQueryHandler(
                voltar_inicio,
                pattern="^voltar_inicio$"
            ),

            CommandHandler(
                "cancelar",
                cancelar
            )

        ]

    )


    # =====================================================
    # 🔐 LOGIN
    # =====================================================

    login_handler = ConversationHandler(

        entry_points=[

            CallbackQueryHandler(
                iniciar_login,
                pattern="^login$"
            )

        ],


        states={

            LOGIN_EMAIL: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_login_email
                )

            ],


            LOGIN_SENHA: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_login_senha
                )

            ]

        },


        fallbacks=[

            CallbackQueryHandler(
                voltar_inicio,
                pattern="^voltar_inicio$"
            ),

            CommandHandler(
                "cancelar",
                cancelar
            )

        ]

    )


    # =====================================================
    # 🏢 CNPJ
    # =====================================================

    cnpj_handler = ConversationHandler(

        entry_points=[

            CallbackQueryHandler(
                iniciar_cnpj,
                pattern="^consultar_cnpj$"
            )

        ],


        states={

            BUSCAR_CNPJ: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    consultar_cnpj
                )

            ]

        },


        fallbacks=[

            CallbackQueryHandler(
                mostrar_menu,
                pattern="^menu$"
            ),

            CommandHandler(
                "cancelar",
                cancelar
            )

        ]

    )


    # =====================================================
    # ⚖️ PROCESSOS
    # =====================================================

    processo_handler = ConversationHandler(

        entry_points=[

            CallbackQueryHandler(
                iniciar_processo,
                pattern="^consultar_processo$"
            )

        ],


        states={

            BUSCAR_PROCESSO: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    consultar_processo
                )

            ]

        },


        fallbacks=[

            CallbackQueryHandler(
                mostrar_menu,
                pattern="^menu$"
            ),

            CommandHandler(
                "cancelar",
                cancelar
            )

        ]

    )


    # =====================================================
    # ➕ ADICIONAR HANDLERS
    # =====================================================

    app.add_handler(
        cadastro_handler
    )

    app.add_handler(
        login_handler
    )

    app.add_handler(
        cnpj_handler
    )

    app.add_handler(
        processo_handler
    )


    # =====================================================
    # 📋 MENU
    # =====================================================

    app.add_handler(

        CallbackQueryHandler(
            mostrar_menu,
            pattern="^menu$"
        )

    )


    # =====================================================
    # 👤 MINHA CONTA
    # =====================================================

    app.add_handler(

        CallbackQueryHandler(
            minha_conta,
            pattern="^minha_conta$"
        )

    )


    # =====================================================
    # 🚪 LOGOUT
    # =====================================================

    app.add_handler(

        CallbackQueryHandler(
            logout,
            pattern="^logout$"
        )

    )


    # =====================================================
    # 🏠 VOLTAR INÍCIO
    # =====================================================

    app.add_handler(

        CallbackQueryHandler(
            voltar_inicio,
            pattern="^voltar_inicio$"
        )

    )


    # =====================================================
    # 💬 QUALQUER MENSAGEM INICIA
    # =====================================================

    app.add_handler(

        MessageHandler(

            filters.TEXT
            &
            ~filters.COMMAND,

            iniciar_por_mensagem

        )

    )


    # =====================================================
    # 🖥️ CONSOLE
    # =====================================================

    print()
    print("╔════════════════════════════════════╗")
    print("║       🤖 ULTRABOTX ONLINE          ║")
    print("╚════════════════════════════════════╝")
    print()
    print("🚀 Sistema iniciado com sucesso!")
    print("🔒 Segurança: ATIVA")
    print("🗄️ Banco SQLite: CONECTADO")
    print("🏢 Consulta CNPJ: ATIVA")
    print("⚖️ Busca Processual: ATIVA")
    print(f"🏛️ Tribunais configurados: {len(TRIBUNAIS)}")
    print()
    print("💬 Qualquer mensagem inicia o bot.")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()


    app.run_polling()


if __name__ == "__main__":

    main()