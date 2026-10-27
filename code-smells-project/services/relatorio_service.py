from config import constants
from models import sistema_model


def calcular_desconto(faturamento):
    for minimo, percentual in constants.FAIXAS_DESCONTO:
        if faturamento > minimo:
            return faturamento * percentual
    return 0


def relatorio_vendas():
    totais = sistema_model.totais_pedidos()
    faturamento = totais["faturamento"]
    desconto = calcular_desconto(faturamento)
    total_pedidos = totais["total_pedidos"]

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": totais["pendentes"],
        "pedidos_aprovados": totais["aprovados"],
        "pedidos_cancelados": totais["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
