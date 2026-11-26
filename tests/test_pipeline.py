import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from src.validate_data import validate
from src.train_mlflow import load_data, split_data

CONTRACT = "data/contract.json"

@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("DepHour", 25),
        ("IsWeekend", 2),
        ("FlightDate", "bad-date"),
    ],
)
def test_invalid_values_are_rejected(valid_frame, csv_factory, column, value):
    frame = valid_frame.copy()
    frame.loc[0, column] = value
    result = validate(csv_factory(frame), CONTRACT)
    assert result == 1

def test_missing_column_is_rejected(valid_frame, csv_factory):
    frame = valid_frame.drop(columns=["ArrDelay"])
    result = validate(csv_factory(frame), CONTRACT)
    assert result == 1

def test_model_bundle_is_deterministic(valid_frame):
    df = load_data_from_frame(valid_frame)
    train, val = split_data(df)
    features = ['DepHour', 'IsWeekend']
    model1 = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    model1.fit(train[features], train['target'])
    proba1 = model1.predict_proba(val[features])[:, 1]
    model2 = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    model2.fit(train[features], train['target'])
    proba2 = model2.predict_proba(val[features])[:, 1]
    assert pytest.approx(proba1, abs=1e-5) == proba2

def test_prediction_shape_and_range(valid_frame):
    df = load_data_from_frame(valid_frame)
    train, val = split_data(df)
    features = ['DepHour', 'IsWeekend']
    model = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    model.fit(train[features], train['target'])
    single_row = val[features].iloc[[0]]
    proba = model.predict_proba(single_row)
    assert proba.shape == (1, 2)
    assert 0.0 <= proba[0, 1] <= 1.0

def test_integration_smoke(valid_frame, tmp_path):
    data_path = tmp_path / "smoke_data.csv"
    valid_frame.to_csv(data_path, index=False)
    df = load_data(data_path)
    train, val = split_data(df)
    features = ['DepHour', 'IsWeekend']
    model = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    model.fit(train[features], train['target'])
    predictions = model.predict(val[features])
    assert len(predictions) == len(val)

def load_data_from_frame(frame):
    df = frame.copy()
    df['FlightDate'] = pd.to_datetime(df['FlightDate'])
    df = df.sort_values('FlightDate').reset_index(drop=True)
    df['target'] = (df['ArrDelay'] >= 15).astype(int)
    return df