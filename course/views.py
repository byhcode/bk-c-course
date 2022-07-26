import json
import logging

import xlrd
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import FileResponse, JsonResponse

from blueapps.core.exceptions import DatabaseError

from .models import Course, Member, UserCourseContact
from .utils.verify_account import identify_user

# Create your views here.


def update_user_info(request):
    """
    更新用户信息
    """
    if request.method == "POST":
        user = request.user
        member_info = json.loads(request.body)
        try:
            can_edit_prop_list = [
                "phone_number",
                "qq_number",
                "email_number",
                "wechat_number",
            ]
            kwargs = {prop: member_info[prop] for prop in can_edit_prop_list}
            Member.objects.filter(id=user.id).update(**kwargs)
            return JsonResponse(
                {"result": True, "message": "更新成功", "code": 201, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
        except IntegrityError or DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {"result": False, "message": "更新失败", "code": 412, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )


logger = logging.getLogger("root")


def is_teacher(fun):
    def inner(request, *args, **kwargs):
        try:
            user_id = request.user.id
            identity = Member.objects.filter(id=user_id).values(
                "identity"
            )  # 取出数据表中的identity值
            if (
                identity.first()["identity"] == Member.Identity.TEACHER
            ):  # 将取出的Queryset转化为字典与字符串比较
                return fun(request, *args, **kwargs)
            else:
                return JsonResponse(
                    {"result": False, "code": 403, "message": "您没有操作权限！", "data": []}
                )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"result": False, "code": 401, "message": "请求错误！用户id不存在", "data": []}
            )  # 返回信息

    return inner


