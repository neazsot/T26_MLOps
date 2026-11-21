import json
import hashlib
import sys
from pathlib import Path
import pandas as pd

def validate(data_path, contract_path):
    with open(contract_path, 'r') as f:
        contract = json.load(f)
    
    try:
        df = pd.read_csv(data_path)
    except Exception:
        return 1

    checks = []
    passed = True

    expected_cols = set(contract['columns'].keys())
    actual_cols = set(df.columns)
    if expected_cols != actual_cols:
        passed = False
        checks.append({"rule": "columns", "passed": False, "message": f"Expected {expected_cols}, got {actual_cols}"})
    else:
        checks.append({"rule": "columns", "passed": True})

    if len(df) < contract['minimum_rows']:
        passed = False
        checks.append({"rule": "min_rows", "passed": False, "message": f"Expected >= {contract['minimum_rows']}, got {len(df)}"})
    else:
        checks.append({"rule": "min_rows", "passed": True})

    nulls = df.isnull().sum()
    if nulls.any():
        passed = False
        checks.append({"rule": "nullable", "passed": False, "message": f"Nulls found: {nulls[nulls > 0].to_dict()}"})
    else:
        checks.append({"rule": "nullable", "passed": True})

    for col, rules in contract['columns'].items():
        if col not in df.columns:
            continue
        
        if rules.get('type') == 'integer':
            if not pd.api.types.is_integer_dtype(df[col]):
                passed = False
                checks.append({"rule": f"{col}_type", "passed": False, "message": "Not integer"})
            else:
                checks.append({"rule": f"{col}_type", "passed": True})
        
        if 'minimum' in rules and 'maximum' in rules:
            if df[col].min() < rules['minimum'] or df[col].max() > rules['maximum']:
                passed = False
                checks.append({"rule": f"{col}_range", "passed": False, "message": f"Out of range [{rules['minimum']}, {rules['maximum']}]"})
            else:
                checks.append({"rule": f"{col}_range", "passed": True})
        
        if 'allowed_values' in rules:
            if not df[col].isin(rules['allowed_values']).all():
                passed = False
                checks.append({"rule": f"{col}_values", "passed": False, "message": f"Allowed: {rules['allowed_values']}"})
            else:
                checks.append({"rule": f"{col}_values", "passed": True})

    if contract.get('duplicate_rows') == 'forbid':
        if df.duplicated().any():
            passed = False
            checks.append({"rule": "duplicates", "passed": False, "message": "Duplicates found"})
        else:
            checks.append({"rule": "duplicates", "passed": True})

    sha256 = hashlib.sha256(Path(data_path).read_bytes()).hexdigest()

    report = {
        "contract_version": contract['contract_version'],
        "dataset": contract['dataset'],
        "data_file": str(data_path),
        "sha256": sha256,
        "rows": len(df),
        "columns": list(df.columns),
        "passed": passed,
        "checks": checks
    }
    
    report_path = Path('reports/validation/lr2.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/validate_data.py <data.csv> <contract.json>")
        sys.exit(1)
    data_path = sys.argv[1]
    contract_path = sys.argv[2]
    sys.exit(validate(data_path, contract_path))
