from datetime import datetime
import re
from django.utils.crypto import get_random_string
from django.core.mail import get_connection, EmailMessage, send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import *
from .serializers import UserSerializer

RU_NAME_RE = re.compile(r'^[А-ЯЁа-яё]+$')
REQ_COLS = ['Тип', 'Вопрос', 'Ответ']
MARKER = 'ДАННЫЕ:'
CHOICE_SPLIT = re.compile(r'\(\d+\)')
TYPE_MAP = {
    'Один ответ':        'one',
    'Несколько ответов': 'multi',
    'Строка':            'text',
    'Таблица':           'table',
}

def validate_and_parse_questions(df):
    """
    Проверяет, что в Excel три колонки [Тип, Вопрос, Ответ],
    затем валидирует и парсит каждую строку в dict:
      {
        'qtype': 'one'|'multi'|'text'|'table',
        'text':   "…",
        'payload': {...},
        'correct': ...,
      }
    Возвращает (parsed_rows, errors).
    """
    # 1) колонки
    if list(df.columns) != REQ_COLS:
        return [], {None: f"Ожидаются колонки: {REQ_COLS}"}

    parsed, errors = [], {}

    for idx, row in df.iterrows():
        row_errors = {}
        ri = idx + 2  # строка в Excel

        # читаем ячейки
        human_type = row['Тип']
        qcell      = str(row['Вопрос'] or '').strip()
        acell      = row['Ответ']
        print(qcell)

        # A) Тип → колонка A
        if human_type not in TYPE_MAP:
            row_errors[f"A{ri}"] = f"Неверный Тип «{human_type}»"
        else:
            qtype = TYPE_MAP[human_type]

        # B) Разделяем текст/контент → колонка B
        if 'qtype' in locals() and qtype != 'text':
            if MARKER not in qcell:
                row_errors[f"B{ri}"] = f"Для типа «{human_type}» нужен маркер «{MARKER}»"
            else:
                before, after = qcell.split(MARKER, 1)
                question_text = before.strip()
                content       = after.strip()
        elif 'qtype' in locals():
            question_text = qcell
            content       = None

        # Если уже есть ошибки по этой строке, пропускаем дальнейшую валидацию
        if row_errors:
            errors.update(row_errors)
            continue

        # C) Парсим по типу
        if qtype in ('one', 'multi'):
            # варианты — колонка B
            if not content.startswith('(1)'):
                row_errors[f"B{ri}"] = "Варианты должны начинаться с «(1)»"
            parts = [p.strip() for p in CHOICE_SPLIT.split(content) if p.strip()]
            if len(parts) < 2:
                row_errors[f"B{ri}"] = "Нужно минимум 2 варианта через «(1)», «(2)»"
            if not row_errors:
                choices = parts
                # правильные номера (колонка C)
                if acell is None or str(acell).strip()=='':
                    row_errors[f"C{ri}"] = "Укажите номер(а) правильных вариантов"
                else:
                    nums = [int(x) for x in re.findall(r'\d+', str(acell))]
                    if qtype=='one' and len(nums)!=1:
                        row_errors[f"C{ri}"] = "Для «Один ответ» нужен ровно один номер"
                    if qtype=='multi' and len(nums)<2:
                        row_errors[f"C{ri}"] = "Для «Несколько ответов» нужно минимум 2 номера"
                    correct = ",".join(str(n) for n in nums)

                payload = {'choices': choices}

        elif qtype == 'text':
            payload = {}
            correct = str(acell or '').strip()

        elif qtype == 'table':
            # content — строки через ";"
            tokens = [tok.strip() for tok in content.split(';') if tok.strip()]
            print(tokens)
            if len(tokens) < 2 or not tokens[0].startswith('|'):
                row_errors[f"B{ri}"] = "После «ДАННЫЕ:» нужна таблица вида |col1|col2|;|r1c1|r1c2|;…"
            if not row_errors:
                header = tokens[0].strip('|').split('|')
                rows = [tok.strip('|').split('|') for tok in tokens[1:]]
                payload = {'columns': header, 'rows': rows}

                # правильная таблица — та же семантика, потом flatten для correct
                ans = str(acell or '').strip()
                if not ans:
                    row_errors[f"C{ri}"] = "В Ответе должна быть заполненная таблица"
                else:
                    # flatten: используем ";" как разделитель строк
                    answer_tokens = [tok.strip() for tok in ans.split(';') if tok.strip()]
                    if (len(answer_tokens) != len(tokens) or answer_tokens[0] != tokens[0]):
                        row_errors[f"C{ri}"] = "Структура таблицы в «Ответе» не совпадает"
                    correct = ";".join(answer_tokens)

        # если были ошибки — сохраним и перейдём к следующей строке
        if row_errors:
            errors.update(row_errors)
            continue

        # Если дошли сюда — строка валидна
        parsed.append({
            'type':  qtype,
            'text':   question_text,
            'payload': payload,
            'correct_answer': correct,
        })

    return parsed, errors