@is_teacher
def manage_course(request):
    # 增
    if request.method == "POST":
        req = json.loads(request.body)
        course_name = req.get("course_name")  # 想创建的课程名称
        teacher = req.get("teacher")
        teacher_id = req.get("teacher_id")
        course_introduction = req.get("course_introduction")  # 课程简介
        manage_student = req.get("manage_student")  # 学生管理员
        manage_student_str = ",".join(manage_student)
        manage_student_ids = req.get("manage_student_ids")
        manage_student_list = []
        try:
            news_course_info = Course.objects.create(
                course_name=course_name,
                course_introduction=course_introduction,
                teacher=teacher,
                create_people="{}({})".format(
                    request.user.class_number, request.user.name
                ),
                manage_student=manage_student_str,
            )  # 将得到的数据加到course表
            UserCourseContact.objects.update_or_create(
                user_id=request.user.id, course_id=news_course_info.id
            )
            UserCourseContact.objects.update_or_create(
                user_id=teacher_id, course_id=news_course_info.id
            )
            for manage_student_id in manage_student_ids:
                manage_student_list.append(
                    UserCourseContact(
                        user_id=manage_student_id, course_id=news_course_info.id
                    )
                )
            with transaction.atomic():
                UserCourseContact.objects.filter(
                    user_id__in=manage_student_ids, course_id=news_course_info.id
                ).delete()
                UserCourseContact.objects.bulk_create(manage_student_list)
            return JsonResponse(
                {"result": True, "message": "增加成功", "code": 201, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "result": True,
                    "message": "增加失败，请检查您输入的信息或者身份信息是否完善",
                    "code": 412,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )
    # 删
    if request.method == "DELETE":
        course_ids = json.loads(request.GET.get("course_id"))
        user_info = "{}({})".format(request.user.class_number, request.user.name)
        if not course_ids:
            return JsonResponse(
                {
                    "result": False,
                    "message": "删除失败！课程id不能为空",
                    "code": 400,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )
        del_courses = Course.objects.filter(id__in=course_ids)
        for del_course in del_courses:
            if not (
                del_course.create_people == user_info or del_course.teacher == user_info
            ):
                return JsonResponse(
                    {
                        "result": False,
                        "message": "删除失败，权限不够",
                        "code": 403,
                        "data": [],
                    },
                    json_dumps_params={"ensure_ascii": False},
                )
        try:
            with transaction.atomic():
                Course.objects.filter(id__in=course_ids).delete()
                UserCourseContact.objects.filter(course_id__in=course_ids).delete()
                return JsonResponse(
                    {
                        "result": True,
                        "message": "删除成功",
                        "code": 200,
                        "data": [],
                    },
                    json_dumps_params={"ensure_ascii": False},
                )
        except ObjectDoesNotExist as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "result": False,
                    "message": "删除失败！",
                    "code": 412,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )

    # 改
    if request.method == "PUT":
        req = json.loads(request.body)
        course_id = req.pop("id", "")
        manage_student = req.pop("manage_student")  # 学生管理员
        manage_student_str = ",".join(manage_student)
        if not course_id:
            return JsonResponse(
                {
                    "result": False,
                    "message": "修改失败！课程id不能为空",
                    "code": 400,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )
        try:
            user_info = "{}({})".format(request.user.class_number, request.user.name)
            course = Course.objects.get(id=course_id)
            if course.create_people == user_info or course.teacher == user_info:
                course.manage_student = manage_student_str
                for k, v in req.items():
                    setattr(course, k, v)
                course.save()
                return JsonResponse(
                    {"result": True, "message": "修改成功", "code": 200, "data": []},
                    json_dumps_params={"ensure_ascii": False},
                )
            else:
                return JsonResponse(
                    {
                        "result": False,
                        "message": "修改失败，权限不够",
                        "code": 403,
                        "data": [],
                    },
                    json_dumps_params={"ensure_ascii": False},
                )
        except DatabaseError as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "result": False,
                    "message": "修改失败",
                    "code": 412,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )


# 查课程列表
def search_courses_by_userid(request):
    if request.method == "GET":
        courses_list = []
        course_ids = UserCourseContact.objects.filter(
            user_id=request.user.id
        ).values_list("course_id", flat=True)
        courses = Course.objects.filter(id__in=course_ids)
        for course in courses:
            manage_student = course.manage_student.split(",")
            courses_list.append(
                {
                    "course_id": course.id,
                    "course_name": course.course_name,
                    "course_introduction": course.course_introduction,
                    "teacher": course.teacher,
                    "create_people": course.create_people,
                    "manage_student": manage_student,
                }
            )
        return JsonResponse(
            {
                "result": True,
                "message": "查询成功",
                "code": 200,
                "data": courses_list,
            },
            json_dumps_params={"ensure_ascii": False},
        )


def search_member_info(request):
    if request.method == "GET":
        member_identify = request.GET.get("member_identify")  # 传递用户身份
        member_info_list = []
        member_info = {}
        members = Member.objects.filter(identity=member_identify)
        for member in members:
            member_info["member_id"] = member.id  # 返回用户id
            member_info["member_display_name"] = "{}({})".format(
                member.class_number, member.name
            )  # 返回工号（姓名）
            member_info["professional_class"] = member.professional_class  # 用户专业
            member_info["class_number"] = member.class_number  # 用户学号
            member_info["college"] = member.college  # 用户学院
            member_info["name"] = member.name  # 用户姓名
            member_info["gender"] = member.gender  # 用户性别
            member_info_list.append(member_info.copy())
        return JsonResponse(
            {
                "result": True,
                "message": "显示成功",
                "code": 200,
                "data": member_info_list,
            },
            json_dumps_params={"ensure_ascii": False},
        )


# 老师为指定课程导入学生信息
def import_student_excel(request):
    excel_files = request.FILES.get("excel_file")
    suffix = excel_files.name.split(".")[-1]
    course_id = request.POST.get("course_id")
    if suffix == "xls":
        data = xlrd.open_workbook(
            filename=None, file_contents=excel_files.read(), formatting_info=True
        )
    else:
        return JsonResponse(
            {
                "result": False,
                "message": "导入文件错误，请检查导入文件是否为excel后缀名为（.xls）格式",
                "code": 406,
                "data": [],
            },
            json_dumps_params={"ensure_ascii": False},
        )
    table = data.sheet_by_index(0)
    student_class_number = set()
    student_info_list = []
    student_member_list = []
    student_contact_list = []
    student_info = {}
    row_sign = 0
    row_err = 0
    rows = table.nrows
    values_0 = table.row_values(0)
    if rows != 1:
        values_1 = table.row_values(1)
        if not (values_0[0] == "教学班点名册" and values_1[0] == "学年"):
            return JsonResponse(
                {
                    "result": False,
                    "message": "文件格式错误,请检查文件内容是否符合模板规范",
                    "code": 403,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )
        else:
            values_4 = table.row_values(4)
            if values_4[0] == "" or values_4[2] == "" or values_4[4] == "":
                return JsonResponse(
                    {
                        "result": False,
                        "message": "请检查您的excel表中的数据是否齐全",
                        "code": 403,
                        "data": [],
                    },
                    json_dumps_params={"ensure_ascii": False},
                )
            try:
                for row in range(4, rows):
                    row_err = row
                    row_values = table.row_values(row)
                    if not (
                        row_values[0] == ""
                        and row_values[2] == ""
                        and row_values[4] == ""
                    ):
                        student_info["class_number"] = int(row_values[0])
                        student_info["professional_class"] = row_values[4]
                        student_info["name"] = row_values[2]
                        student_info_list.append(student_info.copy())
                        student_class_number.add(int(row_values[0]))
            except SyntaxError as e:
                logger.exception(e)
                return JsonResponse(
                    {
                        "result": False,
                        "message": "导入失败，请检查第{}行的学号是否输入非数字字符".format(row_err),
                        "code": 412,
                        "data": [],
                    },
                    json_dumps_params={"ensure_ascii": False},
                )
            user_class_number = Member.objects.filter(
                class_number__in=student_class_number
            ).values_list("class_number", flat=True)
            user_ids = UserCourseContact.objects.filter(
                course_id=course_id
            ).values_list("user_id", flat=True)
            user_ids_list = list(user_ids)
            user_class_number_list = list(user_class_number)
            for student in student_info_list:
                if str(student["class_number"]) not in user_class_number_list:
                    student_member_list.append(
                        Member(
                            username="{}X".format(student["class_number"]),
                            class_number=student["class_number"],
                            name=student["name"],
                            professional_class=student["professional_class"],
                        )
                    )
            Member.objects.bulk_create(student_member_list)
            objs = Member.objects.filter(
                class_number__in=student_class_number
            ).values_list("id", flat=True)
            objs_list = list(objs)
            for obj in objs_list:
                if obj not in user_ids_list:
                    student_contact_list.append(
                        UserCourseContact(user_id=obj, course_id=course_id)
                    )
                    row_sign = row_sign + 1
            UserCourseContact.objects.bulk_create(student_contact_list)
            return JsonResponse(
                {
                    "result": True,
                    "message": "导入成功,共导入{}行数据".format(row_sign),
                    "code": 200,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )
    return JsonResponse(
        {
            "result": False,
            "message": "请检查您的excel表中的数据是否齐全",
            "code": 403,
            "data": [],
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 根据课程id,为课程新加学生
def add_course_student(request):
    req = json.loads(request.body)
    course_id = req.get("course_id")
    student_id_list = req.get("student_id")
    student_list = []
    if not course_id:
        return JsonResponse(
            {
                "result": False,
                "message": "增加失败，课程id不存在",
                "code": 406,
                "data": [],
            },
            json_dumps_params={"ensure_ascii": False},
        )
    user_ids = UserCourseContact.objects.filter(course_id=course_id).values_list(
        "user_id", flat=True
    )
    user_ids_list = list(user_ids)
    for student in student_id_list:
        if student not in user_ids_list:
            student_list.append(UserCourseContact(user_id=student, course_id=course_id))
    if not student_list:
        return JsonResponse(
            {
                "result": False,
                "message": "增加失败，请勿重复添加关系",
                "code": 403,
                "data": [],
            },
            json_dumps_params={"ensure_ascii": False},
        )
    UserCourseContact.objects.bulk_create(student_list)
    return JsonResponse(
        {
            "result": True,
            "message": "增加成功, 已经去除重复关系",
            "code": 200,
            "data": [],
        },
        json_dumps_params={"ensure_ascii": False},
    )


# 根据学号新增用户
def add_course_member(request):
    req = json.loads(request.body)
    course_id = req.get("course_id")
    member_class_number = req.get("class_number")
    member_name = req.get("name")
    if Member.objects.filter(class_number=member_class_number).exists():
        user = Member.objects.get(class_number=member_class_number)
        if UserCourseContact.objects.filter(
            course_id=course_id, user_id=user.id
        ).exists():
            return JsonResponse(
                {
                    "result": False,
                    "message": "添加失败，学生已存在于该课程",
                    "code": 412,
                    "data": [],
                },
            )
        else:
            UserCourseContact.objects.update_or_create(
                course_id=course_id, user_id=user.id
            )
            return JsonResponse(
                {
                    "result": True,
                    "message": "添加成功",
                    "code": 200,
                    "data": [],
                },
            )
    else:
        user = Member.objects.create(
            username="{}X".format(member_class_number),
            class_number=member_class_number,
            name=member_name,
            identity="NOT_CERTIFIED",
        )
        UserCourseContact.objects.create(course_id=course_id, user_id=user.id)
        return JsonResponse(
            {
                "result": True,
                "message": "添加成功",
                "code": 200,
                "data": [],
            },
        )


# 下载学生点名册模板
def download_student_excel_template(request):
    file = open("static/files/studentTemplate.xls", "rb")
    response = FileResponse(file)
    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = 'attachment;filename="studentTemplate.xls"'
    return response


def download_student_excel_template_url(request):
    host_path = request.get_host()
    url = "{}/course/download_student_excel_template/".format(host_path)
    return JsonResponse(
        {
            "result": True,
            "message": "跳转成功",
            "url": url,
            "code": 200,
            "data": [],
        },
        json_dumps_params={"ensure_ascii": False},
    )


def delete_student_course_contact(request):
    if request.method == "DELETE":
        course_id = request.GET.get("course_id")
        student_ids = json.loads(request.GET.get("student_id"))  # 传递学生id列表
        student_identities = Member.objects.filter(id__in=student_ids).values_list(
            "identity", flat=True
        )
        i = 0
        for student_identity in student_identities:
            if student_identity == Member.Identity.TEACHER:
                del student_ids[i]
            else:
                i += 1
        try:
            UserCourseContact.objects.filter(
                user_id__in=student_ids, course_id=course_id
            ).delete()
            return JsonResponse(
                {"result": True, "message": "删除成功", "code": 200, "data": []},
                json_dumps_params={"ensure_ascii": False},
            )
        except ObjectDoesNotExist as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "result": False,
                    "message": "删除失败！,课程号不存在",
                    "code": 412,
                    "data": [],
                },
                json_dumps_params={"ensure_ascii": False},
            )


# 获取课程学生列表
def search_course_student(request):
    student_info = {}
    student_list = []
    course_id = request.GET.get("course_id")
    if not course_id:
        return JsonResponse(
            {
                "result": False,
                "message": "课程id不能为空",
                "code": 406,
                "data": [],
            },
        )
    try:
        user_ids = UserCourseContact.objects.filter(course_id=course_id).values_list(
            "user_id", flat=True
        )
        if not user_ids:
            return JsonResponse(
                {
                    "result": True,
                    "message": "该课程暂无学生",
                    "code": 406,
                    "data": [],
                },
            )
        user_ids_list = list(user_ids)
        user_objects = Member.objects.in_bulk(user_ids_list)
        for index, user_object in user_objects.items():
            student_info["student"] = "{}({})".format(
                user_object.class_number, user_object.name
            )
            student_info["student_id"] = user_object.id
            student_info["id"] = user_object.id
            student_info["name"] = user_object.name
            student_info["class_number"] = user_object.class_number
            student_info["professional_class"] = user_object.professional_class
            student_info["identify"] = user_object.identity
            student_list.append(student_info.copy())
        student_list.sort(key=lambda x: x['identify'], reverse=True)  # 对课程成员展示排序
        page_size = request.GET.get("page_size", 10)
        paginator = Paginator(student_list, page_size)  # 分页器对象，10是每页展示的数据条数
        page = request.GET.get("page", "1")  # 获取当前页码，默认为第一页
        page_info_list = list(paginator.get_page(page))  # 更新students为对应页码数据
        return JsonResponse(
            {
                "result": True,
                "message": "成功",
                "code": 200,
                "data": page_info_list,  # 当前页数据
                "page": int(page),  # 这是是返回当前页码给前端
                "count": len(student_list),
            },
            json_dumps_params={"ensure_ascii": False},
        )
    except DatabaseError:
        return JsonResponse(
            {
                "result": False,
                "message": "获取失败",
                "code": 400,
                "data": [],
            },
            json_dumps_params={"ensure_ascii": False},
        )


# 下拉显示课程列表
def get_course_list(request):
    if request.method == "GET":
        course_list = []
        course_ids = UserCourseContact.objects.filter(
            user_id=request.user.id
        ).values_list("course_id", flat=True)
        course_ids_list = list(course_ids)
        courses = Course.objects.filter(id__in=course_ids_list)
        for course in courses:
            course_list.append(
                {
                    "course_id": course.id,
                    "course_name": "({}){}({})".format(
                        course.id, course.course_name, course.teacher
                    ),
                }
            )
        return JsonResponse(
            {
                "result": True,
                "message": "显示成功",
                "code": 200,
                "data": course_list,
            },
            json_dumps_params={"ensure_ascii": False},
        )


def verify_school_user(request):
    """
    功能：通过学分制的账号密码, 进行验证, 并绑定用户
    输入：request头中带有username,password
    返回：认证成功： result: True; data: user_id
         认证失败： result: False; data: []; message：错误信息
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            username = body.get("username")
            password = body.get("password")
            if not username or not password:
                return JsonResponse(
                    {"result": False, "message": "请求参数不完整", "code": 400, "data": {}}
                )

            if username == "test_teacher":
                member = Member.objects.get(username=request.user.username)
                member.identity = "TEACHER"
                member.save()
                return JsonResponse(
                    {
                        "result": True,
                        "code": 201,
                        "message": "mock老师认证成功",
                        "data": {"user_id": member.id},
                    }
                )

            try:
                result, user_info, message = identify_user(
                    username=username, password=password
                )
            except Exception as e:
                logger.exception('函数: [verify_school_user]: 获取身份信息失败. 具体问题: {}'.format(e))
                return JsonResponse({'result': False, 'code': 500, 'message': '认证失败(请检查日志)', 'data': {}})

            if result:
                kwargs = {
                    "class_number": user_info["user_name"],
                    "name": user_info["user_real_name"],
                    "professional_class": user_info["user_major"],
                    "gender": Member.Gender.MAN
                    if user_info["user_sex"] == "男"
                    else Member.Gender.WOMAN,
                    "identity": Member.Identity.STUDENT,
                    "college": user_info["user_college"],
                    "classroom": user_info["user_class"],
                }

                # 如果是微信小程序端进行认证
                if request.is_wechat():
                    user, _ = Member.objects.get_or_create(
                        username="{}X".format(username)
                    )
                    kwargs.update(
                        {
                            "openid": request.user.openid,
                        }
                    )
                else:
                    user = Member.objects.get(username=request.user.username)

                if user.identity != Member.Identity.NOT_CERTIFIED:
                    return JsonResponse({'result': False, 'message': '该账号已经被认证, 如果需要修改认证信息请联系管理员', 'code': 400, 'data': {}})

                for attr_name, attr_value in kwargs.items():
                    setattr(user, attr_name, attr_value)

                user.save()
                data = {
                    "result": True,
                    "message": message,
                    "code": 201,
                    "data": {},
                }
                return JsonResponse(data)
            else:
                data = {"result": False, "message": message, "data": []}
                return JsonResponse(data)
        except Exception as e:
            data = {"result": False, "message": e, "code": 500, "data": []}  # 后端出错
            return JsonResponse(data)


# 下载出题模板
def download_set_question_excel_template_url(request):
    host_path = request.get_host()
    url = "{}/course/download_set_question_excel_template/".format(host_path)
    return JsonResponse(
        {
            "result": True,
            "message": "跳转成功",
            "url": url,
            "code": 200,
            "data": [],
        },
        json_dumps_params={"ensure_ascii": False},
    )

