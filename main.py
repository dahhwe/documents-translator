import os

import uvicorn
from ezodf import opendoc
from fastapi import FastAPI, UploadFile, HTTPException, File, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from translation import translate_node, translate_docx_file

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_unique_filename(filename):
    counter = 1
    new_filename = filename
    name, extension = os.path.splitext(filename)

    while os.path.exists(new_filename):
        new_filename = f"{name}({counter}){extension}"
        counter += 1

    return new_filename


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.post("/upload/")
async def upload(file: UploadFile = File(...), prompt: str = Form(...)):
    filename, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension[1:].lower()
    if file_extension not in ['docx', 'odt', 'doc']:
        raise HTTPException(status_code=400, detail="Некорректное расширение документа."
                                                    "Только .docx, .odt, and .doc разрешены.")

    temp_filename = f"temp_{file.filename}"
    try:
        contents = await file.read()
        with open(temp_filename, 'wb') as f:
            f.write(contents)

        if file_extension == 'docx' or file_extension == 'doc':
            translate_docx_file(temp_filename, prompt)
        elif file_extension == 'odt':
            doc = opendoc(temp_filename)
            for element in doc.body:
                translate_node(element, prompt)
            doc.save()

        translated_dir = 'translated_files'
        if not os.path.exists(translated_dir):
            os.makedirs(translated_dir)

        new_filename = os.path.join(translated_dir, get_unique_filename(f"translated_{file.filename}"))
        os.rename(temp_filename, new_filename)
        return {"message": "Документ успешно переведен", "filename": os.path.basename(new_filename)}

    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = os.path.join('translated_files', get_unique_filename(filename))
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="Документ не найден")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
