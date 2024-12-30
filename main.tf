provider "aws" {
  region = "ap-south-1"  # Mumbai region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

resource "aws_security_group" "allow_all" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "sonarqube" {
  ami           = "ami-053b12d3152c0cc71"  # Provided AMI for Mumbai region
  instance_type = "t2.medium"
  subnet_id     = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.allow_all.id]

  tags = {
    Name = "SonarQube"
  }
}

resource "aws_instance" "jenkins" {
  ami           = "ami-053b12d3152c0cc71"  # Provided AMI for Mumbai region
  instance_type = "t2.medium"
  subnet_id     = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.allow_all.id]

  tags = {
    Name = "Jenkins"
  }
}

resource "aws_instance" "docker_server" {
  ami           = "ami-053b12d3152c0cc71"  # Provided AMI for Mumbai region
  instance_type = "t2.medium"
  subnet_id     = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.allow_all.id]

  tags = {
    Name = "Docker-Server"
  }
}

resource "aws_elb" "main" {
  name               = "main-load-balancer"
  subnets            = [aws_subnet.main.id]  # Ensure ELB is in the same VPC

  listener {
    instance_port     = 80
    instance_protocol = "HTTP"
    lb_port           = 80
    lb_protocol       = "HTTP"
  }

  instances = [
    aws_instance.docker_server.id,
  ]

  health_check {
    target              = "HTTP:80/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "main-load-balancer"
  }
}
