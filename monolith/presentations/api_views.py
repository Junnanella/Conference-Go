from inspect import _void
from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods

from .models import Presentation
from events.api_views import ConferenceListEncoder

import pika, json

# Encoder


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "name",
    ]


# views


def api_list_presentations(request, conference_id):
    """
    Lists the presentation titles and the link to the
    presentation for the specified conference id.

    Returns a dictionary with a single key "presentations"
    which is a list of presentation titles and URLS. Each
    entry in the list is a dictionary that contains the
    title of the presentation, the name of its status, and
    the link to the presentation's information.

    {
        "presentations": [
            {
                "title": presentation's title,
                "status": presentation's status name
                "href": URL to the presentation,
            },
            ...
        ]
    }
    """
    presentations = [
        {
            "title": p.title,
            "status": p.status.name,
            "href": p.get_api_url(),
        }
        for p in Presentation.objects.filter(conference=conference_id)
    ]
    return JsonResponse(
        presentations,
        encoder=PresentationListEncoder,
        safe=False,
    )


def api_show_presentation(request, pk):
    """
    Returns the details for the Presentation model specified
    by the pk parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL

    {
        "presenter_name": the name of the presenter,
        "company_name": the name of the presenter's company,
        "presenter_email": the email address of the presenter,
        "title": the title of the presentation,
        "synopsis": the synopsis for the presentation,
        "created": the date/time when the record was created,
        "status": the name of the status for the presentation,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """

    presentation = Presentation.objects.get(id=pk)

    return JsonResponse(
        presentation, encoder=PresentationDetailEncoder, safe=False
    )


def queue_presentation(data, queue_name: str) -> None:
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange="",
        routing_key="tasks",
        body=json.dumps(data),
    )
    connection.close()


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()
    queue_presentation(
        {
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        },
        "presentation_approvals",
    )
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()
    queue_presentation(
        {
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        },
        "presentation_rejections",
    )
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
