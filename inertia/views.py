import json
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.shortcuts import render
from django.http import JsonResponse
from django.middleware import csrf
from .share import shared_props
from .version import asset_version

from rest_framework.generics import GenericAPIView

from django.views.generic import View
from django.conf import settings


def _build_context(component_name, props, version):
    context = {
        "page": {
            "version": version,
            "component": component_name,
            "props": props
        }
    }

    return context


def render_inertia(request, component_name, props=None, template_name=None):
    """
    Renders either an HttpRespone or JsonResponse of a component for 
    the use in an InertiaJS frontend integration.
    """
    inertia_template = None

    if settings.INERTIA_TEMPLATE is not None:
        inertia_template = settings.INERTIA_TEMPLATE

    if template_name is not None:
        inertia_template = template_name

    if inertia_template is None:
        raise ImproperlyConfigured(
            "No Inertia template found. Either set INERTIA_TEMPLATE"
            "in settings.py or pass template parameter."
        )

    if props is None:
        props = {}

    shared = {}
    for key, value in shared_props.items():
        if callable(value):
            shared[key] = value(request)
        else:
            shared[key] = value

    props['shared'] = shared

    # subsequent renders
    if ('x-inertia' in request.headers and
        'x-inertia-version' in request.headers and
        request.headers['x-inertia-version'] == str(asset_version.get_version())):
        response = JsonResponse({
            "component": component_name,
            "props": props,
            "version": asset_version.get_version(),
            "url": request.path
        })

        response['X-Inertia'] = True
        response['Vary'] = 'Accept'
        return response

    context = _build_context(component_name, props,
                             asset_version.get_version())

    return render(request, inertia_template, context)


class InertiaMixin():
    component_name = ""
    props = None
    template_name = None
    serializer_class = None

    def render_to_response(self, context, many=False):
        if self.serializer_class is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing a ModelSerializer. Define "
                "%(cls)s.serializer_class." % {
                    'cls': self.__class__.__name__
                }
            )

        if (many):
            object_name = self.get_context_object_name(self.object_list)
            serialized_object = self.serializer_class(
                self.object_list, many=True).data
        else:
            object_name = self.get_context_object_name(self.object)
            serialized_object = self.serializer_class(
                self.object).data

        if self.props is None:
            self.props = {object_name: serialized_object}
        else:
            self.props[object_name] = serialized_object

        return render_inertia(self.request, self.component_name, self.props, self.template_name)


class InertiaDetailView(InertiaMixin, BaseDetailView):
    """
    Similiar to Djangos DetailView, but with Inertia templates.
    """


class InertiaListView(InertiaMixin, BaseListView):
    """
    Similiar to Djangos ListView, but with Inertia templates.
    """

    def render_to_response(self, context):
        return super().render_to_response(context, True)
