#%%
from aocd import get_data, submit
import os
import openai
import requests
from bs4 import BeautifulSoup
import time


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AOC_SESSION = os.environ.get("AOC_SESSION")

openai.api_key = OPENAI_API_KEY


def get_task_html(year, day, part):
    # fetch the html body for a given year, day and part

    filename = f"{year}-{day}-{part}.html"

    body = None
    
    if os.path.isfile(filename):
        # use cached html
        with open(filename, "r") as f:
            body = f.read()
    else:
        # fetch html
        url = f"https://adventofcode.com/{year}/day/{day}"
        body = requests.get(url, headers={"cookie": f"session={AOC_SESSION}"}).text

        # ensure page contains desired part
        if part > 1:
            soup = BeautifulSoup(body, features="html.parser")
            part_found = soup.find(id=f"part{part}") is not None
            if not part_found:
                raise Exception(f"Part {part} not found!")

        # write body to file
        with open(filename, "w") as f:
            f.write(body)
    
    return body


def get_desc(year, day, part):
    # get a formatted description of the puzzle

    body = get_task_html(year, day, part)

    # replace code tags with markdown
    body = body.replace("<pre><code>", "```\n")
    body = body.replace("</code></pre>", "```\n")
    body = body.replace("<code>", "`")
    body = body.replace("</code>", "`")

    # extract task text from html for specified part
    soup = BeautifulSoup(body, features="html.parser")

    # find the correct <article> tag
    article = None
    if part == 1:
        article = soup.find("article", class_="day-desc")
    else:
        article = soup.find(id=f"part{part}").parent
    
    return article.text



def get_solution_code(year, day, part, temperature):
    # if we have a cached valid insert_code, load it
    filename = f"{year}-{day}-{part}.py"
    if os.path.isfile(filename):
        # load valid cached solution
        with open(filename, "r") as f:
            return f.read()

    # else, generate (hopefully) working code using openai api
    prompt = get_prompt(year, day, part, temperature)
    prefix, suffix = prompt.split("[insert]")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prefix,
        suffix=suffix,
        temperature=temperature,
        max_tokens=1024,
        top_p=1,
        best_of=20,
        frequency_penalty=0,
        presence_penalty=0
    )

    insert_code = response.choices[0].text
    return insert_code


def generate_solution(year, day, part, temperature):
    insert_code = get_solution_code(year, day, part, temperature)

    function_name = f"solution_{year}_{day}_{part}"

    full_function = f"""def {function_name}(input_list):
    {insert_code}
    return result"""

    return function_name, full_function, insert_code


def get_prompt(year, day, part, temperature):
    prompt = ""
    for i in range(1, part + 1):
        desc = get_desc(year, day, i)
        prompt += desc

        is_last = i == part

        insert_code = None
        if is_last:
            insert_code = "[insert]"
        else:
            insert_code = get_solution_code(year, day, i, temperature)

        prompt += f"""
Here is a python function which solves this puzzle: 
```

def solve(input_list: list[str]) -> int:
    {insert_code}

    return result

```

"""
        if i != part:
            prompt += """
This part of the puzzle is complete! It provides one gold star: *

"""

    return prompt



def solve(year, day, part):
    # main solve function, should work with any year, day and part
    print(f"Solving {year} day {day} part {part}...")
    tries_left = 5
    success = False

    while tries_left > 0 and not success:
        try:
            temp = 1 - tries_left / 5

            tries_left -= 1

            fn_name, code, insert_code = generate_solution(year, day, part, temp)

            # add function to scope
            exec(code, globals())

            # get puzzle data
            data = get_data(session=AOC_SESSION, year=year, day=day).splitlines()

            # run function
            answer = globals()[fn_name](data)
        
            print(f"answer: {answer}")
            submit_response = submit(answer, session=AOC_SESSION, year=year, day=day, part=str(part), reopen=False, quiet=True)
            if submit_response is not None and submit_response.status_code == 200 and "That's the right answer!" in submit_response.text:
                submit_response.text
                print("Answer was correct, caching solution")
                success = True
                # save code to cache
                with open(f"{year}-{day}-{part}.py", "w") as f:
                    f.write(insert_code)
            else:
                print("Answer was not correct")
        except Exception as e:
            print(e)
            time.sleep(10)


#%%
solve(2022, 1, 1)
