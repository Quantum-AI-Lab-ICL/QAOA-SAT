class Variable:
    def __init__(self, id: int, is_negation: bool) -> None:
        self.id = id
        self.is_negation = is_negation

    def __repr__(self) -> str:
        return f"¬x{self.id}" if self.is_negation else f"x{self.id}"

    def __str__(self) -> str:
        return f"¬x{self.id}" if self.is_negation else f"x{self.id}"

    def is_satisfied(self, assignment: str) -> bool:
        ass = bool(int(assignment[self.id]))
        return (self.is_negation and not ass) or (not self.is_negation and ass)
