# Generated by Django 2.2.6 on 2022-01-21 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_member_college'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.IntegerField(verbose_name='课程id')),
                ('chapter_name', models.TextField(verbose_name='章节名称')),
            ],
        ),
        migrations.CreateModel(
            name='CustomType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.IntegerField(verbose_name='课程id')),
                ('custom_type_name', models.TextField(verbose_name='题目类型名称')),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('types', models.CharField(choices=[('EXERCISE', '练习卷'), ('EXAM', '测试卷')], max_length=10, verbose_name='试卷类型')),
                ('course_id', models.IntegerField(verbose_name='卷子所属课程id')),
                ('chapter_id', models.IntegerField(blank=True, null=True, verbose_name='卷子所属章节id')),
                ('paper_name', models.CharField(max_length=255, verbose_name='卷子名字')),
                ('teacher', models.CharField(max_length=90, verbose_name='教师姓名')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='截至时间')),
                ('status', models.CharField(choices=[('NOT_START', '未开始'), ('ON_GOING', '开始'), ('FINISHED', '结束')], max_length=10, verbose_name='卷子状态')),
            ],
        ),
        migrations.CreateModel(
            name='PaperQuestionContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paper_id', models.IntegerField(verbose_name='卷子id')),
                ('custom_type_id', models.IntegerField(verbose_name='卷子中题目自定义类型id')),
                ('types', models.CharField(choices=[('EXERCISE', '练习卷'), ('EXAM', '测试卷')], max_length=20, verbose_name='题目类型')),
                ('score', models.FloatField(default=1, verbose_name='题目分数')),
                ('question_id', models.IntegerField(verbose_name='题目id')),
                ('question', models.TextField(verbose_name='题目')),
                ('option_A', models.TextField(blank=True, null=True, verbose_name='选项A')),
                ('option_B', models.TextField(blank=True, null=True, verbose_name='选项B')),
                ('option_C', models.TextField(blank=True, null=True, verbose_name='选项C')),
                ('option_D', models.TextField(blank=True, null=True, verbose_name='选项D')),
                ('option_E', models.TextField(blank=True, null=True, verbose_name='选项E')),
                ('answer', models.TextField(verbose_name='问题答案')),
                ('explain', models.TextField(blank=True, default='无', null=True, verbose_name='答案解析')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.IntegerField(verbose_name='题目所属课程id')),
                ('chapter_id', models.IntegerField(verbose_name='题目所属章节id')),
                ('types', models.CharField(choices=[('SINGLE', '单选题'), ('MULTIPLE', '多选题'), ('COMPLETION', '填空题'), ('JUDGE', '判断题'), ('SHORT_ANSWER', '简答题')], max_length=20, verbose_name='题目类型')),
                ('question', models.TextField(verbose_name='题目')),
                ('option_A', models.TextField(blank=True, null=True, verbose_name='选项A')),
                ('option_B', models.TextField(blank=True, null=True, verbose_name='选项B')),
                ('option_C', models.TextField(blank=True, null=True, verbose_name='选项C')),
                ('option_D', models.TextField(blank=True, null=True, verbose_name='选项D')),
                ('option_E', models.TextField(blank=True, null=True, verbose_name='选项E')),
                ('answer', models.TextField(verbose_name='问题答案')),
                ('explain', models.TextField(blank=True, default='无', null=True, verbose_name='答案解析')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(verbose_name='学生id')),
                ('PQContact_id', models.IntegerField(verbose_name='卷子与题目关联表单的id')),
                ('answer', models.TextField(verbose_name='学生的作答')),
                ('score', models.FloatField(blank=True, null=True, verbose_name='学生这道题的得分')),
            ],
        ),
    ]
