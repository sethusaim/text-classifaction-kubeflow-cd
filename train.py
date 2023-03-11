import os

from kfp import Client
from kfp.components import load_component_from_file
from kfp.dsl import ContainerOp, pipeline
from kubernetes.client.models import V1EnvVar

from api.auth import get_istio_auth_session

KUBEFLOW_ENDPOINT = os.environ["KUBEFLOW_ENDPOINT"]
KUBEFLOW_USERNAME = os.environ["KUBEFLOW_USERNAME"]
KUBEFLOW_PASSWORD = os.environ["KUBEFLOW_PASSWORD"]
MONGO_DB_URL = os.environ["MONGO_DB_URL"]

auth_session = get_istio_auth_session(
    url=KUBEFLOW_ENDPOINT, username=KUBEFLOW_USERNAME, password=KUBEFLOW_PASSWORD
)

data_ingestion = load_component_from_file("kfp_components/data_ingestion.yaml")

data_validation = load_component_from_file("kfp_components/data_validation.yaml")

data_transformation = load_component_from_file(
    "kfp_components/data_transformation.yaml"
)

model_training = load_component_from_file("kfp_components/model_training.yaml")

model_evaluation = load_component_from_file("kfp_components/model_evaluation.yaml")

model_pusher = load_component_from_file("kfp_components/model_pusher.yaml")


@pipeline(name="Train Pipeline")
def train_pipeline():
    task_1: ContainerOp = data_ingestion()

    env_var = V1EnvVar(name="MONGO_DB_URL", value=MONGO_DB_URL)

    task_1.container.add_env_variable(env_var)

    task_2: ContainerOp = data_validation()

    task_2.after(task_1)

    task_3: ContainerOp = data_transformation()

    task_3.after(task_2)

    task_4: ContainerOp = model_training()

    task_4.after(task_3)

    task_5: ContainerOp = model_evaluation()

    task_5.after(task_4)

    task_6: ContainerOp = model_pusher()

    task_6.after(task_5)


if __name__ == "__main__":
    client = Client(
        host=f"{KUBEFLOW_ENDPOINT}/pipeline", cookies=auth_session["session_cookie"]
    )

    client.create_run_from_pipeline_func(
        pipeline_func=train_pipeline,
        arguments={},
        namespace="kubeflow-user-example-com",
        experiment_name="ecom-exp",
        service_account="kube-ecom-sa",
        enable_caching=False,
    ).wait_for_run_completion()
