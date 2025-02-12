from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException
import time
import g4f
import clipboard
from re import search as search_number_in_text, findall as find_adll_numbers, match as search_text_in_text, sub as replace_text_in_text
import sys, io
from colorama import init as colorama_init, Fore, Style
colorama_init()

def log_print(*text):
    print(Fore.RED, end="")
    for i in text:
        print(i, end="")
    print(Style.RESET_ALL)

driver = webdriver.Chrome()
def click_next_button():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "lesson__next-btn")))
    next_button = driver.find_element(By.CLASS_NAME, "lesson__next-btn")
    next_button.click()
def click_submit_button():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "submit-submission")))
    submit_button = driver.find_element(By.CLASS_NAME, "submit-submission")
    submit_button.click()
    time.sleep(10)
    if driver.find_elements(By.CLASS_NAME, "submit-submission"):
        driver.find_element(By.CLASS_NAME, "submit-submission").click()
    get_current_guiz_state()

def askGPT(content, question):
    print("TO GPT: ", content, question)
    response = g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=[{"role": "user", "content": f"{content} {question}"}])
    print("FROM GPT: ", response)
    return response



def GPTtexarea(question):
    response = askGPT("Нужен только код, ничего больше в ответе быть не должно: ", question)
    return response

def GPTnumberinput(question):
    response = askGPT("Требуется числовой ответ на вопрос, только ответ, одной строчкой, никакие пояснения не нужны: ", question)
    response = find_adll_numbers(r'\d+', response)
    return response

def GPTchoiceRadioButton(question):
    response = askGPT("Напиши номер верного ответа выделив его фигурными скобками. Не нужно писать сам ответ\n", question)
    response = search_number_in_text(r'\{(\d+)\}', response)
    if response:
        return response.group(1)
    else:
        log_print("Error:", response)
        return False

def GPTchoiceCheckbox(question) -> str:
    prompt = """
    В задаче ниже предоставлены несколько варинтов ответа, выбери только правельные. 
    Не нужно писать сам вопрос, нужны только ответы, без комментриваев, лишних символов.
    Если правельных ответов несколько, каждый должен быть с новой строки.
    Очень важно, чтобы номера выбранных элементов были заключены в фигурные скобки.
    """
    response = askGPT(prompt, question)
    response = find_adll_numbers(r"\{([^}]+)\}", response)
    return response

def GPTsorting_process(question):
    response = askGPT("Нужно отсортировать список в правельном порядке. Ничего другого кроме отсортированного списка в ответе быть не должно. Каждый элемент списка с новой строки\n", question)
    response.replace('```', '')
    response = response.split('\n')
    response = list(filter(lambda x: x != '', response))
    response = list(filter(lambda x: x != '```', response))
    return response


def GPTmatching_process(question, lv = None):
    prompt = """
    Нужно отсортировать список справа так, чтобы он соответсвовал списку слева.
    Отет должен содержать список без лишних символов, каждый элемент с новой строки.
    Ответ должен быть без комментариев, только список.
    Речь идёт в контексте python разработки.
    """
    response = askGPT(prompt, question)
    response = response.split('\n')
    response = list(filter(lambda x: x != '```' and x != '', response))
    result = {}
    try:
        for pair in response:
            key, value = pair.split(':')
            result[key.strip()] = value.strip()
    except:
        result = dict(zip(lv, response))
    return result

def GPTfilling_process(question):
    prompt = """
    Твоя задача - заполнить пропуски, но при этом не выписывая сами вопросы.
    Ответ должен включать только заполнители, без комментариев, это необходимо для правельной работы программы.
    Ответ должен быть без лишних символов, каждый элемент с новой строки.
    Помни, что речь идёт о языке программирования Python с его операторами.
    Все ответы должны быть окружены фигурными скобками.
    """
    response = askGPT(prompt, question)
    response = response.split('\n')
    response = list(filter(lambda x: x != '```' and x != '', response))
    return response

def GPTtable_process(question):
    prompt = "Для программы необходимо, чтобы ты отвечала чётко либо True, либо False, ничего более, ни единого слова. Контекст: Python\n"
    response = askGPT(prompt, question)
    return "true" in response.lower()
    

def run_code(code, input_text = None):
    output = io.StringIO()
    sys.stdout = output
    if input_text:
        sys.stdin = io.StringIO(input_text)
    exec(code)
    sys.stdout = sys.__stdout__
    sys.stdin = sys.__stdin__
    script_output = output.getvalue()
    return script_output

