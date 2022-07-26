# -*- coding: utf-8 -*-

import json
import logging
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from MySQLdb import DatabaseError

from .celery_task.judge_objective import judge_objective
from .models import (
    CustomType,
    Member,
    Paper,
    PaperQuestionContact,
    Question,
    StudentAnswer,
    StudentPaperContact,
    UserCourseContact, Chapter, Course,
    Binary_tree_1,
)

from algorithm import huffman

logger = logging.getLogger("root")


def authority_manage(function, *args, **kwargs):
    def inner(request):
        method = request.method
        if method == 'GET':
            course_id = request.GET.get('course_id')
        else:
            course_id = json.loads(request.body).get('course_id')

        if not course_id:
            return JsonResponse(
                {'result': False, 'code': 403, 'message': '请求参数不完整', 'data': []}
            )

        user_info = "{}({})".format(request.user.class_number, request.user.name)
        try:
            if Member.objects.get(username=request.user.username).identity != Member.Identity.TEACHER:
                return JsonResponse(
                    {'result': False, 'code': 403, 'message': '您没有操作权限！', 'data': []}
                )
            course = Course.objects.get(id=course_id)
            if course.create_people == user_info or course.teacher == user_info:
                return function(request, *args, **kwargs)
            else:
                return JsonResponse(
                    {'result': False, 'code': 403, 'message': '您没有操作权限！', 'data': []}
                )
        except DatabaseError as e:
            logger.exception("函数[authority_manage]: {}".format(e))
            return JsonResponse({'result': False, 'code': 500, 'message': '操作失败(请检查日志)', 'data': {}})

    return inner


@authority_manage
def question_title(request):
    method = request.method

    if method == "POST":
        """
        功能：针对每一种的课程，建立大题标题
        输入：课程id， 大题题目
        返回：添加成功或失败
        """
        body = json.loads(request.body)
        course_id = body.get("course_id")
        custom_type_info = body.get("custom_type_info")
        if custom_type_info is None or course_id is None:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        create_types = []
        update_types = []
        delete_types = []

        for info in custom_type_info:
            if info.get("custom_type_id") is None:
                create_types.append(
                    CustomType(
                        course_id=course_id,
                        custom_type_name=info.get("custom_type_name"),
                    )
                )
            elif info.get("custom_type_name") is None:
                delete_types.append(info.get("custom_type_id"))
            else:
                update_types.append(
                    CustomType(
                        custom_type_name=info.get("custom_type_name"),
                        id=info.get("custom_type_id"),
                    )
                )
        try:
            with transaction.atomic():
                CustomType.objects.bulk_create(create_types)
                CustomType.objects.bulk_update(update_types, ["custom_type_name"])
                CustomType.objects.filter(id__in=delete_types).delete()
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "保存失败", "code": 500, "data": {}}
            )
        return JsonResponse(
            {"result": True, "message": "保存成功", "code": 200, "data": {}}
        )

    if method == "GET":
        """
        功能: 根据课程id，返回对应的大题的信息
        输入: course_id
        返回: 该课程的题目信息
        """
        course_id = request.GET.get("course_id")
        if course_id is None:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        try:
            custom_types = list(CustomType.objects.filter(course_id=course_id).values())
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": True, "code": 500, "message": "查询失败(请检查日志)", "date": {}}
            )

        return JsonResponse(
            {
                "result": True,
                "code": 200,
                "message": "查询成功",
                "data": {"custom_types": custom_types},
            }
        )

    else:
        return JsonResponse({"result": False, "code": 405, "message": "请求方法错误"})


