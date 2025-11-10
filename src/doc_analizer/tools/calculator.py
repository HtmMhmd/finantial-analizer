from __future__ import annotations

import ast
import math
from typing import Any, Dict, Mapping, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """Input schema for the Calculator tool."""

    expression: str = Field(
        ..., description="Arithmetic expression to evaluate (e.g., '((revenue - cogs)/revenue) * 100')."
    )
    variables: Mapping[str, float] | None = Field(
        default=None,
        description="Optional variables available to the expression, e.g., {'revenue': 1000, 'cogs': 400}",
    )


class CalculatorTool(BaseTool):
    """A safe calculator for arithmetic and common financial computations.

    Supports +, -, *, /, **, unary +/- and parentheses. Also allows a small
    whitelist of math functions: abs, round, min, max, sqrt, log, exp, pow.
    Variables can be injected via the 'variables' mapping.
    """

    name: str = "calculator"
    description: str = (
        "Safely evaluate arithmetic expressions with optional variables and a small set of math functions. "
        "Use this when you need exact numeric calculations (ratios, growth rates, scenario math)."
    )
    args_schema: Type[BaseModel] = CalculatorInput

    _allowed_funcs: Dict[str, Any] = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sqrt": math.sqrt,
        "log": math.log,
        "exp": math.exp,
        "pow": pow,
    }

    _allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.Name,
        ast.Call,
        ast.Constant,
        ast.Tuple,
        ast.List,
    )

    def _safe_eval(self, expression: str, variables: Mapping[str, float] | None) -> float:
        tree = ast.parse(expression, mode="eval")
        for node in ast.walk(tree):

            if not isinstance(node, self._allowed_nodes):
                raise ValueError(f"Disallowed expression element: {type(node).__name__}")
            
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in self._allowed_funcs:
                    raise ValueError("Only whitelisted math functions are permitted")
        
        env: Dict[str, Any] = {}

        if variables:
            # Copy variables while ensuring only numbers

            for k, v in variables.items():
                if not isinstance(v, (int, float)):
                    raise ValueError(f"Variable '{k}' must be numeric")
        
            env.update(variables)
        
        env.update(self._allowed_funcs)
        code = compile(tree, filename="<calc>", mode="eval")
        result = eval(code, {"__builtins__": {}}, env)
        
        if not isinstance(result, (int, float)):
            raise ValueError("Expression did not evaluate to a numeric result")
        return float(result)

    def _run(self, expression: str, variables: Mapping[str, float] | None = None) -> Dict[str, Any]:
        value = self._safe_eval(expression, variables)
        return {"expression": expression, "variables": dict(variables or {}), "result": value}
