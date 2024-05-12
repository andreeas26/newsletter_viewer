from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from gmail import GmailEmail
from data_types import EmailMessage

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
gmail = GmailEmail()



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/unread_emails/{id}", response_class=HTMLResponse)
async def unread_emails(request: Request, id: int):
    email_message = gmail.list_messages()

    email = email_message[id]
    context = {
        "id": id,
        "email": email
        }

    return templates.TemplateResponse(
        request=request, name="emails.html", context=context
    )
