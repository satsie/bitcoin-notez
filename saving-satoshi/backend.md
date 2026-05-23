# Notes on [autoscaling PR](https://github.com/saving-satoshi/saving-satoshi-backend/pull/104)

## AMIs

AMI = Amazon virtual machine image. Snapshot of a virtual machine. Made with Packer.

`check-ami-changes`: If anything sensitive has changed, we build a new AMI

The build artifact is an AMI. We spin new images up off this base image.

`playbook-base.yaml`: All the stuff to build the AMI. Heavy stuff. Only runs once.
`playbook-runtime.yaml`: What the AMI runs on startup (installs yarn dependencies, starts the Saving Satoshi backend server, etc.). All the lighter stuff.

## Autoscaling

The Terraform code defines what instance sizes the horizontal autoscaling will pick from (`spot_instance_types`)

GitHub Secrets & Actions -> Variables -> `AWS_EC2_INSTANCE_TYPE`

The autoscaling group (ASG) manages the instances

There is a grace period on the autoscaling group and load balancer to make sure we don't keep scaling up infinitely while we wait for new instances to come up.

As the load balancer winds instances down, it will slowly drain connections.

It is possible to do a instance refresh on the autoscaling group. Doing so will kill everything and restart the instances. This happens everytime there is a new deployment so that if there is a new AMI, it gets picked up, as well as any other relevant changes like updates to secrets and variables.

Currently using `t2.small` but `t3.small` is probably a better choice for the Saving Satoshi backend. Can also expose the spot types (a special type of AWS EC2 instance type that is cheaper because AWS reserves the right to reclaim the resources as needed) as a variable.

Improvement idea: use one variable for the instance size, use that same variable for the Terraform autoscaling.

Possible alternative to AWS: [Hetzner](https://www.hetzner.com/). Can get more CPU for the same amount of money. It will probably cost $20 a month for the load balancer to sit around.

## Next steps

1. Merge the PR, sort out the variables in GitHub.
2. Run the load tests on staging. Observe the autoscaling working.
3. Try out some different hardware to determine if there is a better choice for the default instance size/type
4. Deploy to production