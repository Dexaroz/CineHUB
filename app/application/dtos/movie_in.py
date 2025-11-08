from dataclasses import Field
from typing import Annotated

from pydantic import BaseModel, constr, conint


class MovieIn(BaseModel):
    title: constr(min_length=1, max_length=255)
    genre: constr(min_length=1, max_length=100)
    director: constr(min_length=1, max_length=255)
    year: conint(ge=1888, le=2100)
    rate: conint(ge=0, le=10)
    poster: constr(min_length=1)
    synopsis: constr(min_length=1, max_length=2000)
    duration: conint(ge=1, le=1000)