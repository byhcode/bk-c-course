# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = (
    url(r"^update_user_info/$", views.update_user_info, name="update_user_info"),
    url(r"^manage_course/$", views.manage_course),
    url(r"^find_courses/$", views.search_courses_by_userid),
    url(r"^find_teacher_names/$", views.search_teacher_names),
)