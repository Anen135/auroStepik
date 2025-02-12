from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException
import time
import GPTprocess as gpt
import clipboard
import re
import sys, io
from colorama import init as colorama_init, Fore, Style
TARGET_URL = "https://stepik.org/lesson/290248/step/1?auth=login&unit=271724"
EMAIL = "whoyou1994j4920@gmail.com"
PASSWORD = "7ySeVAhh5nj8Xa5"

colorama_init()
driver = webdriver.Chrome()

def log_print(*text):
    print(Fore.RED, end="")
    for i in text:
        print(i, end="")
    print(Style.RESET_ALL)

def log_timesleep(seconds, comment=""):
    log_print("Sleep for ", seconds, " seconds ", comment)
    time.sleep(seconds)

def is_quiz():
    q = driver.find_elements(By.CSS_SELECTOR, ".quiz-layout-head")
    if q:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-layout-head"))) 
        return True
    else: return False

def click_next_button():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "lesson__next-btn")))
    next_button = driver.find_element(By.CLASS_NAME, "lesson__next-btn")
    time.sleep(1)
    next_button.click()

def click_submit_button():
    log_timesleep(1, "Before submit")
    log_print("Submit")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "submit-submission")))
    submit_button = driver.find_element(By.CLASS_NAME, "submit-submission")
    submit_button.click()
    return get_current_guiz_state()

def get_quiz_question():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-layout-head")))
    return driver.find_element(By.CSS_SELECTOR, ".quiz-layout-head")
    
def get_current_guiz_state():
    if not is_quiz(): return "no_quiz"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-component")))
    qs = driver.find_element(By.CLASS_NAME, "quiz-component").get_attribute("data-state")
    return qs

def get_current_guiz_type():
    if not is_quiz(): return "no_quiz"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-component")))
    qt = driver.find_element(By.CLASS_NAME, "quiz-component").get_attribute("data-type")
    return qt


def click_auth_button():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "navbar__auth_login")))
    driver.find_element(By.CLASS_NAME, "navbar__auth_login").click()

def login(email, password):
    log_print("Login to stepik.org")
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.CLASS_NAME, "light-tabs__switch")))
    driver.find_element(By.NAME, "login").send_keys(email)  
    driver.find_element(By.NAME, "password").send_keys(password)
    log_timesleep(5)
    driver.find_element(By.CLASS_NAME, "sign-form__btn").click()

def click_again_button():
    log_print("Click again button")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "again-btn")))
    driver.find_element(By.CLASS_NAME, "again-btn").click()
    quiz_state = get_current_guiz_state()
    log_timesleep(1, "After click again button")
    if get_current_guiz_state() != "wrong": return
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modal-popup__footer")))
    driver.find_element(By.CLASS_NAME, "modal-popup__footer").find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

def move_element_sorted(item_text, target_position):
    quiz_items = driver.find_elements(By.CLASS_NAME, "sorting-quiz__item")
    
    for index, item in enumerate(quiz_items):
        text = item.find_element(By.CLASS_NAME, "html-content").text
        if text == item_text:
            while index > target_position:
                # Нажимаем "Вверх"
                up_button = item.find_element(By.CLASS_NAME, "sorting-quiz__arrow-up")
                up_button.click()
                index -= 1
                time.sleep(0.5)  
            while index < target_position:
                # Нажимаем "Вниз"
                down_button = item.find_element(By.CLASS_NAME, "sorting-quiz__arrow-down")
                down_button.click()
                index += 1
                time.sleep(0.5)

def move_element_matching(item_text, target_position):
    quiz_items = driver.find_elements(By.CLASS_NAME, "matching-quiz__right .matching-quiz__item")
    
    for index, item in enumerate(quiz_items):
        text = item.text.strip()
        if text == item_text:
            while index > target_position:
                up_button = item.find_element(By.CLASS_NAME, "up-arrow_icon")
                up_button.click()
                index -= 1
                time.sleep(0.5)
            while index < target_position:
                down_button = item.find_element(By.CLASS_NAME, "down-arrow_icon")
                down_button.click()
                index += 1
                time.sleep(0.5)

def run_code_script(code, input_text=None):
    output = io.StringIO()
    sys.stdout = output
    if input_text:
        sys.stdin = io.StringIO(input_text)
    exec(code)
    sys.stdout = sys.__stdout__
    sys.stdin = sys.__stdin__
    script_output = output.getvalue()
    return script_output

def next_to_lesson(number):
    lessons = driver.find_elements(By.CLASS_NAME, "lesson-sidebar__lesson-name")
    for lesson in lessons:
        if number in lesson.text:
            lesson.click()
            return
    log_print("Lesson not found")

