resource "aws_instance" "bastion-instance" {
    ami                    = lookup(var.amis, var.region)
    instance_type          = "t2.micro"
    subnet_id              = aws_subnet.public-subnet-1.id
    vpc_security_group_ids = [aws_security_group.allow-ssh.id]
    key_name               = aws_key_pair.production.key_name

    tags = {
        Name = "bastion-instance"
    }
}