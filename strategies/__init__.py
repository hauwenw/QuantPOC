import importlib
import re


def _camel_to_snake(text):
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', text).lower()


def get_strategy_class(strategy_name):
    try:
        module = importlib.import_module(f".{_camel_to_snake(strategy_name)}", package="strategies")
        strategy_class = getattr(module, strategy_name)
        return strategy_class
    except (ImportError, AttributeError):
        raise ValueError(f"Invalid strategy name: {strategy_name}")