def paper(request):
    method = request.method

    if method == "GET":
        """
        功能:
             老师
             1. 根据老师id，返回给老师的所有卷子
             2. 根据老师id与课程id，返回对应老师教的本门课程的所有卷子
             3. 根据question_id查询所含该题目的卷子（同步题目使用）
             学生
             1. 根据课程去查
        输入：老师id或老师与课程id
        返回：对应卷子信息
        """
        question_id = request.GET.get("question_id")
        query_param = {}
        identity = request.user.identity
        # 根据请求的identity，构造查询Paper表的参数
        if not question_id:
            if identity == Member.Identity.TEACHER:
                query_param = {"teacher": str(Member.objects.get(id=request.user.id))}
            if request.GET.get("course_id"):
                query_param["course_id"] = request.GET.get("course_id")
            else:
                return JsonResponse({
                    'result': False, 'code': 400, 'message': '请求参数不完整', 'data': {}
                })
            if identity == Member.Identity.STUDENT:
                query_param = {"status__in": ["RELEASE", "MARKED"]}
        else:
            query_param["id__in"] = [
                pq.paper_id
                for pq in PaperQuestionContact.objects.filter(question_id=question_id)
            ]

        try:
            # 得到查询参数的卷子信息
            papers = Paper.objects.filter(**query_param).values()
            # 给卷子按时间排序
            try:
                papers = sorted(papers, key=lambda p: p['start_time'], reverse=True)
            except TypeError as e:
                logger.exception("函数: [paper]: 有paper没有设置时间{}".format(e))
                return JsonResponse({"result": False, "code": 500, "message": "查询失败(请检查日志)", "data": {}})
            # 得到卷子的所属章节
            chapter_ids = [p['chapter_id'] for p in papers]
            chapters = {chapter.id: chapter.chapter_name for chapter in Chapter.objects.filter(id__in=chapter_ids)}
            # 构造数据
            paper_info = {}
            for paper in papers:
                paper_info[paper['id']] = paper
                paper_info[paper['id']]['chapter_name'] = chapters[paper['chapter_id']] \
                    if paper['chapter_id'] != -1 else '全部章节'

            # 老师和学生都会查询卷子的作答情况(老师也可以去答卷)
            SPContacts = {spc.paper_id: spc for spc in
                          StudentPaperContact.objects.filter(student_id=request.user.id)}
            for paper_id, paper in paper_info.items():
                paper_info[paper_id]['student_status'] = SPContacts[paper_id]. \
                    status if paper_id in SPContacts.keys() else StudentPaperContact.Status.NOT_ANSWER

                if paper['status'] == Paper.Status.MARKED:
                    paper_info[paper_id]['score'] = SPContacts[paper_id]. \
                        score if paper_id in SPContacts.keys() else 0

            # 如果是老师请求
            if identity == Member.Identity.TEACHER:
                for paper_id, paper in paper_info.items():
                    if (paper['status'] == Paper.Status.MARKED) or (paper['status'] == Paper.Status.RELEASE):
                        # 获取那些学生没有答，那些学生答过(数量)(包括老师)
                        total_students_num = UserCourseContact.objects.filter(course_id=paper['course_id']).count()
                        query_param = {'paper_id': paper_id, 'course_id': paper['course_id']}
                        # 如果答题时间未过, 只统计提交卷子的学生数量
                        if paper['end_time'] < timezone.now():
                            query_param['status__in'] = [
                                StudentPaperContact.Status.SUBMITTED,
                                StudentPaperContact.Status.MARKED
                            ]
                        else:
                            # 如果答题时间过了, 统计提交与保存的学生数量
                            query_param['status__in'] = [
                                StudentPaperContact.Status.SUBMITTED,
                                StudentPaperContact.Status.SAVED,
                                StudentPaperContact.Status.MARKED
                            ]
                        submitted_students_num = StudentPaperContact.objects.filter(**query_param).count()
                        paper_info[paper_id]['total_students_num'] = total_students_num
                        paper_info[paper_id]['submitted_students_num'] = submitted_students_num
            [p.pop('question_order') for _, p in paper_info.items()]

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "查询失败(请检查日志)", "code": 500, "data": {}}
            )
        return JsonResponse(
            {
                "result": True,
                "message": "查询成功",
                "code": 200,
                "data": list(paper_info.values()),
            }
        )

    # 以下的方法只可以以老师的身份请求
    user_info = "{}({})".format(request.user.class_number, request.user.name)
    try:
        course = Course.objects.get(id=json.loads(request.body).get('course_id'))
    except ObjectDoesNotExist as e:
        logger.exception("函数[Paper]: 访问数据库得不到对应的课程 {}".format(e))
        return JsonResponse(
            {"result": False, "code": 500, "message": "操作失败(请检查日志)", "data": {}}
        )
    if not (course.create_people == user_info or course.teacher == user_info):
        return JsonResponse(
            {"result": False, "code": 403, "message": "您没有操作权限！", "data": {}}
        )

    if method == "POST":
        """
        功能：卷子的增加
        输入：试卷类型，课程id，卷子名称，教师信息
        返回：卷子id
        """
        body = json.loads(request.body)
        paper_info_list = ["types", "course_id", "chapter_id", "paper_name", "teacher"]
        paper_info = {info: body.get(info) for info in paper_info_list}

        paper_info["teacher"] = str(Member.objects.get(id=request.user.id))
        # 当创建卷子的那一刻（还没有给卷子选题），将卷子状态设置为”草稿“
        paper_info["status"] = Paper.Status.DRAFT
        if None in paper_info.values():
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        try:
            paper = Paper.objects.create(**paper_info)
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "添加卷子失败(请检查日志)", "code": 500, "data": {}}
            )

        return JsonResponse(
            {
                "result": True,
                "message": "添加卷子成功",
                "code": 200,
                "data": {"paper_id": paper.id},
            }
        )

    if method == "DELETE":
        """
        功能：删除对应卷子
        输入：对应卷子id
        返回：是否成功
        """

        body = json.loads(request.body)
        paper_id = body.get("paper_id")
        if paper_id is None:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        try:
            paper = Paper.objects.filter(id=paper_id)
            if not paper:
                return_data = {
                    "result": False,
                    "message": "删除失败(数据库中没有该字段)",
                    "code": 412,
                    "data": {},
                }
            else:
                if paper.get().status != Paper.Status.DRAFT:
                    return_data = {
                        "result": False,
                        "message": "卷子不可以删除（只有草稿卷才可以删除）",
                        "code": 412,
                        "data": {},
                    }
                else:
                    result = paper.delete()[0]
                    if result:
                        question_num = PaperQuestionContact.objects.filter(
                            paper_id=paper_id
                        ).delete()[0]
                        _ = StudentPaperContact.objects.filter(
                            paper_id=paper_id
                        ).delete()[0]
                        return_data = {
                            "result": True,
                            "message": "删除成功(关联题目{}道)".format(question_num),
                            "code": 200,
                            "data": {},
                        }
                    else:
                        return_data = {
                            "result": False,
                            "message": "删除失败(数据库中没有该字段)",
                            "code": 412,
                            "data": {},
                        }

        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "删除卷子失败(请检查日志)", "code": 500, "data": {}}
            )

        return JsonResponse(return_data)

    if method == "PUT":
        """
        功能：卷子信息的修改(所有属性)
        输入：卷子id与修改信息与对应的值
        返回：是否成功
        """
        body = json.loads(request.body)
        paper_id = body.get("paper_id")
        update_info = body.get("update_info")
        # 起始时间同时设定
        if paper_id is None or (
                ("start_time" in update_info.keys()) ^ ("end_time" in update_info.keys())
        ):
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        if ("status" in update_info.keys()) and (
                update_info.get("status") not in Paper.status_list
        ):
            return JsonResponse(
                {"result": False, "code": 400, "message": "卷子状态码不存在", "data": {}}
            )
        try:
            paper = Paper.objects.filter(id=paper_id)
            if update_info.get("status") == Paper.Status.RELEASE and (
                    not paper.get().question_order or paper.get().question_order == "{}"
            ):
                return JsonResponse(
                    {"result": False, "code": 400, "message": "卷子没有题目，无法发布", "data": {}}
                )
            result = paper.update(**update_info)
            if result:
                return_data = {
                    "result": True,
                    "message": "修改成功",
                    "code": 200,
                    "data": {"paper_id": paper_id, "update_info": update_info},
                }
            else:
                return_data = {
                    "result": False,
                    "message": "修改失败(数据库中没有该字段)",
                    "code": 412,
                    "data": {},
                }

        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "卷子信息修改失败(请检查日志)", "code": 500, "data": {}}
            )

        return JsonResponse(return_data)

    else:
        return JsonResponse({"result": False, "code": 405, "message": "请求方法错误"})


