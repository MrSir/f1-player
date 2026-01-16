from enum import Enum


class ConventionalSessionIdentifiers(Enum):
    FREE_PRACTICE_1 = "Practice 1"
    FREE_PRACTICE_2 = "Practice 2"
    FREE_PRACTICE_3 = "Practice 3"
    QUALIFYING = "Qualifying"
    RACE = "Race"

    @staticmethod
    def all_values() -> list[str]:
        return [member.value for member in ConventionalSessionIdentifiers]


class SprintQualifyingSessionIdentifiers(Enum):
    FREE_PRACTICE_1 = "Practice 1"
    SPRINT_QUALIFYING = "Sprint Qualifying"
    SPRINT = "Sprint"
    QUALIFYING = "Qualifying"
    RACE = "Race"

    @staticmethod
    def all_values() -> list[str]:
        return [member.value for member in SprintQualifyingSessionIdentifiers]
