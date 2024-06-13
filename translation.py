import string

import ezodf
import openai
from docx import Document

BLUE_TEXT = '\033[34m{}\033[0m'
GREEN_TEXT = '\033[32m{}\033[0m'
RED_TEXT = '\033[31m{}\033[0m'
YELLOW_TEXT = '\033[33m{}\033[0m'


def clear_node_content(node):
    for child in node:
        clear_node_content(child)
    node.text = ''
    node.tail = ''


def translate_text(text, prompt):
    if not text.strip() or text in string.punctuation:
        return text

    openai.api_key = "API_KEY"
    system_message = prompt
    user_message = f'{prompt} text: {text}'
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        temperature=0,
        messages=[
            {'role': 'system',
             'content': system_message},
            {'role': 'user',
             'content': user_message}
        ]
    )
    return response.choices[0].message.content


def translate_node(node, prompt):
    if (isinstance(node, ezodf.text.Paragraph) or
            isinstance(node, ezodf.text.Heading)):
        inner_text = node.plaintext()
        if inner_text:
            print(BLUE_TEXT.format(f'\n***\nNode: {node}'))
            print(GREEN_TEXT.format('SOURCE_TEXT:'), inner_text)

            translated_text = translate_text(inner_text, prompt)
            print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
            clear_node_content(node)
            node.text = translated_text
    elif isinstance(node, ezodf.table.Table):
        for row in node:
            for cell in row:
                for element in cell:
                    translate_node(element, prompt)


def translate_run(run, prompt):
    if run.text.strip():
        print(BLUE_TEXT.format(f'\n***\nRun: {run}'))
        print(GREEN_TEXT.format('SOURCE_TEXT:'), run.text)

        translated_text = translate_text(run.text, prompt)
        print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
        run.text = translated_text


def translate_docx_file(docx_file, prompt):
    doc = Document(docx_file)
    for i, paragraph in enumerate(doc.paragraphs):
        for run in paragraph.runs:
            translate_run(run, prompt)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        translate_run(run, prompt)

    doc.save(docx_file)
