#!/usr/bin/env python3
import re
from aws_cdk import App
from conda_build_cdk.conda_build_cdk_stack import CondaBuildCdkStack

PROJECT_REPO = "metaflow"

RESOURCE_NAMES = {
    'repo_name': PROJECT_REPO,
    'repo_owner': "building-estimates",
    'repo_branch': "master",
    'project_name': ''.join(part.title() for part in re.split(', |_|-|!',  PROJECT_REPO)),
    'dockerfile_name': "Dockerfile.codebuild",
    'conda_channel_bucket': "building-estimates-conda-channel",
    'conda_channel_name': "brain-engine"
}

app = App()
CondaBuildCdkStack(
    app,
    RESOURCE_NAMES["project_name"] + "Stack",
    RESOURCE_NAMES,
    stack_name=RESOURCE_NAMES["project_name"] + "Stack",
    env={
        "account": '785965938585',
        "region": 'ap-southeast-2',
    })

app.synth()
