from config import constants
from utils.errors import ApiError


def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_produto(dados):
    if not dados:
        raise ApiError("Dados inválidos")
    for campo, mensagem in (
        ("nome", "Nome é obrigatório"),
        ("preco", "Preço é obrigatório"),
        ("estoque", "Estoque é obrigatório"),
    ):
        if campo not in dados:
            raise ApiError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", constants.CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ApiError("Nome inválido")
    if not isinstance(descricao, str):
        raise ApiError("Descrição inválida")
    if not _numero(preco):
        raise ApiError("Preço inválido")
    if not _numero(estoque):
        raise ApiError("Estoque inválido")

    if preco < 0:
        raise ApiError("Preço não pode ser negativo")
    if estoque < 0:
        raise ApiError("Estoque não pode ser negativo")
    if len(nome) < constants.NOME_PRODUTO_MIN:
        raise ApiError("Nome muito curto")
    if len(nome) > constants.NOME_PRODUTO_MAX:
        raise ApiError("Nome muito longo")
    if categoria not in constants.CATEGORIAS_VALIDAS:
        raise ApiError("Categoria inválida. Válidas: " + str(constants.CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_usuario(dados):
    if not dados:
        raise ApiError("Dados inválidos")
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ApiError("Nome, email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (nome, email, senha)):
        raise ApiError("Nome, email e senha devem ser texto")
    return nome, email, senha


def validar_login(dados):
    dados = dados or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise ApiError("Email e senha são obrigatórios")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ApiError("Email e senha devem ser texto")
    return email, senha


def validar_pedido(dados):
    if not dados:
        raise ApiError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ApiError("Usuario ID é obrigatório")
    if not itens:
        raise ApiError("Pedido deve ter pelo menos 1 item")
    if not _inteiro(usuario_id):
        raise ApiError("Usuario ID inválido")
    if not isinstance(itens, list):
        raise ApiError("Itens inválidos")
    for item in itens:
        if not isinstance(item, dict) or not _inteiro(item.get("produto_id")) or not _inteiro(item.get("quantidade")):
            raise ApiError("Cada item deve ter produto_id e quantidade inteiros")
        if item["quantidade"] <= 0:
            raise ApiError("Quantidade deve ser maior que zero")
    return usuario_id, itens


def validar_status_pedido(dados):
    status = (dados or {}).get("status", "")
    if status not in constants.STATUS_PEDIDO_VALIDOS:
        raise ApiError("Status inválido")
    return status


def parse_preco(valor, nome_campo):
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ApiError(nome_campo + " inválido")
