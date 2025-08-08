# Password Manager

## Project Layout

### Code

```
src/
├── main.py
└── password_manager/
    ├── app/
    └── components/
```

The layout for the frontend code takes inspiration from [bulletproof-react](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md). We have the `password_manager` library that exposes an app and some components.

`app.app()` spawns the entire nicegui application, and is used for the very small `main.py`. The components are generally any self-contained element that can be used elsewhere.

> [!NOTE]
>
> `bulletproof-react` suggests making a distinction between components (truly generic things that can be used anywhere, like a file picker) and features (where each module in `password_manager/features/` namespaces feature-specific components that should only be used to implement that feature).
>
> In that paradigm, our `password_factories` module would be under a login feature instead of the generic components module. We can switch to this or something else if organization gets too crazy.

## Contributing

This project can be developed with `uv`. Main entrypoint is `uv run src/main.py`.

Run `uvx pre-commit install` to install the `.pre-commit-config.yaml` lints.