def next_to_quiz():
    while not is_quiz() or get_current_guiz_state() == "correct":
        click_next_button()
        if driver.find_elements(By.CLASS_NAME, "lesson-end-modal__footer"):
            log_print("Lesson is over")
            break

def getCodeMirror():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "CodeMirror")))
    return driver.find_element(By.CLASS_NAME, "CodeMirror")

def have_error():
    e = driver.find_elements(By.CLASS_NAME, "smart-hints__hint")
    if e: return True
    return False



def process_decorator(func):
    def wrapper(*args, **kwargs):
        if not is_quiz():
            log_print("Its not quiz")
            return "No quiz"
        quiz_state = get_current_guiz_state()
        log_print("Current quiz state:", quiz_state)
        if quiz_state == "correct":
            return "Correct"
        elif quiz_state == "evaluation":
            log_print("Already submitted")
            return "Already submitted"
        elif quiz_state == "pending":
            log_print("Pending")
            return "Pending"
        if get_current_guiz_state() == "no_submission":
            log_print("Starting:", func.__name__)
            return func(*args, **kwargs)
        else:
            log_print("Unknown quiz state")
            return "Unknown quiz state"
    return wrapper

@process_decorator
def sorting_Quiz(quiz):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sorting-quiz__item .dnd-quiz__item-content")))
    items = driver.find_elements(By.CSS_SELECTOR, ".sorting-quiz__item .dnd-quiz__item-content")
    items = [i.text for i in items]
    items = [i + "\n" for i in items]
    response = gpt.GPTsorting_process(f"{quiz.text}\n{items}")
    if not response:
        log_print("response is empty")
        return
    for correct_index, correct_item in enumerate(response):
        move_element_sorted(correct_item, correct_index)

def number_Quiz(quiz):
    response = gpt.GPTnumberic_process(quiz.text)
    if not response:
        log_print("response is empty")
        return
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "number-quiz__input")))
    driver.find_element(By.CLASS_NAME, "number-quiz__input").send_keys(response)

@process_decorator
def run_code(quiz):
    code = quiz.find_element(By.CSS_SELECTOR, "code.hljs").text
    output = run_code_script(code)
    textarea = driver.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(output)

@process_decorator
def write_code(quiz, hint=""):
    quiz_question = quiz.text
    response = gpt.GPTcodewrite_process(f"{hint}\n{quiz_question}\nCode:\n{driver.execute_script("return arguments[0].CodeMirror.getValue();", getCodeMirror())}")
    if not response:
        log_print("response is empty")
        return "response is empty"
    driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", getCodeMirror(), response)

@process_decorator
def fill_blanks(quiz):
    quiz_question = quiz.text
    expressions = driver.find_elements(By.CLASS_NAME, "fill-blanks-quiz__text")
    expressions = [expr.text.strip() for expr in expressions]
    expressions = "\n".join(expressions)
    problems = gpt.GPTfilling_process(f"{quiz_question}\n{expressions}")
    inputs = driver.find_elements(By.CLASS_NAME, "fill-blanks-quiz__input")
    for input_box, answer in zip(inputs, problems):
        input_box.send_keys(answer)
        time.sleep(0.5)

@process_decorator
def choice_Quiz(quiz, wrong_list = ""):
    options = driver.find_elements(By.CSS_SELECTOR, ".quiz-component .s-radio__label, .quiz-component .s-checkbox__label")
    numbered_options = [f"{i+1}. {option.text}" for i, option in enumerate(options)]
    result_text = "\n".join(numbered_options)
    response = gpt.GPTchoice_process(f"{quiz.text}\nВарианты:{result_text}\nНеправильные ответы:{wrong_list}")
    checkboxes = driver.find_elements(By.CSS_SELECTOR, '.quiz-component .s-radio__input, .quiz-component .s-checkbox__input')
    if len(checkboxes) >= len(response):
        for index, checkbox in enumerate(checkboxes):
            for response_number in response:
                if index == int(response_number)-1:
                    driver.execute_script("arguments[0].click();", checkbox)
    return "WI" + ", ".join(["{" + str(i) + "}" for i in response])

