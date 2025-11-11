import enum


class Status(str, enum.Enum):
    PENDING = "назначена"
    IN_PROGRESS = "выполняется"
    CONTROL = "на контроле"
    DONE = "выполнена"
    OVERDUE = "просрочена"