def get_current_guiz_state():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-component")))
    qs = driver.find_element(By.CLASS_NAME, "quiz-component").get_attribute("data-state")
    log_print("Current quiz state:", qs)
    return qs


def login(email, password):
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "light-tabs__switch")))
    driver.find_element(By.NAME, "login").send_keys(email)  
    driver.find_element(By.NAME, "password").send_keys(password)
    time.sleep(5)
    driver.find_element(By.CLASS_NAME, "sign-form__btn").click()

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

# Функция перемещения элемента вверх/вниз
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

def quiz_wrong():
    get_current_guiz_state()
    again_button = driver.find_element(By.CLASS_NAME, "again-btn")
    again_button.click()
    time.sleep(1)
    try:
        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
        modal_popup.find_element(By.TAG_NAME, "button").click()
        time.sleep(1)
    except Exception as e:
        log_print(e)

def getCodeMirror():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "CodeMirror")))
    return driver.find_element(By.CLASS_NAME, "CodeMirror")
        

def quiz_correct():
    click_next_button()
    time.sleep(1) 

def choice_quiz():
    type_name = driver.find_element(By.CLASS_NAME, "quiz__typename").text
    wrong_list = ""
    for _ in range(10):
        quiz_state = get_current_guiz_state()
        if type_name == "Выберите все подходящие ответы из списка":
            options = driver.find_elements(By.CSS_SELECTOR, '.quiz-component .s-checkbox__label')
            checkboxes = driver.find_elements(By.CSS_SELECTOR, '.quiz-component .s-checkbox__input')
            numbered_options = [f"{i+1}. {option.text}" for i, option in enumerate(options)]
            result_text = "\n".join(numbered_options)
            if quiz_state == "wrong": quiz_wrong()
            response_numbers = GPTchoiceCheckbox(f"{quiz_question.text} Вариванты: {result_text} Не правильные ответы: {wrong_list}")
            if len(checkboxes) >= len(response_numbers):
                for index, checkbox in enumerate(checkboxes):
                    for response_number in response_numbers:
                        if index == int(response_number)-1:
                            driver.execute_script("arguments[0].click();", checkbox)
            log_print("Submit choices:", response_numbers)
            click_submit_button()
            time.sleep(6)
            quiz_state = get_current_guiz_state()
            wrong_list += str(int(response_number)) + " "
            if quiz_state == "correct":
                click_next_button()
                break
                            
                        
        else:
            options = driver.find_elements(By.CSS_SELECTOR, '.quiz-component .s-radio__label')
            numbered_options = [f"{i+1}. {option.text}" for i, option in enumerate(options)]
            result_text = "\n".join(numbered_options)
            if quiz_state == "wrong":
                wrong_message = driver.find_element(By.CLASS_NAME, "attempt-message_wrong")
                response_number = GPTchoiceRadioButton(f"{wrong_message.text} {quiz_question.text}Варианты:\n{result_text}\nНе правильные ответы:\n{wrong_list}")
                again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                again_button.click()
                time.sleep(1)
            else:
                response_number = response_number = GPTchoiceRadioButton(f"{quiz_question.text} {result_text}")
            checkboxes = driver.find_elements(By.CSS_SELECTOR, '.quiz-component .s-radio__input')
            if len(checkboxes) >= int(response_number):
                driver.execute_script("arguments[0].click();", checkboxes[int(response_number) - 1])
                
                click_submit_button()
            time.sleep(3)
            quiz_state = get_current_guiz_state()
            wrong_list += str(int(response_number)) + " "
            if quiz_state == "correct":
                click_next_button()
                break
            elif quiz_state == "wrong":
                continue

