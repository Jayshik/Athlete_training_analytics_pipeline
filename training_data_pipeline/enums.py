from enum import Enum


class LabelledStrEnum(str, Enum):
    """
    Enum where members are also (and must be) strings
    """

    label: str

    def __new__(cls, *values: str):
        member = str.__new__(cls, values[0])
        member._value_ = values[0]

        if len(values) == 1:
            member.label = values[0]
        else:
            member.label = values[1]
        return member

    def _generate_next_value_(name, start, count, last_values):
        """
        Return the lower-cased version of the member name.
        """
        return name.lower()

    @classmethod
    def labels(cls):
        return [member.label for member in cls]

    def __str__(self) -> str:
        return self.value


class TrainingStimulus(LabelledStrEnum):
    NEUROMUSCULAR = "N", "Neuromuscular"
    ANAEROBIC = "AN", "Anaerobic"
    VO2MAX = "V", "VO2max"
    THRESHOLD = "T", "Threshold"
    AEROBIC = "A", "Aerobic"
    RECOVERY = "RV", "Recovery"
    LACTATE_CLEARANCE = "LC", "Lactate Clearance"
    FATIGUE_RESISTANCE = "FR", "Fatigue Resistance"
    ACTIVATION = "AV", "Activation"
    TEST = "TS", "Test"
    RACE = "R", "Race"


class IntensityV2(LabelledStrEnum):
    AEROBIC = "A", "Aerobic"
    TEMPO = "TP", "Tempo"
    THRESHOLD = "T", "Threshold"
    VO2MAX = "V", "VO2max"
    ANAEROBIC = "AN", "Anaerobic"
    NEUROMUSCULAR = "N", "Neuromuscular"


class Characteristic(LabelledStrEnum):
    MAXIMUM = "M", "Maximum"
    TORQUE = "T", "Torque"
    CADENCE = "C", "Cadence"
    PROGRESSIVE = "P", "Progressive"
    INTRA_RECOVERY = "R", "Intra-Recovery"
    DYNAMIC = "D", "Dynamic"
