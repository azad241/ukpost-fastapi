




#no need to use [as this accept get requests only]





# from pydantic import BaseModel
# from typing import List, Optional
#
# class CityBase(BaseModel):
#     name: str
#     slug: str
#
# class CityCreate(CityBase):
#     pass
#
# class City(CityBase):
#     id: int
#     postcodes: List["Postcode"] = []
#
#     class Config:
#         orm_mode = True
#
# class PostcodeBase(BaseModel):
#     code: str
#     city_id: int
#
# class PostcodeCreate(PostcodeBase):
#     pass
#
# class Postcode(PostcodeBase):
#     id: int
#     city: Optional[City] = None
#
#     class Config:
#         orm_mode = True
