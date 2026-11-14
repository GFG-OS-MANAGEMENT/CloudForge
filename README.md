# ☁️ CloudForge

### Simplifying Cloud Infrastructure Management Through Automation

CloudForge is an open-source cloud infrastructure automation platform designed to help users provision, configure, monitor, and destroy cloud resources through a simplified and centralized interface.

The goal is to make cloud infrastructure management more accessible, efficient, and beginner-friendly by reducing manual configuration and automating repetitive cloud operations.

---

## 🚀 About the Project

Managing cloud infrastructure often involves multiple tools, complex configurations, and repetitive manual tasks.

**CloudForge aims to simplify this process.**

It provides a unified platform where users can manage the complete lifecycle of cloud infrastructure — from initial provisioning to monitoring and resource cleanup.

Whether you're a beginner exploring cloud computing or a developer managing cloud resources, CloudForge aims to make infrastructure management easier to understand and operate.

---

## 🎯 Project Objectives

* Automate cloud infrastructure provisioning.
* Simplify configuration and management of cloud resources.
* Provide centralized infrastructure monitoring.
* Enable users to destroy resources when they are no longer needed.
* Reduce manual intervention and configuration complexity.
* Encourage open-source collaboration and learning in cloud development.

---

## ✨ Key Features

| Feature                        | Description                                                           |
| ------------------------------ | --------------------------------------------------------------------- |
| ☁️ Infrastructure Provisioning | Automatically create cloud resources based on user configurations.    |
| ⚙️ Configuration Management    | Configure infrastructure through simplified workflows.                |
| 📊 Monitoring                  | Track infrastructure status and resource information.                 |
| 🗑️ Resource Destruction       | Safely remove provisioned resources when they are no longer required. |
| 🔄 Automation                  | Reduce repetitive manual cloud operations.                            |
| 🌍 Open Source                 | Encourage contributions, collaboration, and community learning.       |

*Note: Features will be implemented progressively as the project develops.*

---

## 🚦 Quick Start

### Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/Scripts/activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn backend.app.main:app --reload
```

Open <http://localhost:8000> for the dashboard and <http://localhost:8000/docs> for the
interactive API reference.

CloudForge runs in **dry-run mode** by default, so provisioning and destruction are simulated
until you explicitly set `CLOUDFORGE_DRY_RUN=false`.

### Run with Docker

```bash
docker compose up --build
```

### Run the checks

```bash
pytest
ruff check .
```

### API overview

| Method | Endpoint                        | Description                              |
| ------ | ------------------------------- | ---------------------------------------- |
| GET    | `/api/health`                   | Service status and safety mode           |
| GET    | `/api/resources`                | List tracked resources                   |
| POST   | `/api/resources`                | Provision a resource                     |
| GET    | `/api/resources/{id}`           | Resource details                         |
| POST   | `/api/resources/{id}/destroy`   | Destroy a resource after name confirmation |
| GET    | `/api/metrics/summary`          | Status counts and per-resource uptime    |

Safety defaults:

* Every resource consumes a slot in `CLOUDFORGE_MAX_RESOURCES` to bound accidental spend.
* Set `CLOUDFORGE_API_KEY` to require an `X-API-Key` header on mutating requests.
* Destruction requires sending the exact resource name as `confirm_name`.

### Terraform demo module

The included module writes a local JSON manifest instead of creating billable cloud
resources, so you can try the full workflow without an account:

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform apply
```

---

## 🏗️ Proposed Architecture

CloudForge will follow a modular architecture to keep the platform maintainable and extensible.

```text
             USER
               |
               v
        +---------------+
        |  User Interface|
        +---------------+
               |
               v
        +---------------+
        |   Backend API  |
        +---------------+
               |
               v
        +---------------+
        | Automation Layer|
        +---------------+
               |
        +-------+-------+
        |               |
        v               v
 +-------------+  +-------------+
 | Provisioning|  | Configuration|
 |   Engine    |  |    Engine    |
 +-------------+  +-------------+
        |               |
        +-------+-------+
                |
                v
       +------------------+
       |  Cloud Provider  |
       +------------------+
                |
                v
       +------------------+
       | Monitoring Layer |
       +------------------+
```

---

## 🛠️ Proposed Technology Stack

The technology stack will be finalized during development.

