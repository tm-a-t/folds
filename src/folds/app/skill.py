from folds.rules.rule_builder_set import RuleBuilderSet
from folds.rules.rule import Rule


class Skill(RuleBuilderSet):
    """
    A set of rules that can be attached to a bot.
    """

    def __init__(self):
        super().__init__()
        self._rules: list[Rule] = []

    @property
    def rules(self):
        return tuple(self._rules)

    def _use_rule(self, rule: Rule):
        self._rules.append(rule)

    def use(self, skill: 'Skill'):
        self._rules += skill.rules
