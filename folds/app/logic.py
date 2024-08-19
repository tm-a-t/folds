from folds.rules.rule_builder_set import RuleBuilderSet
from folds.rules.rule import Rule


class Logic(RuleBuilderSet):
    def __init__(self):
        super().__init__()
        self._rules: list[Rule] = []

    @property
    def rules(self):
        return tuple(self._rules)

    def _use_rule(self, rule: Rule):
        self._rules.append(rule)

    def use_logic(self, logic: 'Logic'):
        self._rules += logic.rules
