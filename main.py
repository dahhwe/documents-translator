import os

import uvicorn
from ezodf import opendoc
from fastapi import FastAPI, UploadFile, HTTPException, File, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from translation import translate_node, translate_docx_file

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, 'wb') as f:
            f.write(contents)

        if file.filename.endswith('.docx'):
            translate_docx_file(temp_filename)
        elif file.filename.endswith('.odt'):
            doc = opendoc(temp_filename)
            for element in doc.body:
                translate_node(element)

            doc.save()

        translated_dir = 'translated_files'
        if not os.path.exists(translated_dir):
            os.makedirs(translated_dir)

        new_filename = os.path.join(translated_dir, f"translated_{file.filename}")
        os.rename(temp_filename, new_filename)

        return {"message": "File translated successfully", "filename": f"translated_{file.filename}"}
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = os.path.join('translated_files', filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