@authority_manage
def manage_paper_question_contact(request):
    if request.method == "GET":
        """
        功能: 老师预览卷子
        输入: 卷子id
        返回: 卷子信息
        """
        paper_id = request.GET.get("paper_id")
        if not paper_id:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        try:
            paper = Paper.objects.get(id=paper_id)

            # 获取小题题目与大题题目信息
            if not paper.question_order or paper.question_order == "{}":
                return JsonResponse(
                    {"result": False, "code": 400, "message": "卷子没有题目", "data": {}}
                )
            order = json.loads(paper.question_order)
            custom_type_ids = order.keys()
            questions = {
                pq["id"]: pq
                for pq in PaperQuestionContact.objects.filter(
                    paper_id=paper_id
                ).values()
            }
            custom_types = {
                custom_type.id: custom_type.custom_type_name
                for custom_type in CustomType.objects.filter(id__in=custom_type_ids)
            }
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "code": 500, "message": "查询失败", "data": {}}
            )
        # 构造传输格式
        return_data = {}
        for title_id, question_ids in order.items():
            questions_list = []
            for question_id in question_ids:
                questions_list.append(questions[question_id])
            return_data[custom_types[int(title_id)]] = questions_list

        return JsonResponse(
            {"result": True, "message": "查询成功", "code": 201, "data": return_data}
        )

    if request.method == "POST":
        """
        功能: 保存卷子信息
        输入: 卷子与对应题目的信息
             {'大题题目id': [[小题id数组], [小题分数数组]]}
        返回: 保存成功或保存失败
        """
        body = json.loads(request.body)
        paper_info_list = body.get("paper_info")
        paper_id = body.get("paper_id")

        if paper_id is None or paper_info_list is None:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        PQContact_info = [
            "types",
            "question",
            "option_A",
            "option_B",
            "option_C",
            "option_D",
            "option_E",
            "answer",
            "explain",
        ]
        question_id_list, score_list, create_obj_list, title_info = [], [], [], []

        for info_dict in paper_info_list:
            for k, v in info_dict.items():
                question_id_list.extend(v[0])
                score_list.extend(v[1])
                title_info.append((k, len(v[1])))
        try:
            # 通过小题的id在题库中将所有小题的信息拿出来
            for question in Question.objects.filter(id__in=question_id_list):
                PQContact = PaperQuestionContact(
                    **({info: getattr(question, info) for info in PQContact_info})
                )
                PQContact.question_id = question.id
                PQContact.paper_id = paper_id
                PQContact.score = score_list[question_id_list.index(question.id)]
                create_obj_list.append(PQContact)

            with transaction.atomic():
                # 删除上一次的信息，将本次的题目数据进行添加
                PaperQuestionContact.objects.filter(paper_id=paper_id).delete()
                PaperQuestionContact.objects.bulk_create(create_obj_list)

                # 构造Json数据(顺序不能变)
                for PQContact in PaperQuestionContact.objects.filter(paper_id=paper_id):
                    score_list[
                        question_id_list.index(PQContact.question_id)
                    ] = PQContact.id

            sum = 0
            order_json = {}
            for title in title_info:
                order_json[title[0]] = score_list[sum: sum + title[1]]
                sum += title[1]

            Paper.objects.filter(id=paper_id).update(
                question_order=json.dumps(order_json)
            )

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "code": 500, "message": "保存失败(请检查日志)", "date": {}}
            )

        return JsonResponse(
            {"result": True, "code": 200, "message": "保存成功", "data": {}}
        )

    # 编辑习题 单个编辑
    if request.method == "PUT":
        req = json.loads(request.body)
        PQ_contact_id = req["PQ_contact_id"]
        can_edit_prop_list = [
            "custom_type_id",
            "types",
            "score",
            "question",
            "option_A",
            "option_B",
            "option_C",
            "option_D",
            "option_E",
            "answer",
            "explain",
        ]
        kwargs = {key: req[key] for key in can_edit_prop_list}
        try:
            PaperQuestionContact.objects.filter(id=PQ_contact_id).update(**kwargs)
            return JsonResponse(
                {"result": True, "message": "更新成功", "code": 201, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "更新失败", "code": 412, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
    else:
        return JsonResponse(
            {"result": False, "code": 405, "message": "请求方法错误", "data": {}}
        )


@authority_manage
def mark_or_check_paper(request):
    """
    功能: 老师批改卷子或看查学生答题情况的请求试卷内容
    输入: 卷子id与学生id
    返回: 题目信息, 学生的答案, 每道题的分数, 总分
    """
    if request.method == "GET":
        paper_id = request.GET.get("paper_id")
        student_id = request.GET.get("student_id")
        if not (paper_id and student_id):
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        try:
            paper = Paper.objects.get(id=paper_id)

            # 获取小题题目与大题题目信息
            order = json.loads(paper.question_order)
            custom_type_ids = order.keys()
            questions = {
                pq["id"]: pq
                for pq in PaperQuestionContact.objects.filter(
                    paper_id=paper_id
                ).values()
            }
            custom_types = {
                custom_type.id: custom_type.custom_type_name
                for custom_type in CustomType.objects.filter(id__in=custom_type_ids)
            }

            # 查询StudentAnswer表
            student_answer = {}
            PQContact_ids = questions.keys()
            for sa in StudentAnswer.objects.filter(
                    student_id=student_id,
                    PQContact_id__in=PQContact_ids
            ).values():
                student_answer[sa["PQContact_id"]] = (
                    sa["answer"],
                    sa["score"],
                    sa["id"],
                )
            # 查询StudentPaperContact表
            SPContact = StudentPaperContact.objects.filter(
                paper_id=paper_id, student_id=student_id
            )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "code": 500, "message": "查询失败(请检查日志)", "data": {}}
            )

        # 构造传输格式
        return_data = {}
        for title_id, question_ids in order.items():
            questions_list = []
            for question_id in question_ids:
                question = questions[question_id]
                question["student_answer"] = student_answer[question_id][0]
                question["student_score"] = student_answer[question_id][1]
                question["student_answer_id"] = student_answer[question_id][2]
                questions_list.append(question)
            return_data[custom_types[int(title_id)]] = questions_list
        return_data['total_score'] = SPContact.get().score if SPContact else 0
        return_data['StudentPaperContact_id'] = SPContact.get().id if SPContact else -1

        return JsonResponse(
            {"result": True, "code": 200, "message": "查询成功", "data": return_data}
        )

    else:
        return JsonResponse(
            {"result": False, "code": 405, "message": "请求方法错误", "data": {}}
        )


