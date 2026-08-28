class KnowledgeBase:
    """
    A declarative Knowledge Base that stores dynamic facts, Horn clause rules,
    and infers new facts using a Data-Driven Forward Chaining algorithm.
    """
    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell_fact(self, fact_string: str) -> None:
        """Adds a unique atomic fact to the Knowledge Base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str) -> None:
        """
        Adds a Horn clause rule to the Knowledge Base in the form:
        IF all(premise_list) THEN conclusion_string.
        """
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self) -> None:
        """Clears all temporary facts from the Knowledge Base while preserving static rules."""
        self.facts.clear()

    def forward_chain(self) -> None:
        """
        Executes Data-Driven Forward Chaining using Modus Ponens.
        Iteratively derives new facts until no further conclusions can be drawn.
        """
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    # Modus Ponens Check: all premises must currently exist in self.facts
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True