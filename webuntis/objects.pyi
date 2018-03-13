import datetime
from typing import List, Tuple

from webuntis import Session


class Result(object):

    def __init__(self, data, parent: Result = None, session: Session = None):
        ...

    @property
    def id(self) -> int:
        ...

    def __int__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __eq__(self, other) -> bool:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...


class ListItem(Result):
    ...


class ListResult(Result):
    def filter(self, **criterions):
        ...

    def __contains__(self, criterion) -> bool:
        ...

    def __getitem__(self, i: int) -> ListItem:
        ...

    def __len__(self) -> int:
        ...


class ColorInfo(Result):

    @property
    def backcolor(self) -> str:
        ...

    @property
    def forecolor(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class DepartmentList(ListResult):

    def filter(self, **criterions) -> DepartmentList:
        ...

    def __getitem__(self, i: int) -> DepartmentObject:
        ...


class DepartmentObject(ListItem):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class HolidayList(ListResult):

    def filter(self, **criterions) -> HolidayList:
        ...

    def __getitem__(self, i: int) -> HolidayObject:
        ...


class HolidayObject(ListItem):

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def short_name(self) -> str:
        ...

    @property
    def start(self) -> datetime.datetime:
        ...


class KlassenList(ListResult):

    def filter(self, **criterions) -> KlassenList:
        ...

    def __getitem__(self, i: int) -> KlassenObject:
        ...


class KlassenObject(ListItem):
    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class PeriodList(ListResult):

    def filter(self, **criterions) -> PeriodList:
        ...

    def __getitem__(self, i: int) -> PeriodObject:
        ...

    def to_table(self) -> List[Tuple[datetime.time, List[Tuple[datetime.date, PeriodList]]]]:
        ...


class PeriodObject(ListItem):

    @property
    def code(self) -> str:
        ...

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def klassen(self) -> KlassenList:
        ...

    @property
    def original_rooms(self) -> RoomList:
        ...

    @property
    def original_teachers(self) -> TeacherList:
        ...

    @property
    def rooms(self) -> RoomList:
        ...

    @property
    def start(self) -> datetime.datetime:
        ...

    @property
    def subjects(self) -> SubjectList:
        ...

    @property
    def teachers(self) -> TeacherList:
        ...

    @property
    def type(self) -> str:
        ...


class PersonObject(ListItem):

    @property
    def fore_name(self) -> str:
        ...

    @property
    def full_name(self) -> str:
        ...

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def surname(self) -> str:
        ...


class RoomList(ListResult):

    def filter(self, **criterions) -> RoomList:
        ...

    def __getitem__(self, i: int) -> RoomObject:
        ...


class RoomObject(ListItem):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class SchoolyearList(ListResult):

    def filter(self, **criterions) -> SchoolyearList:
        ...

    def __getitem__(self, i: int) -> SchoolyearObject:
        ...

    @property
    def current(self) -> str:
        ...


class SchoolyearObject(ListItem):

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def is_current(self) -> bool:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def start(self) -> datetime.datetime:
        ...


class StatusData(Result):

    @property
    def lesson_types(self) -> List[ColorInfo]:
        ...

    @property
    def period_codes(self) -> List[ColorInfo]:
        ...


class SubjectList(ListResult):

    def filter(self, **criterions) -> SubjectList:
        ...

    def __getitem__(self, i: int) -> SubjectObject:
        ...


class SubjectObject(ListItem):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class StudentsList(ListResult):
    def filter(self, **criterions) -> StudentsList:
        ...

    def __getitem__(self, i: int) -> StudentObject:
        ...


class StudentObject(PersonObject):
    @property
    def full_name(self) -> str:
        ...


class SubstitutionList(ListResult):

    def filter(self, **criterions) -> SubstitutionList:
        ...

    def __getitem__(self, i: int) -> SubstitutionObject:
        ...


class SubstitutionObject(PeriodObject):

    @property
    def reschedule_end(self) -> datetime.datetime:
        ...

    @property
    def reschedule_start(self) -> datetime.datetime:
        ...

    @property
    def type(self) -> str:
        ...


class TeacherList(ListResult):

    def filter(self, **criterions) -> TeacherList:
        ...

    def __getitem__(self, i: int) -> TeacherObject:
        ...


class TeacherObject(PersonObject):
    @property
    def title(self) -> str:
        ...

    @property
    def full_name(self):
        ...


class TimeStampObject(Result):

    @property
    def date(self) -> datetime.datetime:
        ...


class TimeUnitObject(Result):

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def start(self) -> datetime.datetime:
        ...


class TimegridDayObject(Result):

    @property
    def day(self) -> str:
        ...

    @property
    def dayname(self) -> str:
        ...

    @property
    def timeUnits(self) -> List[TimeUnitObject]:
        ...


class TimegridObject(ListResult):

    def filter(self, **criterions) -> TimegridObject:
        ...

    def __getitem__(self, i: int) -> TimegridDayObject:
        ...
