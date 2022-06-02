import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body, request):
    print("Received %r" % body)

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.basic_consume(
        queue="presentation_approvals",
        on_message_callback=send_mail(
            f"To: {request.presenter_email}",
            "From: admin@conference.go",
            "Your presentation has been accepted",
            f"{request.presenter_name}, we're happy to tell you that your presentation {request.title} has been approved",
        ),
        auto_ack=True,
    )
    channel.start_consuming()


def process_rejection(ch, method, properties, body, request):
    print("Received %r" % body)

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    channel.basic_consume(
        queue="presentation_rejections",
        on_message_callback=send_mail(
            f"To: {request.presenter_email}",
            "From: admin@conference.go",
            "Your presentation has been rejected",
            f"{request.presenter_name}, we're sad to tell you that your presentation {request.title} has been rejected",
        ),
        auto_ack=True,
    )
    channel.start_consuming()
