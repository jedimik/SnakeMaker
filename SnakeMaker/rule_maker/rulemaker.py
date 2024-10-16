import SnakeMaker.rule_maker.rule_defaults as rdf
import SnakeMaker.utils as ut
from SnakeMaker.defaults import ConfigError
from SnakeMaker.rule_maker.rule import Rule, RuleBuilder


class Rulemaker:
    def __init__(self, rule_config: dict | str = None, shortened: bool = False):
        """
        Initializes a new instance of the Rulemaker class.
        """
        # Parameters
        self.rule_config = dict()
        self.rules = dict()
        self.rule_0 = None
        self.registered_names = dict()
        self.shortened = shortened  # If the paths are shortened
        # Initialize parameters
        self.initialize_config(rule_config)
        # Rules
        self.create_rules()

    def initialize_config(self, rule_config: dict | str):
        """
        Initializes the configuration for the Rulemaker class.

        Parameters:
        rule_config (dict | str): The configuration for the Rulemaker class.

        Args:
            rule_config (dict | str): The configuration for the Rulemaker class.
        """
        if isinstance(rule_config, str):
            self.rule_config = ut.load_config(rule_config)
        elif isinstance(rule_config, dict):
            self.rule_config = rule_config
        elif rule_config is None:
            msg = "Rule config is not provided. Check the config."
            ut.get_logger("error_logger").error(msg)
            raise ConfigError(msg)
        else:
            msg = f"Rule config is not in correct format. Check the config.:{rule_config}"
            ut.get_logger("error_logger").error(msg)
            print(f"{msg}. Check the rule config.")
            raise ConfigError(msg)
        # Check for rule 0 and rules
        self.rule_0 = self.rule_config.get("rule0", None)
        self.rule_config = (
            self.rule_config.get("rules", "") if "rules" in self.rule_config else self.rule_config
        )  # Check for nested rules in rules key

    def create_rules(self):
        for rule, rule_dict in self.rule_config.items():
            rule_builder = RuleBuilder(shortened=self.shortened)
            rule = (
                rule_builder.set_name(rule)
                .set_inputs(rule_dict.get("input", None), self.registered_names)
                .set_outputs(rule_dict.get("output", None), self.registered_names)
                .set_params(rule_dict.get("params", None), self.registered_names)
                .set_shell(rule_dict.get("shell", None), inputs=rule_builder.rule.inputs, outputs=rule_builder.rule.outputs)
                .set_description(rule_dict.get("description", None))
                .set_run(rule_dict.get("run", None), self.registered_names)
                .build()
            )

            self.rules[rule.name] = rule
        # Construct plane rule
        for rule in self.rules.values():
            rule.construct_plane_rule()
        # Write them to the file
        ut.create_directory(ut.get_env_variable("OUTPUT_RULE_MAKER_PATH"))
        with open(ut.merge_paths(ut.get_env_variable("OUTPUT_RULE_MAKER_PATH"), "rules.smk"), "w") as f:
            for rule in self.rules.values():
                f.write(rule.rule_string)
        pass

    def get_rules(self):
        return self.rules

    def get_rule_0(self):
        return self.rule_0

