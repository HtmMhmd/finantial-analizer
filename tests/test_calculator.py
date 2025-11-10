from doc_analizer.tools.calculator import CalculatorTool


def run_case(expr, vars=None):
    tool = CalculatorTool()
    return tool._run(expr, vars or {})["result"]


def expect_exception(expr, vars=None):
    try:
        run_case(expr, vars)
    except Exception:
        return True
    return False


def main():
    passed = 0
    failed = 0

    cases = [
        ("2 + 2", None, 4.0),
        ("(1 + 2) * 3", None, 9.0),
        ("revenue - cogs", {"revenue": 1000, "cogs": 400}, 600.0),
        (
            "((revenue - cogs) / revenue) * 100",
            {"revenue": 1000, "cogs": 400},
            60.0,
        ),
        ("round( sqrt(144) + 0.49, 0 )", None, 12.0),
        ("max(10, 20, 5) - min(3, 7)", None, 17.0),
        ("pow(2, 10)", None, 1024.0),
        # Financial: gross margin %
        (
            "((revenue - cogs) / revenue) * 100",
            {"revenue": 2_500_000, "cogs": 1_750_000},
            30.0,
        ),
        # Current ratio
        (
            "current_assets / current_liabilities",
            {"current_assets": 4_475_652, "current_liabilities": 56_000},
            79.91842857142857,
        ),
        # Quick ratio = (CA - Inventory) / CL
        (
            "(current_assets - inventory) / current_liabilities",
            {"current_assets": 600_000, "inventory": 120_000, "current_liabilities": 200_000},
            2.4,
        ),
        # Debt-to-equity = Total Debt / Equity
        (
            "total_debt / equity",
            {"total_debt": 1_200_000, "equity": 800_000},
            1.5,
        ),
        # ROA = Net Income / Total Assets
        (
            "net_income / total_assets",
            {"net_income": 250_000, "total_assets": 5_000_000},
            0.05,
        ),
        # ROE = Net Income / Equity
        (
            "net_income / equity",
            {"net_income": 250_000, "equity": 1_250_000},
            0.2,
        ),
        # CAGR = (ending/beginning)^(1/n) - 1
        (
            "pow(ending / beginning, 1/years) - 1",
            {"ending": 1_350_000, "beginning": 1_000_000, "years": 3},
            0.10471285480509043,
        ),
        # Simple 3-period NPV = -initial + c1/(1+r)^1 + c2/(1+r)^2 + c3/(1+r)^3
        (
            "-initial + c1 / pow(1+rate,1) + c2 / pow(1+rate,2) + c3 / pow(1+rate,3)",
            {"initial": 1_000, "c1": 400, "c2": 500, "c3": 600, "rate": 0.1},
            276.2998754688672,
        ),
        # WACC = wd*kd*(1-t) + we*ke
        (
            "wd*kd*(1-tax) + we*ke",
            {"wd": 0.4, "kd": 0.07, "tax": 0.25, "we": 0.6, "ke": 0.12},
            0.091,
        ),
    ]

    for expr, vars, expected in cases:
        try:
            result = run_case(expr, vars)
            if abs(result - expected) < 1e-9:
                passed += 1
            else:
                print(f"FAIL: {expr} => {result} (expected {expected})")
                failed += 1
        except Exception as e:
            print(f"ERROR: {expr} raised {e}")
            failed += 1

    # Error cases
    error_exprs = [
        ("1 / 0", None),  # ZeroDivisionError
        ("__import__('os').system('echo hi')", None),  # Disallowed call
        ("revenue + 1", {"revenue": "not-a-number"}),  # Non-numeric var
    ]

    for expr, vars in error_exprs:
        if expect_exception(expr, vars):
            passed += 1
        else:
            print(f"FAIL: Expected exception but got success for expr: {expr}")
            failed += 1

    total = passed + failed
    print(f"Calculator tests: {passed}/{total} passed, {failed} failed.")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