def save_parsed_questions(parsed):
    """
    Принимает список dict-ов вида {
      'type': qtype,
      'text': question_text,
      'payload': {...},
      'correct_answer': correct_str,
    }
    Возвращает (created_ids, existing_ids, all_questions_data).
    """
    created_ids = []
    existing_ids = []
    all_q = []

    for item in parsed:
        obj, created = Question.objects.get_or_create(
            text=item['text'],
            type=item['type'],
            payload=item['payload'],
            correct_answer=item['correct_answer'],
        )
        if created:
            created_ids.append(obj.id)
        else:
            existing_ids.append(obj.id)

        # собираем полную информацию, включая id
        all_q.append({
            'id': obj.id,
            'type': obj.type,
            'text': obj.text,
            'payload': obj.payload,
            'correct_answer': obj.correct_answer,
        })

    return created_ids, existing_ids, all_q

def validate_excel(df, importer):
    """
    1) Читает DataFrame из Excel.
    2) Проверяет все ячейки и накапливает ошибки { 'A2': msg, 'C5': msg, ... }.
    3) НЕ сохраняет и НЕ шлёт письма.
    Возвращает (rows, errors). Если errors не пуст — rows будет [].
    """
    required = ['Фамилия','Имя','Отчество','Почта','Роль','Дата рождения']
    if df.columns.tolist() != required:
        return [], {None: f"Ожидаются столбцы: {required}"}

    allowed_roles = set(Role.objects.values_list('name', flat=True))
    rows, errors = [], {}

    for idx, row in df.iterrows():
        rn = idx + 2
        row_err = {}

        # ФИО
        for col in ('Фамилия','Имя','Отчество'):
            v = row[col]
            if not isinstance(v, str) or not RU_NAME_RE.match(v):
                cell = f"{chr(65 + df.columns.get_loc(col))}{rn}"
                row_err[cell] = f"{col}: только русские буквы"

        # Почта
        email = row['Почта']
        try:
            validate_email(email)
        except DjangoValidationError:
            cell = f"{chr(65 + df.columns.get_loc('Почта'))}{rn}"
            row_err[cell] = "Почта: неверный формат"

        # Дата рождения
        try:
            datetime.strptime(str(row['Дата рождения'])[:10], "%Y-%m-%d")
        except Exception:
            cell = f"{chr(65 + df.columns.get_loc('Дата рождения'))}{rn}"
            row_err[cell] = "Дата рождения: ожидается YYYY-MM-DD"

        # Роль и права
        role = row['Роль']
        if role not in allowed_roles:
            cell = f"{chr(65 + df.columns.get_loc('Роль'))}{rn}"
            row_err[cell] = f"Роль «{role}» неизвестна"
        elif role in ('Преподаватель','Администратор') and importer.role.name != 'Администратор':
            cell = f"{chr(65 + df.columns.get_loc('Роль'))}{rn}"
            row_err[cell] = "Нет прав на создание пользователя с этой ролью"

        if row_err:
            errors.update(row_err)
        else:
            rows.append({
                'last_name':      row['Фамилия'],
                'first_name':     row['Имя'],
                'second_name':    row['Отчество'],
                'email':          email,
                'role':           role,
                'date_of_birth':  str(row['Дата рождения'])[:10],
            })

    # Если были ошибки — не возвращаем ни одной строки
    if errors:
        return [], errors

    return rows, {}

def import_and_notify(rows):
    """
    rows — список словарей, как из validate_excel
    Возвращает два списка: created_ids, existing_ids.
    Рассылает письма пачкой через один SMTP-соединение.
    """
    connection = get_connection(fail_silently=True)
    messages   = []
    created_ids, existing_ids = [], []

    for data in rows:
        # создаём без рассылки
        user = create_user_account(data, do_send_mail=False)
        if hasattr(user, '_raw_password'):
            # новый пользователь
            created_ids.append(user.id)
            # готовим одно письмо
            messages.append(
                EmailMessage(
                    subject='Регистрация на сайте EduCert',
                    body=f'Вы успешно зарегистрированы. Ваш пароль: {user._raw_password}',
                    from_email='noreply@educert.local',
                    to=[user.email],
                )
            )
        else:
            existing_ids.append(user.id)

    # шлём все вместе
    connection.send_messages(messages)

    return created_ids, existing_ids

