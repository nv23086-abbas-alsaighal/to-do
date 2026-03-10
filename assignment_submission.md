# GitHub Actions CI/CD Pipeline - Submission

## Part A - CI Workflow

### CI Workflow File

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r app/requirements.txt
          pip install pytest flake8

      - name: Run lint
        run: |
          flake8 app tests scripts --exclude=.venv,__pycache__,app/.venv --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run tests
        run: pytest tests -v
```

### Evidence

- [ ] Screenshot: successful CI run (green check)
- [ ] Screenshot: failed CI run (then fixed)

## Part B - CD Workflow

### CD Workflow File

```yaml
name: CD

on:
  release:
    types: [published]

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract version from release tag
        id: version
        run: |
          TAG_NAME="${{ github.event.release.tag_name }}"
          VERSION="${TAG_NAME#v}"
          echo "version=${VERSION}" >> "$GITHUB_OUTPUT"

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/to-do:${{ steps.version.outputs.version }}
            ${{ secrets.DOCKERHUB_USERNAME }}/to-do:latest
```

### Evidence

- [ ] Screenshot: successful CD run
- [ ] Screenshot: DockerHub/ECR image tag

## Part C - End-to-End Flow

### 3-5 Sentence Flow Description

I made a small change on the dev branch and pushed it to GitHub. This triggered the CI workflow, which ran flake8 linting and pytest tests automatically and passed. I then opened a pull request from dev to main, merged it after CI succeeded, and created a new GitHub Release with a v-prefixed tag. Publishing the release triggered the CD workflow, which built the Docker image and pushed both the version tag and latest tag to DockerHub. Finally, I verified the new image tag in the container registry.

### Evidence

- [ ] Screenshot: GitHub Release page showing new version
- [ ] Screenshot: Registry showing the pushed image tag

## Reflection

Using GitHub Actions made the project workflow more reliable and faster because testing and linting now run on every push and pull request. It also reduced manual errors in container publishing by tying Docker image builds to release events. The secrets system kept credentials safe and out of source control, which is critical for real projects. I also learned how important consistent tagging is, since release tags directly control image version tags in CD.

## Secret Names Used

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

No secret values are included in this document.