try:
    driver.get("https://stepik.org/lesson/290248/step/1?auth=login&unit=271724")
    #Пользователь должен зарегестрироваться под своей учетной записью
    login("whoyou1994j4920@gmail.com", "7ySeVAhh5nj8Xa5")
    input("Press Enter to continue...")
    
    # Находим строку поиска и вводим запрос
    while True:
        try:
            quiz_question = driver.find_elements(By.CSS_SELECTOR, ".quiz-layout-head")
            if not quiz_question:
                click_next_button()
                log_print("Skip this question, because no quiz question found")
                continue
            quiz_question = quiz_question[0]
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quiz-component")))
            quiz_type = driver.find_elements(By.CLASS_NAME, "quiz-component")
            if not quiz_type:
                click_next_button()
                "Skip this question, because no quiz type found"
                continue
            quiz_type = quiz_type[0].get_attribute("data-type")
            quiz_state = get_current_guiz_state()
            if quiz_state == "correct":
                click_next_button()
                continue
            elif quiz_state == "wrong":
                quiz_wrong()
            elif quiz_state == "no_submission":
                pass
            else: 
                time.sleep(5)
                log_print("skip this question, because state is:", quiz_state)
                continue
            
            log_print("Quiz Type:", quiz_type)
            if quiz_type == "choice-quiz":
                choice_quiz()
            elif quiz_type == "string-quiz":
                for _ in range(10):
                    input_field = driver.find_element(By.CLASS_NAME, "string-quiz__textarea")
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "wrong":
                        quiz_wrong()
                    if "Что покажет приведённый ниже код?" in quiz_question.text:
                        response = run_code(quiz_question.find_element(By.TAG_NAME, "code").text)
                    else:
                        response = GPTtexarea(quiz_question.text)
                    if '`' in response:
                        response = response.replace("`", "")
                        response = response.replace("python", "")
                    input_field.send_keys(response)
                    
                    click_submit_button()
                    time.sleep(3)
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
            elif quiz_type == "number-quiz":
                for _ in range(10):
                    input_field = driver.find_element(By.CLASS_NAME, "number-quiz__input")
                    qp = quiz_question.find_elements(By.TAG_NAME, "p")
                    qp = [q.text for q in qp]
                    if "Что покажет приведённый ниже код?" in qp:
                        if "если на вход программе будет подано следующее число:" in qp:
                            print("TO PYTHON:", quiz_question.find_element(By.TAG_NAME, "code").text)
                            response = run_code(quiz_question.find_element(By.TAG_NAME, "code").text, quiz_question.find_elements(By.TAG_NAME, "code")[1].text)
                            print("FROM PYTHON:", response)
                        print("TO PYTHON:", quiz_question.find_element(By.TAG_NAME, "code").text)
                        response = run_code(quiz_question.find_element(By.TAG_NAME, "code").text)
                        print("FROM PYTHON:", response)
                    else:
                        response = GPTnumberinput(quiz_question.text)
                    input_field.send_keys(response)
                    
                    click_submit_button()
                    time.sleep(3)
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
                    elif quiz_state == "no_submission":
                        time.sleep(3)
                        continue
                    else:
                        again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                        again_button.click()
                        time.sleep(1)
                        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
                        modal_popup.find_element(By.TAG_NAME, "button").click()
                        time.sleep(1)
            elif quiz_type == "code-quiz":
                smart_hints = ""
                for lifes in range(3):
                    quiz_state = get_current_guiz_state()
                    log_print("lifes left: ", 3 - lifes)
                    if quiz_state == "wrong":
                        smart_hints = driver.find_element(By.CLASS_NAME, "smart-hints__hint").text
                        quiz_wrong()
                    elif quiz_state == "no_submission":
                        response = GPTtexarea(f"{smart_hints}\n{quiz_question.text}")
                        if '`' in response:
                            if response.startswith("```python"):
                                response = response[len("```python"):]
                            response = response.replace("`", "")
                        if response == "":
                            log_print("response is empty")
                        driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", getCodeMirror(), response)
                        if quiz_state == "correct":
                            click_next_button()
                            break
                        
                        click_submit_button()
                        time.sleep(5)
                        quiz_state = get_current_guiz_state()
                        log_print("Anser:", quiz_state)
                        if quiz_state == "correct":
                            click_next_button()
                            break
                    elif quiz_state == "correct":
                        click_next_button()
                        break
                    elif quiz_state == "evaluation" or quiz_state == "pending":
                        while quiz_state == "evaluation" or quiz_state == "no_submission" or quiz_state == "pending":
                            time.sleep(5)
                            quiz_state = get_current_guiz_state()
                        if quiz_state == "correct":
                            click_next_button()
                            break
                        elif quiz_state == "wrong":
                            break
                    else:
                        log_print("Unknown quiz state:", quiz_state)
                        break
            elif quiz_type == "sorting-quiz":
                for _ in range(10):
                    items = driver.find_elements(By.CSS_SELECTOR, ".sorting-quiz__item .dnd-quiz__item-content")
                    items = [i.text for i in items]
                    items = [i + "\n" for i in items]
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
                    elif quiz_state == "wrong":
                        again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                        again_button.click()
                        time.sleep(1)
                        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
                        modal_popup.find_element(By.TAG_NAME, "button").click()
                        time.sleep(1)
                    elif "no_submission":
                        response = GPTsorting_process(f"{quiz_question.text}\n{"\n".join(items)}")
                        if response == []:
                            log_print("response is empty")
                            continue
                        for correct_index, correct_item in enumerate(response):
                            move_element_sorted(correct_item, correct_index)
                        
                        click_submit_button()
                        time.sleep(3)
                    else:
                        log_print("Sleep:", quiz_state)
                        time.sleep(5)
                        continue
            elif quiz_type == "matching-quiz":
                for _ in range(10):
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
                    if quiz_state == "wrong":
                        again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                        again_button.click()
                        time.sleep(1)
                        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
                        modal_popup.find_element(By.TAG_NAME, "button").click()
                        time.sleep(1)
                        response = GPTmatching_process(f"Неправильно, отсортируй в соотетствий с левым списком:\n{quiz_question.text}\n{items}", left_values)
                    else:   
                        response = GPTmatching_process(f"{quiz_question.text}\n{items}", left_values)
                    print("FROM GPT:", response)
                    if response == []:
                        log_print("response is empty")
                        continue
                    # Заполняем словарь
                    sorted_right_values = [response[expr] for expr in left_values]
                    for correct_index, item_text in enumerate(sorted_right_values):
                        move_element_matching(item_text, correct_index)
                    
                    click_submit_button()
                    time.sleep(3)
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
            elif quiz_type == "fill-blanks-quiz":
                for _ in range(10):
                    if quiz_state == "wrong":
                        again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                        again_button.click()
                        time.sleep(1)
                        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
                        modal_popup.find_element(By.TAG_NAME, "button").click()
                        time.sleep(1)
                    expressions = driver.find_elements(By.CLASS_NAME, "fill-blanks-quiz__text")
                    # Обрабатываем выражения
                    problems = []
                    for expr in expressions:
                        text = expr.text.strip()
                        if text:
                            result = GPTfilling_process(text)
                            problems.append(result[0])
                    inputs = driver.find_elements(By.CLASS_NAME, "fill-blanks-quiz__input")
                    for input_box, answer in zip(inputs, problems):
                        input_box.send_keys(answer)
                        time.sleep(0.5)  
                    
                    click_submit_button()
                    time.sleep(3)
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
            elif quiz_type == "table-quiz":
                for _ in range(10):
                    if quiz_state == "wrong":
                        again_button = driver.find_element(By.CLASS_NAME, "again-btn")
                        again_button.click()
                        time.sleep(1)
                        modal_popup = driver.find_element(By.CLASS_NAME, "modal-popup__footer")
                        modal_popup.find_element(By.TAG_NAME, "button").click()
                        time.sleep(1)
                    questions = driver.find_elements(By.CSS_SELECTOR, '.table-quiz__table tbody td[data-katex]')
                    answers = []
                    for question in questions:
                        response = GPTtable_process(f"{quiz_question.text} {question.text}")
                        answers.append(response)
                    rows = driver.find_elements(By.CSS_SELECTOR, ".table-quiz__table tbody tr")
                    for i, row in enumerate(rows):
                        if i >= len(answers):
                            break          
                        radios = row.find_elements(By.CSS_SELECTOR, "input.s-radio__input")
                        driver.execute_script("arguments[0].click();", radios[0 if answers[i] else 1])

                    
                    click_submit_button()
                    time.sleep(3)
                    quiz_state = get_current_guiz_state()
                    if quiz_state == "correct":
                        click_next_button()
                        break
            else:
                log_print("Unknown quiz type:", quiz_type)
                               
                
            
        except TimeoutException as e:  
            click_next_button()
            log_print("Clicked next button:", e)
        except InvalidSessionIdException as e:
            log_print("InvalidSessionIdException:", e)
            # Открываем Google
            driver = webdriver.Chrome()
            driver.refresh()
            driver.get("https://stepik.org/lesson/265083/step/5?auth=login&unit=246031")
            input("Press Enter to continue...")
            continue
    
finally:
    # Закрываем браузер
    log_print("Program finished")