@process_decorator
def match_Quiz(quiz):
    # Получаем элементы из левой колонки (вопросы)
    left_items = driver.find_elements(By.CLASS_NAME, "matching-quiz__left .matching-quiz__item")
    left_values = [item.text.strip() for item in left_items]
    # Получаем элементы из правой колонки (ответы)
    right_items = driver.find_elements(By.CLASS_NAME, "matching-quiz__right .matching-quiz__item")
    right_values = [item.text.strip() for item in right_items]
    items = list(zip(left_values, right_values))
    _temp = ""
    for item in items:
        _temp += f"{item[0]} : {item[1]}\n"
    items = _temp
    for _ in range(10):
        response = gpt.GPTmatching_process(f"{quiz.text}\n{items}")
        if len(response) != len(left_values): continue
        break
    if type(response) == list:
        sorted_right_values = response
    elif type(response) == dict:
        sorted_right_values = [response[expr] for expr in left_values]
    if not response:
        log_print("response is empty")
        return "response is empty"
    for correct_index, correct_item in enumerate(sorted_right_values):
        move_element_matching(correct_item, correct_index)

@process_decorator
def string_Quiz(quiz):
    quiz_question = quiz.text
    responce = gpt.GPTstring_process(quiz_question)
    if not responce:
        log_print("response is empty")
        return "response is empty"
    textarea = driver.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(responce)

@process_decorator
def table_Quiz(quiz):    
    headers = driver.find_elements(By.CSS_SELECTOR, ".table-quiz__table thead th[data-katex] code")
    options = [header.text for header in headers]  
    rows = driver.find_elements(By.CSS_SELECTOR, ".table-quiz__table tbody tr")
    table_text = f"Варианты: {', '.join(options)}\n"
    questions = []
    for row in rows:
        question_text = row.find_element(By.CSS_SELECTOR, "td[data-katex]").text
        questions.append(f"{question_text}: {{}}")
    table_text += "\n".join(questions)    
    response = gpt.GPTtable_process(f"ВОПРОС: {quiz.text}\n{table_text}", options)
    if not response:
        log_print("response is empty")
        return "response is empty"
    numeric_answers = [options.index(answer) for answer in response]
    for i, row in enumerate(rows):
        if i >= len(numeric_answers):
            break  
        radios = row.find_elements(By.CSS_SELECTOR, "input.s-radio__input")
        driver.execute_script("arguments[0].click();", radios[numeric_answers[i]])



def code_rain():
    while True:
        try:
            if not is_quiz: break
            if get_current_guiz_state() == "correct": 
                click_next_button()
                continue
            if get_current_guiz_type() != "code-quiz": break
            if get_current_guiz_state() == "wrong": click_again_button()
            write_code(driver.find_element(By.CLASS_NAME, "quiz-layout-head"))
            click_submit_button()
            click_next_button()
        except Exception as e:
            log_print(e)
            break

def solve():
    quiz_type = get_current_guiz_type()
    
    log_print(f"Type:", quiz_type)
    wrong_list = ""
    for _ in range(3):
        hint = "" if not have_error() else driver.find_element(By.CLASS_NAME, "smart-hints__hint").text
        quiz_state = get_current_guiz_state()
        if quiz_state == "wrong": click_again_button()
        if quiz_state in ["correct", "no_quiz"]: return
        log_print("Current state:", get_current_guiz_state())
        if quiz_type == "sorting-quiz":
            res = sorting_Quiz(driver.find_element(By.CLASS_NAME, "quiz-layout-head"))
        elif quiz_type == "number-quiz":
            res = number_Quiz(driver.find_element(By.CLASS_NAME, "number-quiz"))
        elif quiz_type == "code-quiz":
            res = write_code(driver.find_element(By.CLASS_NAME, "quiz-layout-head"), hint)
        elif quiz_type == "fill-blanks-quiz":
            res = fill_blanks(driver.find_element(By.CLASS_NAME, "quiz-layout-head"))
        elif quiz_type == "choice-quiz":
            res = choice_Quiz(driver.find_element(By.CLASS_NAME, "quiz-layout-head"), wrong_list)
        elif quiz_type == "string-quiz":
            quiz = get_quiz_question()
            if "Что покажет приведённый ниже код?" in quiz.text: res = run_code(quiz)
            else: res = string_Quiz(quiz)
        elif quiz_type == "matching-quiz":
            res = match_Quiz(driver.find_element(By.CLASS_NAME, "quiz-layout-head"))
        elif quiz_type == "table-quiz":
            res = table_Quiz(driver.find_element(By.CLASS_NAME, "quiz-layout-head"))
        while get_current_guiz_state() == "pending":
            log_timesleep(5, "Pedding waiting")
        if get_current_guiz_state() == "correct": break
        if get_current_guiz_state() == "wrong": continue
        if res == "Already submitted": break
        if res and res.startswith("WI"):
            wrong_list = res[2:]
        click_submit_button()
        log_timesleep(1, "solve time stop")