def answer_or_check_paper(request):
    """
    功能: 学生答题或看查批改情况请求卷子内容信息
    输入: 卷子id
    返回: 卷子信息
    """
    if request.method == "GET":
        paper_id = request.GET.get("paper_id")
        student_id = request.user.id
        if not paper_id:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        try:
            SPContact = StudentPaperContact.objects.filter(
                paper_id=paper_id, student_id=student_id
            )
            paper = Paper.objects.get(id=paper_id)
            if paper.status == Paper.Status.DRAFT:
                return JsonResponse(
                    {"result": False, "code": 400, "message": "没有权限查看", "data": {}}
                )
            # 获取小题题目与大题题目信息
            order = json.loads(paper.question_order)
            custom_type_ids = order.keys()
            questions = {
                pq["id"]: pq
                for pq in PaperQuestionContact.objects.filter(
                    paper_id=paper_id
                ).values()
            }
            custom_types = {
                custom_type.id: custom_type.custom_type_name
                for custom_type in CustomType.objects.filter(id__in=custom_type_ids)
            }

            # 查询StudentAnswer表
            student_answer = {}
            PQContact_ids = questions.keys()
            for sa in StudentAnswer.objects.filter(
                    PQContact_id__in=PQContact_ids,
                    student_id=student_id
            ).values():
                student_answer[sa["PQContact_id"]] = (
                    sa["answer"],
                    sa["score"],
                    sa["id"],
                )

        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "code": 500, "message": "查询失败(请检查日志)", "data": {}}
            )

        # 构造传输格式
        return_data = {}
        for title_id, question_ids in order.items():
            questions_list = []
            for question_id in question_ids:
                question = questions[question_id]
                if request.is_wechat():
                    question["question"] = "({}) {}".format(custom_types[int(title_id)], question["question"])
                if (
                        paper.status == Paper.Status.RELEASE
                        and paper.end_time > timezone.now()
                ):
                    # 为了防止一份卷子有id相同的两个题
                    question.pop("answer") if "answer" in question.keys() else None
                    question.pop("explain") if "explain" in question.keys() else None
                question["student_answer_id"] = (
                    student_answer[question_id][2]
                    if question_id in student_answer.keys()
                    else None
                )

                if question_id in student_answer.keys():
                    question["student_answer"] = (student_answer[question_id][0])
                else:
                    question["student_answer"] = None if question["types"] != Question.Types.MULTIPLE else "[]"

                if paper.status == Paper.Status.MARKED:
                    question["student_score"] = (
                        student_answer[question_id][1]
                        if question_id in student_answer.keys()
                        else None
                    )
                questions_list.append(question)
            return_data[custom_types[int(title_id)]] = questions_list
        if paper.status == Paper.Status.MARKED:
            return_data["total_score"] = SPContact.get().score if SPContact else 0
        return_data["cumulative_time"] = (
            int(SPContact.get().cumulative_time.total_seconds()) if SPContact else 0
        )
        return_data['status'] = SPContact.get().status if SPContact else StudentPaperContact.Status.NOT_ANSWER
        return JsonResponse(
            {"result": True, "code": 200, "message": "查询成功", "data": return_data}
        )

    else:
        return JsonResponse(
            {"result": False, "code": 405, "message": "请求方法错误", "data": {}}
        )


