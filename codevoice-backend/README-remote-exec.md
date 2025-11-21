# Remote Code Execution (Piston / Judge0)

This backend supports running code remotely with Piston, Judge0, JDoodle, or OneCompiler. Use this to avoid installing many compilers locally, and to run untrusted code in sandboxes.

## Options
- Piston: https://github.com/engineer-man/piston (self-hosted)
- Judge0 CE: https://github.com/judge0/judge0 (self-hosted or RapidAPI)
- JDoodle: https://www.jdoodle.com/compiler-api (cloud)
- OneCompiler: https://rapidapi.com/onecompiler-labs/api/onecompiler-apis (cloud via RapidAPI)

## Configure
Copy `.env.example` to `.env` and set one of:

- `EXEC_PROVIDER=piston`
- `EXEC_PROVIDER=judge0`

Alternatively set `USE_REMOTE_EXECUTION=true` (defaults to piston).

### Piston
- Public demo URL (rate-limited): `https://emkc.org/api/v2/piston/execute`
- Prefer self-hosting. Set `PISTON_URL` to your instance.
- Optional versions: `PISTON_VERSION` or per language `PISTON_VERSION_PYTHON=3.10`

### Judge0 via RapidAPI
- Set:
  - `JUDGE0_URL=https://judge0-ce.p.rapidapi.com`
  - `RAPIDAPI_KEY=<your_key>` (or `JUDGE0_RAPIDAPI_KEY`)
  - Optional: `RAPIDAPI_HOST=judge0-ce.p.rapidapi.com`

### Judge0 self-hosted
- Easiest: Docker. Follow Judge0 docs to run `judge0` and `judge0-api`.
- Default API base: `http://localhost:2358`
- Set in `.env`:
  - `EXEC_PROVIDER=judge0`
  - `JUDGE0_URL=http://localhost:2358`
- No RapidAPI headers are used for self-hosted URLs.

### JDoodle (cloud)
- Set in `.env`:
  - `EXEC_PROVIDER=jdoodle`
  - `JDOODLE_CLIENT_ID=<your_id>`
  - `JDOODLE_CLIENT_SECRET=<your_secret>`
  - Optional: `JDOODLE_LANGUAGE_<LANG>=<mappedName>` and `JDOODLE_VERSIONINDEX[_<LANG>]=<index>`
- JDoodle requires a valid language name (e.g., python3) and a versionIndex per language.

### OneCompiler via RapidAPI (cloud)
- Set in `.env`:
  - `EXEC_PROVIDER=onecompiler`
  - `ONECOMPILER_RAPIDAPI_KEY=<your_key>`
  - Optional: `ONECOMPILER_URL` (defaults to their RapidAPI endpoint), `ONECOMPILER_VERSION[_<LANG>]`, `ONECOMPILER_FILENAME[_<LANG>]`

## Test
- Start backend
- GET `http://localhost:8000/compile/providers` → should show the provider and languages
- POST `http://localhost:8000/compile/` with form-data `code`, `language`, `inputs` to execute code.

## Notes
- For production, always self-host to avoid rate limits and ensure data control.
- Add your own rate limiting and auth in front of these endpoints if exposed publicly.
