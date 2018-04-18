import datetime
from typing import List, Tuple

from webuntis import Session


class Result(object):

    def __init__(self, data, parent: Result = None, session: Session = None) -> None:
        self._session = session or parent._session
        self._parent = parent
        self._data = data

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
    _itemclass = ListItem

    def filter(self, **criterions) -> ListResult:
        ...

    def __contains__(self, criterion) -> bool:
        ...

    def __getitem__(self, i: int) -> ListItem:
        ...

    def __len__(self) -> int:
        ...


class ColorMixin:
    @property
    def backcolor(self) -> str:
        ...

    @property
    def forecolor(self) -> str:
        ...


class ColorInfo(Result):

    @property
    def name(self) -> str:
        ...


class DepartmentObject(ListItem):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class DepartmentList(ListResult):
    _itemclass = DepartmentObject

    def filter(self, **criterions) -> DepartmentList:
        ...

    def __getitem__(self, i: int) -> DepartmentObject:
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


class HolidayList(ListResult):
    _itemclass = HolidayObject

    def filter(self, **criterions) -> HolidayList:
        ...

    def __getitem__(self, i: int) -> HolidayObject:
        ...


class KlassenObject(ListItem, ColorMixin):
    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class KlassenList(ListResult):
    _itemclass = KlassenObject

    def filter(self, **criterions) -> KlassenList:
        ...

    def __getitem__(self, i: int) -> KlassenObject:
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


class PeriodList(ListResult):
    _itemclass = PeriodObject

    def filter(self, **criterions) -> PeriodList:
        ...

    def __getitem__(self, i: int) -> PeriodObject:
        ...

    def to_table(self) -> List[Tuple[datetime.time, List[Tuple[datetime.date, PeriodList]]]]:
        ...

    def combine(self) -> PeriodList:
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


class RoomObject(ListItem, ColorMixin):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class RoomList(ListResult):
    _itemclass = RoomObject

    def filter(self, **criterions) -> RoomList:
        ...

    def __getitem__(self, i: int) -> RoomObject:
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


class SchoolyearList(ListResult):
    _itemclass = SchoolyearObject

    def filter(self, **criterions) -> SchoolyearList:
        ...

    def __getitem__(self, i: int) -> SchoolyearObject:
        ...

    @property
    def current(self) -> SchoolyearObject:
        ...


class StatusData(Result):

    @property
    def lesson_types(self) -> List[ColorInfo]:
        ...

    @property
    def period_codes(self) -> List[ColorInfo]:
        ...


class SubjectObject(ListItem, ColorMixin):

    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class SubjectList(ListResult):
    _itemclass = SubjectObject

    def filter(self, **criterions) -> SubjectList:
        ...

    def __getitem__(self, i: int) -> SubjectObject:
        ...


class StudentObject(PersonObject):
    @property
    def full_name(self) -> str:
        ...

    @property
    def gender(self) -> str:
        ...


class StudentsList(ListResult):
    _itemclass = StudentObject

    def filter(self, **criterions) -> StudentsList:
        ...

    def __getitem__(self, i: int) -> StudentObject:
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


class SubstitutionList(ListResult):
    _itemclass = SubstitutionObject

    def filter(self, **criterions) -> SubstitutionList:
        ...

    def __getitem__(self, i: int) -> SubstitutionObject:
        ...

    def combine(self) -> SubstitutionList:
        ...


class TeacherObject(PersonObject):
    @property
    def title(self) -> str:
        ...

    @property
    def full_name(self):
        ...


class TeacherList(ListResult):
    _itemclass = TeacherObject

    def filter(self, **criterions) -> TeacherList:
        ...

    def __getitem__(self, i: int) -> TeacherObject:
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
    def time_units(self) -> List[TimeUnitObject]:
        ...


class TimegridObject(ListResult):
    _itemclass = TimegridDayObject

    def filter(self, **criterions) -> TimegridObject:
        ...

    def __getitem__(self, i: int) -> TimegridDayObject:
        ...


class ExamTypeObject(Result):
    @property
    def long_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def show_in_timetable(self) -> bool:
        ...


class ExamTypeList(ListResult):
    _itemclass = ExamTypeObject

    def filter(self, **criterions) -> ExamTypeList:
        ...

    def __getitem__(self, i: int) -> ExamTypeObject:
        ...


class ExamObject(Result):
    @property
    def start(self) -> datetime.datetime:
        ...

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def klassen(self) -> KlassenList:
        ...

    @property
    def subject(self) -> SubjectObject:
        ...

    @property
    def teachers(self) -> TeacherList:
        ...

    @property
    def students(self) -> StudentsList:
        ...


class ExamsList(ListResult):
    _itemclass = ExamObject

    def filter(self, **criterions) -> ExamsList:
        ...

    def __getitem__(self, i: int) -> ExamObject:
        ...


class AbsenceObject(Result):
    @property
    def start(self) -> datetime.datetime:
        ...

    @property
    def end(self) -> datetime.datetime:
        ...

    @property
    def student(self) -> SubjectObject:
        ...

    @property
    def subject(self) -> SubjectObject:
        ...

    @property
    def teachers(self) -> TeacherList:
        ...

    @property
    def student_group(self) -> str:
        ...

    @property
    def checked(self) -> bool:
        ...

    @property
    def reason(self) -> str:
        ...

    @property
    def time(self) -> int:
        ...


class AbsencesList(ListResult):
    _itemclass = AbsenceObject

    def filter(self, **criterions) -> AbsencesList:
        ...

    def __getitem__(self, i: int) -> AbsenceObject:
        ...


class ClassRegEvent(Result):
    @property
    def student(self) -> StudentObject:
        ...

    @property
    def sur_name(self) -> str:
        ...

    @property
    def fore_name(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def reason(self) -> str:
        ...

    @property
    def text(self) -> str:
        ...

    @property
    def date(self) -> date:
        ...

    @property
    def subject(self) -> str:
        ...


class ClassRegEventList(ListResult):
    _itemclass = ClassRegEvent

    def filter(self, **criterions) -> ClassRegEventList:
        ...

    def __getitem__(self, i: int) -> ClassRegEvent:
        ...
