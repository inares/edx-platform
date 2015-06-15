"""
Signal handler for invalidating cached course overviews
"""
from celery.task import task
from django.dispatch.dispatcher import receiver

from xmodule.modulestore.django import SignalHandler

from .models import CourseOverview


@task()
def _delete_entry(course_key):
    """
    Given a course key, delete the corresponding CourseOverview from the database.
    """
    CourseOverview.objects.filter(id=course_key).delete()


@receiver(SignalHandler.course_published)
def _listen_for_course_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Catches the signal that a course has been published in Studio and invalidates
    the corresponding CourseOverview cache entry if one exists.
    """
    _delete_entry.delay(course_key)
