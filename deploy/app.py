from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_lambda
from aws_cdk import core
from aws_cdk.aws_logs import RetentionDays


def create_sqlite_on_efs_stack(app):
    stack = core.Stack(app, "sqlite-on-efs")

    subnet_configuration = [
        ec2.SubnetConfiguration(
            name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
        )
    ]

    vpc = ec2.Vpc(
        stack,
        "sqlite-on-efs-vpc",
        cidr="10.0.0.0/21",
        max_azs=1,
        subnet_configuration=subnet_configuration,
    )

    code = aws_lambda.DockerImageCode.from_image_asset("..")

    security_group = ec2.SecurityGroup(
        stack,
        "sqlite-on-efs-sg",
        vpc=vpc,
        allow_all_outbound=True,
        security_group_name="sqlite-on-efs",
    )
    subnet_selection = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
    aws_lambda.DockerImageFunction(
        stack,
        "sqlite-on-efs-lambda",
        code=code,
        vpc=vpc,
        allow_public_subnet=True,
        vpc_subnets=subnet_selection,
        log_retention=RetentionDays.ONE_WEEK,
        security_group=security_group,
        function_name="sqlite-on-efs",
    )


app = core.App()

crawler = create_sqlite_on_efs_stack(app)

app.synth()