def get_paper_status(request):
    """
    功能: 查询卷子的状态
    输入: 卷子的id
    返回: 卷子的所属状态与截至时间
    """
    if request.method == "GET":
        paper_id = request.GET.get("paper_id")
        if not paper_id:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        try:
            paper = Paper.objects.get(id=paper_id)
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "卷子状态查询失败(请检查日志)", "code": 500, "data": {}}
            )

        return JsonResponse(
            {
                "result": True,
                "code": 200,
                "message": "查询成功",
                "data": {
                    "paper_id": paper_id,
                    "paper_status": paper.status,
                    "paper_end_time": paper.end_time,
                },
            }
        )
    else:
        return JsonResponse({"result": False, "code": 405, "message": "请求方法错误"})


@authority_manage
def synchronous_paper(request):
    if request.method == "PUT":
        """
        功能: 同步题库与卷子中的题目
        输入: 卷子id（列表）（可以更新多个卷子）
             题目id
        返回: 成功或失败
        """
        req = json.loads(request.body)
        paper_id_list = req["paper_id"]
        question_id = req["question_id"]
        if paper_id_list is None or question_id is None:
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )
        try:
            q = Question.objects.filter(id=question_id)
            PaperQuestionContact.objects.filter(
                paper_id__in=paper_id_list, question_id=question_id
            ).update(
                question_id=q.values()[0].get("id"),
                question=q.values()[0].get("question"),
                explain=q.values()[0].get("explain"),
                types=q.values()[0].get("types"),
                answer=q.values()[0].get("answer"),
                option_A=q.values()[0].get("option_A"),
                option_B=q.values()[0].get("option_B"),
                option_C=q.values()[0].get("option_C"),
                option_D=q.values()[0].get("option_D"),
                option_E=q.values()[0].get("option_E"),
            )
            return JsonResponse(
                {"result": True, "message": "更新成功", "code": 201, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "更新失败", "code": 412, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
    else:
        return JsonResponse(
            {"result": False, "code": 405, "message": "请求方法错误", "data": {}}
        )


def save_answer(request):
    """
    功能: 保存学生的答案
    输入: 卷子id, 题目与卷子关联id、学生的答案,
         save_or_submit: 1保存 0:提交
    注释: 前端将所有题目与卷子的关联id都要传入，学生没有作答的题目答案为None
    返回: 保存成功或失败
    """
    if request.method == "POST":
        body = json.loads(request.body)
        student_id = request.user.id
        request_params = [
            "answer_info",
            "paper_id",
            "save_or_submit",
            "cumulative_time",
        ]
        answer_info, paper_id, save_or_submit, cumulative_time = [
            body.get(param) for param in request_params
        ]
        if not (
                answer_info and paper_id and cumulative_time and save_or_submit in [0, 1]
        ):
            return JsonResponse(
                {"result": False, "code": 400, "message": "请求参数不完整", "data": {}}
            )

        PQContact_ids = []
        # 构造新数据
        create_list = []
        for info in answer_info:
            PQContact_ids.append(info["question_id"])

        PQContacts = {PQContact.id: PQContact for PQContact in
                      PaperQuestionContact.objects.filter(id__in=PQContact_ids)}

        try:
            for info in answer_info:
                flag = (PQContacts[info["question_id"]].types == Question.Types.MULTIPLE
                        and info["stu_answers"]) or PQContacts[info["question_id"]].types != Question.Types.MULTIPLE
                create_list.append(
                    StudentAnswer(
                        student_id=student_id,
                        PQContact_id=info["question_id"],
                        answer=info["stu_answers"] if flag else "[]",
                        score=0,
                    )
                )
        except KeyError as e:
            logger.exception('函数: [save_answer]: 读取表: [PaperQuestionContact]没有的题目id: [{}]'.format(e))
            return JsonResponse({'result': False, 'code': 500, 'message': '提交失败(请检查日志)', 'data': {}})

        # 数据库操作
        try:
            # 获得卷子对应的course_id
            course_id = Paper.objects.get(id=paper_id).course_id

            with transaction.atomic():
                # 删除上一个次提交答案字段
                StudentAnswer.objects.filter(
                    student_id=student_id, PQContact_id__in=PQContact_ids
                ).delete()
                # 保存本次的字段
                StudentAnswer.objects.bulk_create(create_list)
                # 更改学生对于这份卷子的状态，如果有答题记录就更新，如果没有则创建
                SPContact = StudentPaperContact.objects.filter(
                    course_id=course_id, paper_id=paper_id, student_id=student_id
                )
                if SPContact:
                    SPContact.update(
                        status=StudentPaperContact.Status.SAVED
                        if save_or_submit
                        else StudentPaperContact.Status.SUBMITTED,
                        cumulative_time=timedelta(seconds=cumulative_time),
                    )
                else:
                    StudentPaperContact.objects.create(
                        course_id=course_id,
                        paper_id=paper_id,
                        student_id=student_id,
                        status=StudentPaperContact.Status.SAVED
                        if save_or_submit
                        else StudentPaperContact.Status.SUBMITTED,
                        cumulative_time=timedelta(seconds=cumulative_time),
                    )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "code": 500, "message": "提交失败", "data": {}}
            )

        # 起一个celery任务去判断客观题的正误
        judge_objective.delay(PQContact_ids, student_id)
        return JsonResponse(
            {"result": True, "code": 200, "message": "提交成功", "data": {}}
        )
    else:
        return JsonResponse(
            {"result": False, "code": 405, "message": "请求方法错误", "data": {}}
        )


