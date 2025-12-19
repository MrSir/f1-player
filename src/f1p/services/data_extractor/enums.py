from enum import Enum


class ConventionalSessionIdentifiers(Enum):
    FREE_PRACTICE_1 = "FP1"
    FREE_PRACTICE_2 = "FP2"
    FREE_PRACTICE_3 = "FP3"
    QUALIFYING = "Q"
    RACE = "R"

    @staticmethod
    def all_values() -> list[str]:
        return [member.value for member in ConventionalSessionIdentifiers]

class SprintQualifyingSessionIdentifiers(Enum):
    FREE_PRACTICE_1 = "FP1"
    QUALIFYING = "Q"
    SPRINT = "S"
    SPRINT_QUALIFYING = "SQ"
    RACE = "R"

    @staticmethod
    def all_values() -> list[str]:
        return [member.value for member in SprintQualifyingSessionIdentifiers]