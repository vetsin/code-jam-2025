# Password Manager

This project is a concept design for a password manager. But we bet people are getting tired of using passwords to keep track of their passwords---what a tiring tedious fad! Instead, we have developed a few other tools for the job:

| Input Method | Passcode | Extra Notes
| -- | -- | -- |
| Anagram | whether the anagram is correctly solved <!-- idk, didn't test this myself -->  |
| Binary | your given binary string |
| Guesser | whether the thing is correctly guessed <!-- idk, didn't test this myself --> |
| LongVideo | :) <!-- idk what this one does --> |
| Map | location to some meters of accuracy |
| Snake | the sequence of moves you have taken in the current game |
| Text | boring normal password :( |
| Typst | typst output (i.e. `$AA$`, `$\u{1D538}$`, and `$𝔸$` are the same passcode) | to make this functional, add the [`typst` binary](https://github.com/typst/typst?tab=readme-ov-file#installation) to your PATH. Passcodes should be reproducible within the same Typst version.

We developed with `uv`. To start our program, use `uv run src/main.py`.

See developer documentation at [CONTRIBUTING.md](./CONTRIBUTING.md).