| Component              | Proposed Technology |
| ---------------------- | ------------------- |
| Backend                | Python / FastAPI    |
| Infrastructure as Code | Terraform           |
| Cloud Platform         | AWS                 |
| Containerization       | Docker              |
| Version Control        | Git & GitHub        |
| CI/CD                  | GitHub Actions      |
| Monitoring             | CloudWatch          |
| Documentation          | Markdown            |

The project will prioritize modularity, simplicity, and technologies that are suitable for learning and extending.

---

## 📂 Project Structure

```text
CloudForge/
│
├── backend/
│   ├── app/
│   │   ├── api/                  # REST endpoints
│   │   ├── services/             # Terraform runner, resource lifecycle
│   │   ├── static/               # Dashboard (HTML/CSS/JS, no build step)
│   │   ├── config.py             # Environment-based settings
│   │   ├── models.py             # Request/response schemas
│   │   ├── store.py              # In-memory resource registry
│   │   └── main.py               # Application factory
│   └── tests/
│
├── infrastructure/
│   └── terraform/
│       ├── modules/local_demo/   # Safe, offline demo module
│       └── environments/dev/
│
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

---


---

## 🗺️ Development Roadmap

CloudForge will be developed incrementally, with a focus on building a working foundation before expanding functionality.

* [x] **Phase 1: Project Foundation**

  * Repository setup
  * Define architecture
  * Configure development environment
  * Initial documentation

* [ ] **Phase 2: Cloud Integration**

  * Integrate with a cloud provider
  * Configure authentication securely
  * Establish resource management workflows

* [ ] **Phase 3: Infrastructure Provisioning**

  * Implement automated provisioning
  * Integrate Terraform
  * Support configurable infrastructure

* [ ] **Phase 4: Monitoring & Management**

  * Track resource status
  * Implement monitoring functionality
  * Provide infrastructure insights

* [ ] **Phase 5: Resource Lifecycle Management**

  * Implement resource destruction
  * Add validation and error handling
  * Introduce safeguards against accidental deletion

* [ ] **Phase 6: Testing & Documentation**

  * Unit and integration testing
  * CI/CD integration
  * Developer documentation
  * Community contributions

---

## 🔐 Security Considerations

CloudForge will prioritize secure infrastructure management.

* Never commit cloud credentials or secret keys.
* Use environment variables for sensitive configurations.
* Follow the principle of least privilege.
* Validate infrastructure configurations before deployment.
* Include safeguards for destructive operations.
* Encourage testing in controlled environments.

**Important:** Provisioning cloud resources may incur charges. Always review configurations and estimated costs before deployment.

---

## 🤝 Contributing

CloudForge is an open-source project, and contributions are welcome!

Whether you're a beginner learning cloud computing or an experienced developer, you can contribute through:

* Reporting bugs
* Suggesting new features
* Improving documentation
* Submitting pull requests
* Reviewing code
* Helping improve the architecture

### Contribution Guidelines

1. Fork the repository.
2. Create a new feature branch.
3. Make your changes.
4. Test your implementation.
5. Submit a pull request with a clear description.

```bash
git checkout -b feature/your-feature-name
git add .
git commit -m "Add: description of feature"
git push origin feature/your-feature-name
```

Please follow the project's contribution guidelines before submitting changes.

---

## 👩‍💻 Project Leadership

**Project Name:** CloudForge
**Project Type:** Open Source | Cloud Development | Infrastructure Automation
**Project Lead:** Avika Singh

As the project lead, my goal is to build CloudForge as a practical learning and development initiative focused on cloud automation, infrastructure management, and collaborative open-source development.

This project is also an opportunity to explore real-world cloud development practices, understand infrastructure automation, and build something useful for the developer community.

---

## 📌 Current Status

<code>🚧 Under Development</code>

CloudForge is in its initial development phase. The architecture, features, and implementation will evolve through continuous development and community contributions.

A working foundation is now in place: a FastAPI backend, a safe local Terraform module, an
interactive dashboard, automated tests, and CI. Real AWS provisioning is the next milestone.

---

## 📄 License

This project is intended to be open source. The license will be finalized before the first public release.

---

### ⭐ Support the Project

If you find CloudForge interesting, consider starring the repository and contributing to its development.

**Let's make cloud infrastructure management simpler, smarter, and more accessible — one deployment at a time.**

☁️ **Build. Deploy. Monitor. Destroy. Repeat.**
