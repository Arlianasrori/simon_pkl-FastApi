from pydantic import BaseModel

def updateTable(data : BaseModel,models) :
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(models, field, value)