@authority_manage
def teacher_correct_paper(request):
    if request.method == "POST":
        req = json.loads(request.body)  # 需要传StudentAnswer表的id和学生的分数以及卷子id
        student_score_list = req.get("student_answer_list")
        student_paper_contact_id = req.get("student_paper_contact_id")
        update_score_list = []
        total_score = 0
        for student_score in student_score_list:
            update_score_list.append(StudentAnswer(**student_score))
            total_score += student_score["score"]
        try:
            StudentAnswer.objects.bulk_update(
                update_score_list, ["score"]
            )  # 批量保存学生与题目的分数
            student_paper_score = StudentPaperContact.objects.get(
                id=student_paper_contact_id
            )
            student_paper_score.score = total_score
            student_paper_score.status = StudentPaperContact.Status.MARKED
            student_paper_score.save()
            return JsonResponse(
                {"result": True, "message": "卷子批改成功", "code": 200, "data": []}
            )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "result": False,
                    "message": "卷子批改失败",
                    "code": 412,
                    "data": [],
                }
            )
    else:
        return JsonResponse(
            {
                "result": False,
                "message": "请求方法错误",
                "code": 400,
                "data": [],
            }
        )


@authority_manage
def get_student_answer_info(request):
    """
    功能: 看查这份卷子的那些学生作答了，那些没有作答
    输入: paper_id
    返回: 作答的学生信息列表，未作答的学生信息列表（学号 + 名字）
    """
    if request.method == 'GET':
        paper_id = request.GET.get('paper_id')
        if not paper_id:
            return JsonResponse({'result': False, 'code': 400, 'message': '请求参数不完整', 'data': {}})

        try:
            paper = Paper.objects.get(id=paper_id)
            all_student_ids = [i.user_id for i in UserCourseContact.objects.filter(course_id=paper.course_id)]

            all_student_info = {user.id: user for user in Member.objects.filter(id__in=all_student_ids)}
            answer_student_info = {int(user_paper.student_id): user_paper for user_paper in
                                   StudentPaperContact.objects.filter(paper_id=paper.id, course_id=paper.course_id)}
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse({
                'result': False,
                'code': 500,
                'message': '查询失败(请检查日志)',
                'data': {}
            })

        # 构造数据
        return_data = {'submitted': [], 'not_submitted': []}
        submitted = all_student_info.keys() & answer_student_info.keys()
        not_submitted = all_student_info.keys() - answer_student_info.keys()
        return_data['submitted'] = [{
            'student_id': student_id,
            'name': all_student_info[student_id].name,
            'class_number': all_student_info[student_id].class_number,
            'class': all_student_info[student_id].professional_class,
            'status': answer_student_info[student_id].status,
        } for student_id in submitted]
        return_data['not_submitted'] = [{
            'student_id': student_id,
            'name': all_student_info[student_id].name,
            'class_number': all_student_info[student_id].class_number,
            'class': all_student_info[student_id].professional_class
        } for student_id in not_submitted]

        return JsonResponse({
            'result': True,
            'message': '查询成功',
            'code': 200,
            'data': return_data,
        })

    else:
        return JsonResponse(
            {
                'result': False,
                'message': '请求方法错误',
                'code': 400,
                'data': [],
            }
        )


