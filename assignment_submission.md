# To-Do Assignment Submission

## Branch Evidence

```text
* dev
  feature/filters-sorting
  feature/quick-actions
  feature/search
  feature/task-descriptions
  main
  wip/full-assignment-implementation
  remotes/origin/HEAD -> origin/main
  remotes/origin/dev
  remotes/origin/feat/ci-gate-proof
  remotes/origin/feature/filters-sorting
  remotes/origin/feature/pagination-and-performance
  remotes/origin/feature/quick-actions
  remotes/origin/feature/search
  remotes/origin/feature/task-comments
  remotes/origin/feature/task-descriptions
  remotes/origin/feature/task-tags-labels
  remotes/origin/main
```

## Feature PRs Merged Into `dev`

- [PR #1](https://github.com/nv23086-abbas-alsaighal/to-do/pull/1) - feature/task-descriptions: adds description, priority, due date support, and UI/API plumbing.
- [PR #2](https://github.com/nv23086-abbas-alsaighal/to-do/pull/2) - feature/search: adds search by title/description with the `q` query parameter and UI search support.
- [PR #3](https://github.com/nv23086-abbas-alsaighal/to-do/pull/3) - feature/filters-sorting: adds filtering, sorting, and stats support for the task list.

## Release PR And Tag

- [PR #9](https://github.com/nv23086-abbas-alsaighal/to-do/pull/9) - dev merged into main for the release.
- [GitHub Release v0.1.0](https://github.com/nv23086-abbas-alsaighal/to-do/releases/tag/v0.1.0)
- Release notes list the three shipped features: task metadata, search, and filters/sorting.

## Container Verification

- Local build succeeded with `docker build -t todo-saas:0.1.0 .`.
- The release is versioned as `0.1.0`, matching the semantic versioning requirement for the first feature release.
- Registry push and screenshot evidence should be attached from the target DockerHub or ECR account used for submission.

## What I Learned

Branching by feature kept each change focused and made review much easier because the search, metadata, and filtering work could be merged independently. The `dev` integration branch gave a safe place to combine features before promoting them to `main`, and the release tag tied the container image version directly to the Git history. Using a consistent SemVer release also made the Docker build and GitHub release process straightforward to verify.
