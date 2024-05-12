from pydantic import BaseModel, ConfigDict, Field
from typing import Union


class EmailMessage(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: Union[str, None] = Field(None)
    sender: Union[str, None] = Field(None)
    subject: Union[str, None] = Field(None)
    message: Union[str, None] = Field(None)
    date: Union[str, None] = Field(None)

    def __str__(self) -> str:
        msg = self.message[:200] if self.message else ""
        res = """
        EmailMessage:
            Id: {}
            Date: {}
            From: {}
            Subject: {}
            Message: {}
        """.format(self.id, self.sender, self.date, self.subject, msg)
        return res
