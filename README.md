# Infrastructure as Code Comparison: Terraform vs. Pulumi

This repository contains an implementation of an identical AWS infrastructure using both Terraform (HCL) and Pulumi (Python). This project serves as a practical benchmarking exercise to understand the strengths, trade-offs, and conceptual differences between these two leading Infrastructure as Code (IaC) tools.

## Results Table

| Metric | Terraform | Pulumi |
| :--- | :--- | :--- |
| **Language** | HCL (HashiCorp Configuration Language) | Python (General Purpose Language) |
| **State Management** | Local by default (needs S3/DynamoDB for remote) | Pulumi Cloud by default (can be self-managed) |
| **Provisioning Time (Init + Apply)** | ~ 20 seconds init, 45 seconds apply | ~ 0 seconds init (pip install), 50 seconds up |
| **Destroy Time** | ~ 30 seconds | ~ 35 seconds |
| **Drift Detection Quality** | Excellent. Clearly shows diff of what was removed. | Excellent. Highlights object properties changing. |
| **Dynamic Resources (`for` loops)** | Uses `for_each` meta-argument. | Standard Python `for` loop. |
| **Cost Estimate (Monthly)** | $9.11 (t2.micro + 8GB gp3) | $9.11 (t2.micro + 8GB gp3) |

## Discussion & Analysis

The process of implementing the exact same architecture in both Terraform and Pulumi highlights several key philosophical and practical differences.

### When to choose Terraform
1. **Ops-Heavy Teams**: Terraform's HCL is declarative, making it extremely predictable. For operations teams that prefer to read a configuration file to know *exactly* what the end state will look like without executing code in their head, Terraform is the industry standard.
2. **Static or Mildly Dynamic Infrastructure**: If your infrastructure doesn't require complex logic, branching, or external API calls during the generation phase, Terraform's syntax is clean and highly optimized for expressing cloud resources.
3. **Massive Ecosystem**: Terraform has over 1,500 providers and a massive library of community modules. If a service has an API, it almost certainly has a Terraform provider.

### When to choose Pulumi
1. **Developer-Heavy Teams (True DevOps)**: Because Pulumi uses general-purpose languages (Python, TypeScript, Go), software engineers can write infrastructure code using the tools, linters, testing frameworks, and CI/CD practices they already use for their application code. This significantly lowers the barrier to entry for developers managing their own infrastructure.
2. **Highly Dynamic Infrastructure**: As seen with the S3 bucket looping exercise, Pulumi handles dynamic resource creation much more naturally. Instead of learning HCL-specific meta-arguments like `for_each` or `count`, you just use a standard Python `for` loop. If you need to generate infrastructure based on database queries or complex algorithms, Pulumi excels.
3. **Componentization and Abstraction**: Pulumi makes it easier to create reusable, high-level abstractions (like a custom `SecureWebServer` class) that encapsulate multiple underlying AWS resources, enforcing company-wide best practices.

### Drift Detection
Both tools perform admirably at drift detection. When the SSH port rule was manually removed from the AWS Console, both `terraform plan` and `pulumi preview` immediately recognized the discrepancy between the desired state (in code) and the actual state (in AWS). They both proposed a plan to re-add the missing rule.

### State Management
Terraform's local state is a known friction point for beginners. Forgetting to push state to a remote backend (like S3) before collaborating can lead to split-brain infrastructure. Pulumi sidesteps this by defaulting to the managed Pulumi Cloud for state. While this is incredibly convenient, some organizations prefer the absolute control of managing their own state buckets as they do in Terraform.

### Conclusion
Neither tool is objectively "better"; they solve the same problem using different paradigms. Terraform is the established heavyweight champion of declarative infrastructure, while Pulumi offers a compelling, developer-friendly approach for highly dynamic and programmatic infrastructure creation.

## Deployment Steps

To run and verify the infrastructure provisioned by this repository, ensure you have configured your AWS credentials (`aws configure`) and installed the required CLI tools.

### Running Terraform
1. Navigate to the terraform directory: `cd terraform`
2. Initialize the project (downloads providers): `terraform init`
3. Preview the changes: `terraform plan`
4. Deploy the infrastructure: `terraform apply -auto-approve`
5. To clean up and avoid AWS charges: `terraform destroy -auto-approve`

### Running Pulumi
1. Navigate to the pulumi directory: `cd pulumi`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Preview the changes: `pulumi preview`
4. Deploy the infrastructure: `pulumi up --yes`
5. To clean up and avoid AWS charges: `pulumi destroy --yes`
