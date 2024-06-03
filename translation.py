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


def translate_text(text, target_language='Turkey'):
    openai.api_key = "API_KEY_HERE"
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        temperature=0,
        messages=[
            {'role': 'system',
             'content': f'To act as a technical translator for IT educational literature to {target_language}. No '
                        f'creativity! Just a strict translation.'},
            {'role': 'user',
             'content': f'Translate the text into {target_language} language:\n{text}'}
        ]
    )
    return response.choices[0].message.content


def translate_node(node):
    if isinstance(node, ezodf.text.Paragraph) or isinstance(node, ezodf.text.Heading):
        inner_text = node.plaintext()
        if inner_text:
            print(BLUE_TEXT.format(f'\n***\nNode: {node}'))
            print(GREEN_TEXT.format('SOURCE_TEXT:'), inner_text)

            translated_text = translate_text(inner_text)
            print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
            clear_node_content(node)
            node.text = translated_text


def translate_docx_file(docx_file):
    doc = Document(docx_file)
    for i, paragraph in enumerate(doc.paragraphs):
        for run in paragraph.runs:
            if run.text.strip():
                print(BLUE_TEXT.format(f'\n***\nRun: {run}'))
                print(GREEN_TEXT.format('SOURCE_TEXT:'), run.text)

                translated_text = translate_text(run.text)
                print(GREEN_TEXT.format('TRANSLATED_TEXT: '), translated_text)
                run.text = translated_text
    doc.save(docx_file)
