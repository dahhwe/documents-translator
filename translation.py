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


def translate_text(text, target_language='Turkish', custom_prompt=None):
    if text in string.punctuation:
        return text

    openai.api_key = "API_KEY"
    system_message = custom_prompt if custom_prompt \
        else f'You are a highly skilled translator specializing in IT literature.' \
             f' Your task is to translate the following text to {target_language},' \
             f' maintaining its professional tone and keeping all technical terms' \
             f' and object names intact. Your response should only contain the translated text without ' \
             f' any extra information such as specifying the language of the document and so on.' \
             f' If you are unable to provide the translation or text contains some kind of' \
             f' not alphabetic symbols or text seems to be a code fragment keep text as it is.'
    user_message = f'{custom_prompt} text: {text}' if custom_prompt \
        else f'Translate the text into {target_language}:\n{text}'
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


def translate_node(node, custom_prompt=None):
    if isinstance(node, ezodf.text.Paragraph) or isinstance(node, ezodf.text.Heading):
        inner_text = node.plaintext()
        if inner_text:
            print(BLUE_TEXT.format(f'\n***\nNode: {node}'))
            print(GREEN_TEXT.format('SOURCE_TEXT:'), inner_text)

            translated_text = translate_text(inner_text, custom_prompt=custom_prompt)
            print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
            clear_node_content(node)
            node.text = translated_text
    elif isinstance(node, ezodf.table.Table):
        for row in node.rows():
            if isinstance(row, list):
                cells = row
            else:
                cells = row.cells()
            for cell in cells:
                if isinstance(cell, ezodf.text.Paragraph) or isinstance(cell, ezodf.text.Heading):
                    translate_node(cell, custom_prompt)


def translate_run(run, custom_prompt=None):
    if run.text.strip():
        print(BLUE_TEXT.format(f'\n***\nRun: {run}'))
        print(GREEN_TEXT.format('SOURCE_TEXT:'), run.text)

        translated_text = translate_text(run.text, custom_prompt=custom_prompt)
        print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
        run.text = translated_text


def translate_docx_file(docx_file, custom_prompt=None):
    doc = Document(docx_file)
    for i, paragraph in enumerate(doc.paragraphs):
        for run in paragraph.runs:
            translate_run(run, custom_prompt)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        translate_run(run, custom_prompt)

    doc.save(docx_file)
