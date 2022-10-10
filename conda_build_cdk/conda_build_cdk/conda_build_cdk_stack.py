from aws_cdk import Stack
from constructs import Construct
import aws_cdk.aws_iam as iam
import aws_cdk.pipelines as pipelines
import aws_cdk.aws_codebuild as codebuild


class CondaBuildCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, resource_names: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipelines.CodePipeline(
            self,
            resource_names["project_name"] + "Pipeline",
            cross_account_keys=True,
            self_mutation=False,
            synth=pipelines.CodeBuildStep(
                "Synth",
                # Use a connection created using the AWS console to authenticate to GitHub
                # Other sources are available.
                input=pipelines.CodePipelineSource.connection(
                    repo_string=resource_names["repo_owner"] + "/" + resource_names["repo_name"],
                    branch=resource_names["repo_branch"],
                    connection_arn="arn:aws:codestar-connections:ap-southeast-2:785965938585:connection/5f3aaa9a-c98f-484b-a1a5-5bcde080b4ff"
                ),
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.from_asset(
                        self,
                        resource_names["project_name"] + "DockerImage",
                        directory="../",
                        file=resource_names["dockerfile_name"]
                    ),
                    environment_variables={
                        'conda_channel_bucket': codebuild.BuildEnvironmentVariable(
                            value=resource_names['conda_channel_bucket'],
                            type=codebuild.BuildEnvironmentVariableType.PLAINTEXT
                        ),
                        'conda_channel_name': codebuild.BuildEnvironmentVariable(
                            value=resource_names['conda_channel_name'],
                            type=codebuild.BuildEnvironmentVariableType.PLAINTEXT
                        )
                    },
                    privileged=True
                ),
                install_commands=[
                    'npm install -g n aws-cdk@2.26.0',
                    'n lts',
                    'echo `cdk --version`',
                    'python -m ensurepip --upgrade',
                    'python -m pip install --upgrade pip',
                    'mkdir /mnt/channels',
                    'goofys $conda_channel_bucket /mnt/channels',
                ],
                commands=[
                    "python setup.py bdist_conda",
                    "cp /opt/conda/conda-bld/linux-64/metaflow-* /mnt/channels/$conda_channel_name/linux-64/",
                    #"LINUX64_PACKAGES=/mnt/channels/$conda_channel_name/linux-64/*.tar.bz2 && conda convert -f --platform osx-64 ${LINUX64_PACKAGES} -o /mnt/channels/$conda_channel_name",
                    "conda index --no-progress /mnt/channels/$conda_channel_name",
                    "cd conda_build_cdk && pip install --upgrade -r requirements.txt",
                    "cdk synth"
                ],
                primary_output_directory="conda_build_cdk/cdk.out",
                role_policy_statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            's3:ListBucket',
                            's3:GetObject',
                            's3:GetObjectAcl',
                            's3:PutObject',
                            's3:PutObjectAcl',
                            's3:DeleteObject'
                        ],
                        resources=[
                            "arn:aws:s3:::"+resource_names['conda_channel_bucket'],
                            "arn:aws:s3:::"+resource_names['conda_channel_bucket'] + "/*"]
                    )
                ]
            )
        )