def create_user_account(data: dict, do_send_mail: bool = True):
    """
    data = {
      'first_name','second_name','last_name',
      'email','role','date_of_birth'
    }
    1) Если email уже есть — возвращает (user, False).
    2) Иначе — создаёт, шлёт письмо и возвращает (user, True).
    При ошибках валидации/рассылки бросает DRF ValidationError.
    """
    # 1) Существующий пользователь
    existing = User.objects.filter(email=data['email']).first()
    if existing:
        return existing

    # 2) Генерим пароль, прикладываем к данным для сериализации
    password = get_random_string(12)
    data_for_ser = data.copy()
    data_for_ser['password'] = password

    serializer = UserSerializer(data=data_for_ser)
    try:
        serializer.is_valid(raise_exception=True)
    except DRFValidationError as e:
        # пробрасываем в формате DRF
        raise e

    # 3) Сохраняем и шлём почту в атомарной транзакции
    user = serializer.save()
    user.set_password(password)
    user._raw_password = password
    user.save()
    if do_send_mail:
        send_mail(
            subject='Регистрация на сайте EduCert',
            message=f'Вы успешно зарегистрированы. Ваш пароль: {password}',
            from_email='noreply@educert.local',
            recipient_list=[user.email]
        )

    return user

def get_module_details(module):
    """
    Возвращает словарь с данными по одному модулю:
    базовые поля, список файлов и список тестов.
    """
    files_qs = ModuleFile.objects.filter(module_id=module).select_related('file_id')
    tests_qs = ModuleTest.objects.filter(module_id=module).select_related('test_id')

    return {
        "module_id":   module.id,
        "module_name": module.name,
        "description": module.description,
        "files": [
            {
                "modulefile_id":    mf.id,
                "file_id":          mf.file.id,
                "file_name":        mf.file.file_name,
                "file_description": mf.file.description,
                "file_url":         mf.file.file.url,
            }
            for mf in files_qs
        ],
        "tests": [
            {
                "moduletest_id":    mt.id,
                "test_id":          mt.test.id,
                "test_name":        mt.test.name,
                "quesiton_count":   mt.test.test_question_count,
            }
            for mt in tests_qs
        ]
    }

def save_attempt_questions(attempt, questions_data, is_exam=False):
    """
    Сохраняет все ответы из questions_data и
    вычисляет процент правильных.
    questions_data = [
      {'id': <question_id>, 'user_answer': '...'},
      ...
    ]
    """
    correct_count = 0
    total = len(questions_data)

    for item in questions_data:
        q_obj = Question.objects.get(id=item['question_id'])
        ua = str(item['user_answer']).strip()
        ca = str(q_obj.correct_answer).strip()  # или q_obj.correct_answer
        is_correct = (ua == ca)
        if is_correct:
            correct_count += 1
        
        AttemptQuestion.objects.create(
            exam_attempt=attempt if is_exam else None,
            test_attempt=None if is_exam else attempt,
            question=q_obj,
            user_answer=item['user_answer'],
            is_correct=is_correct
        )

    percent = (correct_count / total * 100) if total else 0

    return percent

def update_user_course_progress(user_id, *, course_id=None, test_id=None):
    """
    Пересчитывает progress в UserCourse для одного или нескольких курсов:
      — если передан course_id, обновляем только его;
      — если передан test_id, находим все курсы, в которые этот
        юзер записан (UserCourse) и которые содержат этот тест,
        и обновляем их.
    """
    # 1) Собираем список course_ids для обновления
    if test_id is not None:
        # курсы, куда пользователь записан
        user_courses = UserCourse.objects.filter(
            user_id=user_id
        ).values_list('course_id', flat=True)
        # модули, в которых есть этот тест
        module_ids = ModuleTest.objects.filter(
            test_id=test_id
        ).values_list('module_id', flat=True)
        # курсы, где эти модули
        course_ids = CourseModule.objects.filter(
            course_id__in=user_courses,
            module_id__in=module_ids
        ).values_list('course_id', flat=True).distinct()
    elif course_id is not None:
        course_ids = [course_id]
    else:
        raise ValueError("Нужно передать либо course_id, либо test_id")

    # 2) Для каждого курса пересчитываем progress
    for cid in course_ids:
        # все модули → тесты
        mod_ids = CourseModule.objects.filter(
            course_id=cid
        ).values_list('module_id', flat=True)
        test_ids = ModuleTest.objects.filter(
            module_id__in=mod_ids
        ).values_list('test_id', flat=True).distinct()
        total_tests = test_ids.count()

        # сколько тестов пройдено (is_best & is_passed)
        passed_tests = UserTestAttempt.objects.filter(
            user_id=user_id,
            test_id__in=test_ids,
            is_best=True,
            is_passed=True
        ).count()

        # экзамен (любая попытка) считается «пройденным»
        exam_done = UserExamAttempt.objects.filter(
            user_id=user_id,
            course_id=cid
        ).exists()

        # считаем %
        has_exam = True if Course.objects.get(id=cid).exam_question_count else False
        total_items = total_tests + (1 if has_exam else 0)
        completed   = passed_tests + (1 if exam_done else 0)
        progress_pct = int((completed / total_items) * 100) if total_items else 0

        # сохраняем
        UserCourse.objects.filter(
            user_id=user_id,
            course_id=cid
        ).update(progress=progress_pct)