@authority_manage
def check_students_score(request):
    """
    功能: 老师根据卷子获得本张卷子的所有人的答题情况
    输入: paper_id
    返回: 卷子所属课程的成员的答题情况
    """
    if request.method == 'GET':
        paper_id = request.GET.get('paper_id')
        if not paper_id:
            return JsonResponse({'result': False, 'code': 400, 'message': '请求参数不完整', 'data': {}})
        try:
            if Paper.objects.get(id=paper_id).status != Paper.Status.MARKED:
                return JsonResponse({'result': False, 'code': 400, 'message': '卷子未批改完成', 'data': {}})
            paper_course = Paper.objects.get(id=paper_id).course_id
            student_ids = UserCourseContact.objects.filter(course_id=paper_course).values("user_id")
            students = {student.id: (student.name, student.class_number) for student in
                        Member.objects.filter(id__in=student_ids)}
            student_score = {int(student.student_id): student.score for student in
                             StudentPaperContact.objects.filter(paper_id=paper_id)}
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse({'result': False, 'code': 500, 'message': '查询失败', 'data': {}})

        return_data = []
        for student_id, student_info in students.items():
            if student_id in student_score.keys():
                return_data.append({
                    'student_id': student_id,
                    'student_name': student_info[0],
                    'student_class_number': student_info[1],
                    'score': student_score[student_id]
                })
            else:
                return_data.append({
                    'student_id': student_id,
                    'student_name': student_info[0],
                    'student_class_number': student_info[1],
                    'score': 0
                })
        return JsonResponse({
            'result': True,
            'message': '查询成功',
            'code': 200,
            'data': return_data,
        })


