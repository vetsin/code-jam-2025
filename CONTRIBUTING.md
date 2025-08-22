# Contributing

Follow the user instructions at [README.md](./README.md) to start the password manager.

Run `uvx pre-commit install` to install the `.pre-commit-config.yaml` lints.

Some general rules:

- Follow <https://www.conventionalcommits.org/en/v1.0.0/>.
- Make all edits to the main branch via pull requests (squash merge).
  - Feel free to approve your own PR for the sake of development speed.

## Project Layout

```
src/
├── main.py
└── password_manager/
    ├── app/
    ├── backend/
    ├── components/
    ├── types/
    └── util/
```

The layout for the frontend code takes inspiration from [bulletproof-react](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md). We have the `password_manager` library that exposes a few modules.

- `app/` is responsible for the `app.app()` that spawns the entire nicegui application, and is used for the very small `main.py`.
- `backend/` does backend stuff. It turns out the line between back and front end is much more blurred than we thought at first, for nicegui. Our design decisions reflect this.
- `components/` are generally any self-contained element that can be used elsewhere.
- `types/` provides important types used throughout the application.
- `util/` provides utility functions like `todo()`, which assists type checking during development.

> [!NOTE]
>
> `bulletproof-react` suggests making a distinction between components (truly generic things that can be used anywhere, like a file picker) and features (where each module in `password_manager/features/` namespaces feature-specific components that should only be used to implement that feature).
>
> In that paradigm, our `password_factories` module would be under a login feature instead of the generic components module. We can switch to this or something else if organization gets too crazy.
