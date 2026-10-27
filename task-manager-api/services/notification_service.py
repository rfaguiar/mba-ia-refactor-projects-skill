import logging
import smtplib

from config import settings
from utils.dates import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, host=None, port=None, user=None, password=None):
        self.notifications = []
        self.email_host = host or settings.SMTP_HOST
        self.email_port = port or settings.SMTP_PORT
        self.email_user = user or settings.SMTP_USER
        self.email_password = password or settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, to, f"Subject: {subject}\n\n{body}")
            server.quit()
            logger.info('Email enviado para %s', to)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception('Erro ao enviar email')
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você."
            f"\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
