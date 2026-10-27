import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("Email: pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: seu pedido foi recebido")
    logger.info("Push: novo pedido recebido pelo sistema")


def status_alterado(pedido_id, status):
    if status == "aprovado":
        logger.info("Pedido %s aprovado; preparar envio", pedido_id)
    elif status == "cancelado":
        logger.info("Pedido %s cancelado; devolver estoque", pedido_id)
