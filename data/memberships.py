from dataclasses import dataclass


@dataclass
class MemberCard:
    code: str
    label: str

    def __str__(self):
        return f"{self.label}"
