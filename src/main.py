import mlflow
import argparse

def main():
    with mlflow.start_run() as run:
        mlflow.run(".", "stage_01", use_conda=False)
        mlflow.run(".", "stage_02", use_conda=False)
        mlflow.run(".", "stage_03", use_conda=False)
        mlflow.run(".", "stage_04", use_conda=False)

if __name__ == '__main__':
    main()