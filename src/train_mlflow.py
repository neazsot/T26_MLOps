import argparse
import json
import hashlib
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn


def load_data(path):
    df = pd.read_csv(path)
    df['FlightDate'] = pd.to_datetime(df['FlightDate'])
    df = df.sort_values('FlightDate').reset_index(drop=True)
    df['target'] = (df['ArrDelay'] >= 15).astype(int)
    return df


def split_data(df):
    n = len(df)
    train_end = int(n * 0.6)
    val_end = int(n * 0.8)

    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]
    return train, val, test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--n-estimators", type=int, default=80)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--experiment", required=True)
    args = parser.parse_args()

    df = load_data(args.data)
    train, val, test = split_data(df)

    features = ['DepHour', 'IsWeekend']

    git_commit = "local_run"
    data_hash = hashlib.sha256(Path(args.data).read_bytes()).hexdigest()

    mlflow.set_experiment(args.experiment)

    with mlflow.start_run(run_name=f"rf-depth-{args.max_depth}"):
        mlflow.log_param("n_estimators", args.n_estimators)
        mlflow.log_param("max_depth", args.max_depth)
        mlflow.log_param("random_state", 42)

        mlflow.set_tag("git.commit", git_commit)
        mlflow.set_tag("data.sha256", data_hash)
        mlflow.set_tag("data.contract_version", "1.0.0")
        mlflow.set_tag("split.policy", "chronological-60-20-20")
        mlflow.set_tag("validation.status", "candidate")

        model = RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=42
        )
        model.fit(train[features], train['target'])

        y_pred_proba = model.predict_proba(val[features])[:, 1]
        y_pred = model.predict(val[features])

        roc_auc = roc_auc_score(val['target'], y_pred_proba)
        precision = precision_score(val['target'], y_pred, zero_division=0)
        recall = recall_score(val['target'], y_pred, zero_division=0)
        f1 = f1_score(val['target'], y_pred, zero_division=0)

        mlflow.log_metric("validation_roc_auc", roc_auc)
        mlflow.log_metric("validation_precision", precision)
        mlflow.log_metric("validation_recall", recall)
        mlflow.log_metric("validation_f1", f1)
        mlflow.log_metric("positive_class_share", float(val['target'].mean()))

        mlflow.sklearn.log_model(
            model,
            "model",
            skops_trusted_types=["sklearn.tree._tree.Tree"]
        )

        print(f"Run completed: ROC AUC = {roc_auc:.4f}, F1 = {f1:.4f}")


if __name__ == "__main__":
    main()