def quiz_rain():
    log_print("Quiz rain starting")
    while True:
        try:
            if is_quiz(): solve()
            click_next_button()
        except Exception as e:
            log_print("Error:", e)
            break

def try_while(number):
    for _ in range(number):
        try:
            solve()
        except Exception as e:
            log_print(e)

        
        
        
        

driver.get(TARGET_URL)
flag_auto = False
login(EMAIL, PASSWORD)
input("Enter to continue: ")
while True:
    try:
        user_input = input("Enter the command: ")
        if user_input == "exit":
            break
        if user_input == "help":
                print("""Доступные команды:
                        - help: Вывести список всех команд.
                        - exit: Завершить программу.
                        - login: Авторизоваться в системе.
                        - next: Перейти к следующему шагу.
                        - next to lesson <номер>: Перейти к уроку с указанным номером.
                        - next to quiz: Перейти к следующему тесту.
                        - auto: Включить/выключить автоматический режим.
                        - code rain: Запустить режим 'Code Rain'.
                        - quiz rain: Запустить режим 'Quiz Rain'.
                        - submit: Отправить ответ на текущий тест.
                        - sorting: Решить тест типа 'Сортировка'.
                        - run code: Запустить код в текущем тесте.
                        - write code: Написать код в текущем тесте.
                        - fill blanks: Заполнить пропуски в текущем тесте.
                        - number: Решить тест с числовым ответом.
                        - choice: Решить тест с выбором ответа.
                        - table: Решить тест с таблицей.
                        - solve: Решить текущий тест.
                        - get status: Вывести текущий статус текущего теста.
                        - url stepik: Перейти на сайт stepik.org.
                        - try while <number>: Попытаться решить тест <number> раз. """)
        if user_input == "login":
            login(EMAIL, PASSWORD)
        elif user_input == "next":
            click_next_button()
        elif lesson_match := re.match(r"next to lesson (\d+(?:\.\d+)?)", user_input):
            number = lesson_match.group(1)
            next_to_lesson(number)
        elif user_input == "next to quiz":
            next_to_quiz()
        elif user_input == "auto":
            flag_auto = not flag_auto
            log_print("Auto mode:", flag_auto)
        elif user_input == "code rain":
            code_rain()
        elif user_input == "solve":
            solve()
        elif user_input == "get status":
            print("Current state:",get_current_guiz_state())
        elif user_input == "url stepik":
            driver.get(TARGET_URL)
        elif user_input == "quiz rain":
            quiz_rain()
        elif user_input == re.match(r"try while (\d+)", user_input):
            try_while(int(user_input[10:]))
                
                
        elif is_quiz():
            if get_current_guiz_state() == "wrong":
                click_again_button()   
            quiz = driver.find_element(By.CLASS_NAME, "quiz-layout-head") 
            quiz_type = get_current_guiz_type()
            if user_input == "submit":
                click_submit_button()
            elif user_input == "sorting":
                for i in range(3):
                    if quiz_type != "sorting-quiz": 
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    sorting_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
                else: log_print("Cant decide")
            elif user_input == "run code":
                for i in range(3):
                    if get_current_guiz_state() == "wrong": click_again_button()
                    run_code(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
                else: log_print("Cant decide")
                    
            elif user_input == "write code":
                for i in range(3):
                    if quiz_type != "code-quiz": 
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    write_code(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
                else: log_print("Cant decide")
            elif user_input == "fill blanks":
                for i in range(3):
                    if quiz_type != "fill-blanks-quiz": 
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    fill_blanks(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
                else: log_print("Cant decide")
            elif user_input == "number":
                for i in range(3):
                    if quiz_type != "number-quiz": 
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    number_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
                else: log_print("Cant decide")
            elif user_input == "choice":
                for i in range(3):
                    if quiz_type != "choice-quiz": 
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    choice_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "current": break
            elif user_input == "match":
                for i in range(3):
                    if quiz_type != "matching-quiz":
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    match_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
            elif user_input == "string":
                for i in range(3):
                    if quiz_type != "string-quiz":
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    string_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
            elif user_input == "table":
                for i in range(3):
                    if quiz_type != "table-quiz":
                        log_print("invalid type")
                        break
                    if get_current_guiz_state() == "wrong": click_again_button()
                    table_Quiz(quiz)
                    click_submit_button()
                    if not flag_auto or get_current_guiz_state() == "correct": break
            else: log_print("invalid command")
        else:
            print("Its not quiz")
    except InvalidSessionIdException as e:
        log_print(e)
        driver = webdriver.Chrome()
        continue        