from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_backup as backup
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_efs as efs
from aws_cdk import aws_events as events
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
    filesystem = efs.FileSystem(
        stack,
        "sqlite-on-efs-fs",
        file_system_name="sqlite-on-efs",
        vpc=vpc,
        security_group=security_group,
        vpc_subnets=subnet_selection,
        removal_policy=core.RemovalPolicy.DESTROY,
    )

    core.CfnOutput(stack, "file_system_id", value=filesystem.file_system_id)

    filesystem_ap = filesystem.add_access_point(
        "sqlite-on-efs",
        path="/data",
        create_acl=efs.Acl(owner_uid="1000", owner_gid="1000", permissions="0755"),
        posix_user=efs.PosixUser(uid="1000", gid="1000"),
    )

    handler = aws_lambda.DockerImageFunction(
        stack,
        "sqlite-on-efs-lambda",
        code=code,
        vpc=vpc,
        allow_public_subnet=True,
        vpc_subnets=subnet_selection,
        log_retention=RetentionDays.ONE_WEEK,
        security_group=security_group,
        function_name="sqlite-on-efs",
        filesystem=aws_lambda.FileSystem.from_efs_access_point(
            ap=filesystem_ap, mount_path="/mnt/data"
        ),
        timeout=core.Duration.seconds(30),
    )

    apigateway.LambdaRestApi(
        stack, "sqlite-on-efs-gw", handler=handler, rest_api_name="sqlite-on-efs"
    )

    backup_vault = backup.BackupVault(
        stack,
        "sqlite-on-efs-backup-vault",
        backup_vault_name="sqlite-on-efs",
        removal_policy=core.RemovalPolicy.DESTROY,
    )

    backup_plan = backup.BackupPlan(
        stack,
        "sqlite-on-efs-backup",
        backup_plan_name="sqlite-on-efs",
        backup_vault=backup_vault,
    )
    backup_plan.add_selection(
        "sqlite-on-efs",
        resources=[backup.BackupResource.from_efs_file_system(filesystem)],
    )
    backup_rule = backup.BackupPlanRule(
        delete_after=core.Duration.days(15),
        rule_name="squeaky-on-efs",
        schedule_expression=events.Schedule.cron(hour="1", minute="00"),
    )
    backup_plan.add_rule(backup_rule)

    init_config = ec2.InitConfig(
        [
            ec2.InitFile.from_file_inline(
                "/home/ec2-user/.ssh/authorized_keys", "/root/.ssh/id_rsa.pub"
            ),
            ec2.InitPackage.yum("amazon-efs-utils"),
            ec2.InitCommand.shell_command(
                f"""sudo -u ec2-user aws configure set region {stack.region};
                mkdir /mnt/data;
                mount -t efs {filesystem.file_system_id}:/data /mnt/data;
            """
            ),
        ]
    )
    bastion_init = ec2.CloudFormationInit.from_config(init_config)

    bastion_host = ec2.Instance(
        stack,
        "squeaky-on-efs-bastion",
        vpc=vpc,
        instance_name="squeaky-on-efs",
        security_group=security_group,
        vpc_subnets=subnet_selection,
        instance_type=ec2.InstanceType("t3a.nano"),
        init=bastion_init,
        machine_image=ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        ),
    )

    security_group.add_ingress_rule(
        ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access"
    )

    core.CfnOutput(
        stack, "bastion_public_dns", value=bastion_host.instance_public_dns_name
    )


app = core.App()

crawler = create_sqlite_on_efs_stack(app)

app.synth()
