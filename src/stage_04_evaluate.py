import argparse
import os
import shutil
from tqdm import tqdm
import logging
from src.utils.common import read_yaml, save_json
import joblib
import numpy as np
import sklearn.metrics as metrics
import math
import mlflow

STAGE = "Four"

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )



def main(config_path):
    mlflow.set_tracking_uri("http://127.0.0.1:1234")
    
    config = read_yaml(config_path)

    artifacts = config["artifacts"]
    featurized_data_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"], artifacts["FEATURIZED_DATA"])
    featurized_test_data_path = os.path.join(featurized_data_dir_path, artifacts["FEATURIZED_OUT_TEST"])

    model_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"], artifacts["MODEL_DIR"])
    model_path = os.path.join(model_dir_path, artifacts["MODEL_NAME"])

    model = joblib.load(model_path)
    matrix = joblib.load(featurized_test_data_path)

    labels = np.squeeze(matrix[:, 1].toarray())
    X = matrix[:,2:]

    predictions_by_class = model.predict_proba(X)
    predictions = predictions_by_class[:, 1]

    PRC_json_path = config["plots"]["PRC"]
    ROC_json_path = config["plots"]["ROC"]
    scores_json_path = config["metrics"]["SCORES"]

    avg_prec = metrics.average_precision_score(labels, predictions)
    roc_auc = metrics.roc_auc_score(labels, predictions)

    mlflow.log_metric("avg_prec", avg_prec)
    mlflow.log_metric("roc_auc", roc_auc)

    scores = {
        "avg_prec": avg_prec,
        "roc_auc": roc_auc
    }
    save_json(scores_json_path, scores)

    precision, recall, prc_threshold = metrics.precision_recall_curve(labels, predictions)
    
    nth_point = math.ceil(len(prc_threshold)/1000)
    prc_points = list(zip(precision, recall, prc_threshold))[::nth_point]

    prc_data = {
        "prc": [
            {"precision": p, "recall": r, "threshold": t}
            for p, r, t in prc_points
        ]
    }
    
    save_json(PRC_json_path, prc_data)
    
    fpr, tpr, roc_threshold = metrics.roc_curve(labels, predictions)

    roc_data = {
        "roc": [
            {"fpr": fp, "tpr": tp, "threshold": t}
            for fp, tp, t in zip(fpr, tpr, roc_threshold)
        ]
    }

    save_json(ROC_json_path, roc_data)

    mlflow.sklearn.eval_and_log_metrics(model, predictions, labels, prefix="eval_")





if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main(config_path=parsed_args.config)
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e