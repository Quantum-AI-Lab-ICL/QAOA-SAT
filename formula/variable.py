class Variable:
    def __init__(self, id: int, is_negation: bool) -> None:
        """Class to represent variable in boolean formula.

        Args:
            id (int): Id of variable, x_n has id n
            is_negation (bool): True iff literal is a negation.
        """
        self.id = id
        self.is_negation = is_negation

    def is_satisfied(self, assignment: str) -> bool:
        """Determines whether variable is satisfied by assignment.

        Args:
            assignment (str): Assignment of entire formula.

        Returns:
            bool: True iff variable satisfied.
        """
        ass = bool(int(assignment[self.id]))
        return (self.is_negation and not ass) or (not self.is_negation and ass)

    def __repr__(self) -> str:
        return f"¬x{self.id}" if self.is_negation else f"x{self.id}"

    def __str__(self) -> str:
        return f"¬x{self.id}" if self.is_negation else f"x{self.id}"
