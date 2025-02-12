import g4f
import re

prompts = {
"sort": "\
Нужно отсортировать список в правельном порядке. \
Ничего другого кроме отсортированного списка в ответе быть не должно. \
Каждый элемент списка с новой строки\n",
"codewrite": "\
Нужен только код, ничего больше в ответе быть не должно:\n\
",
"filling": "\
Твоя задача - заполнить пропуски, но при этом не выписывая сами вопросы. \
Ответ должен включать только заполнители, без комментариев, это необходимо для правельной работы программы. \
Ответ должен быть без лишних символов кроме фигурных скобок. \
Все ответы должны быть окружены фигурными скобками. \
",
"number": "\
Требуется числовой ответ на вопрос, ответ должен быть окружен фигурными скобками. \
Фигурными скобками должен быть окружен ТОЛЬКО ответ, это необходимо для правельной работы программы.",
"choice": "\
Ниже приведена задача и варианты ответа на неё. \
Нужно в ответе указать верный вариант ответа, или верные варианты, если их несколько. \
Вне зависимости от количества верных ответов, в ответе должен быть окружен фигурными скобками. \
Не нужно возвращать верный ответ, нужно вернуть лишь его НОМЕР \
Фигурными скобками должены быть окружены ТОЛЬКО ответы, если их несколько, кждый в отдельных фигурных скобках. это необходимо для правельной работы программы.",
"matching": "\
Нужно отсортировать список справа так, чтобы он соответсвовал списку слева. \
Ответ должен содержать список без лишних символов, каждый элемент с новой строки. \
Ответ должен быть без комментариев, только список. \
Порядок левого списка нельзя менять, можно менять лишь порядок правого списка, чтобы он совпадал с првым.\
Речь идёт в контексте python разработки. Вопрос:\n",
"string": "\
Требуется только ответ без комментариев\n",
"table": "\
Снизу есть поля для заполнения: {}, просто заполни их предоставленными вариантами. \
Заполнять можно ТОЛЬКО предоставленными вариантымы, одинаковыми точь в точь. \
НЕЛЬЗЯ убирать фигурные скобки, пиши внутрь них. \
Ты можешь изменять только внутри фигурных скобок, нельзя менять внешние данные. \
Речь идёт в контексте python\n",
}

def parse_string_to_dict(input_string):
    pattern = r"\d+\.\s*\w+\s*:\s*\w+"
    matches = re.findall(pattern, input_string)
    result_dict = {key: value for key, value in matches}
    return result_dict

def askGPT(content, question):
    try:
        print("TO GPT: ", content, question)
        response = g4f.ChatCompletion.create(model=g4f.models.gpt_4o, messages=[{"role": "user", "content": f"{content} {question}"}])
        print("FROM GPT: ", response)
        return response
    except Exception as e:
        return "Error: " + str(e)

def GPTsorting_process(question):
    response = askGPT(prompts["sort"], question)
    response = response.replace('`', '')
    if '`' in response: print("Warning: ` in response")
    response = response.split('\n')
    response = list(filter(lambda x: x != '' and x != '```' and x.lower() not in ['```python'], response))
    return response

def GPTcodewrite_process(question):
    response = askGPT(prompts["codewrite"], question)
    response = response.replace('```python', '')
    response = response.replace('`', '')
    if '`' in response: print("Warning: ` in response")
    return response

def GPTfilling_process(question):
    response = askGPT(prompts['filling'], question)
    response = re.findall(r"\{([^}]+)\}", response)
    return response

def GPTnumberic_process(question):
    response = askGPT(prompts['number'], question)
    response = re.findall(r"\{([^}]+)\}", response)
    return response
def GPTchoice_process(question):
    response = askGPT(prompts['choice'], question)
    response = re.findall(r"\{([^}]+)\}", response)
    return response

def parse_string_to_dict(text):
    """Парсит строки формата 'ключ : значение' в словарь."""
    result = {}
    for line in text.strip().split("\n"):
        if ":" in line:
            key, value = map(str.strip, line.split(":", 1))
            result[key] = value
    return result

def parse_string_to_list(text):
    """Парсит строки без двоеточий в список значений."""
    return [line.strip() for line in text.strip().split("\n") if line.strip()]

def detect_format(text):
    lines = text.strip().split("\n")
    has_colon = any(":" in line for line in lines)  
    if has_colon: return "dict"
    return "list"

def GPTmatching_process(question): 
    response = askGPT(prompts['matching'], question)
    format_type = detect_format(response) 
    if format_type == "dict": return parse_string_to_dict(response)  
    elif format_type == "list": return parse_string_to_list(response)  
    else: return None  

def GPTstring_process(question):
    return askGPT(prompts['string'], question)

def GPTtable_process(question, options):
    while True:
        response = askGPT(prompts['table'], question)
        matches = re.findall(r"\{([^}]+)\}", response)
        response = [str(match) for match in matches]
        if any(option not in options for option in response): continue
        return response