# 批量绘制图片+批量存储
# 将图片存储在指定文件夹（附带创建文件夹）+用循环创建文件名
def log(request):
    if request.method == "POST":
        try:
            string_list = [
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'l', 'm', 'm', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
            ]
            number_list = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'
            ]
            strings_str = ""
            for pop in string_list:
                strings = request.POST.get(pop)
                strings_str = strings_str + strings
                strings = request.POST.get(',')
                strings_str = strings_str + strings
                for pip in number_list:
                    strings = request.POST.get(pip)
                    strings_str = strings_str + strings
            param_list = []
            param_list = strings_str.split(",")
            param = []
            j = 1
            for pop in param_list:
                if j % 2 == 1:
                   test_list = []
                   test_list.append(pop)
                else :
                    if j%2 == 0 :
                        pop = int(pop)
                        test_list.append(pop)
                        param.append(tuple(test_list))
                j = j+1
            # param = [('a', 3),('b', 12),('c', 6),('d', 1),('e', 11),('f', 2)]
            result=[str(i) for i in param]
            d=''.join(result)
            # print(d)
            huffman_tree = huffman.HuffmanTree()
            huffman_tree.creat_HuffmanTree(param)

            huffman.ShowHuffmanBiTree(huffman_tree.root).save_BiTree_1()
            huffman.ShowHuffmanBiTree(huffman_tree.root).PostOrderTree(huffman_tree.root)
            # print("前序遍历:")
            result=[str(i) for i in huffman.nalue_1]
            a=''.join(result)
            # print(a)
            huffman.ShowHuffmanBiTree(huffman_tree.root).PreOrderTree(huffman_tree.root)
            # print("后序遍历:")
            result=[str(i) for i in huffman.nalue_2]
            b=''.join(result)
            # print(b)
            huffman.ShowHuffmanBiTree(huffman_tree.root).InOrderTree(huffman_tree.root)
            # print("中序遍历:")
            result=[str(i) for i in huffman.nalue_3]
            c=''.join(result)
            # print(c)
            f = huffman.figure_save_path+"\\"+huffman.figure_save+".png"

            # print(f)
            with open(f, "rb") as file:
                image = file.read()
            Binary_tree_1.objects.create(img=image, frontanswer=d, firstanswer=a, middleanswer=c,endanswer=b, explain='binarytree')
        except:
            {}


def getProductByID(request):
    if request.method == "GET":
        mod = Binary_tree_1.objects  # 获取DProduct模型的Model操作对象
        ProductList = mod.filter(product_id=Binary_tree_1.id).values()
        ProductList = list(ProductList)  # 转化为列表属性
        return JsonResponse({'data':ProductList})
