# Branch Protection Quick Setup

## Required Settings
Go to `Settings` -> `Branches` -> `Add rule` for `master`:

- [x] Require pull request before merging
- [x] Require 1 approval
- [x] Require status checks: `test (3.11)`, `test (3.12)`, `test-docker-build`
- [x] Require up-to-date branches

## Optional Settings
- [x] Include administrators
- [x] Allow squash merging only