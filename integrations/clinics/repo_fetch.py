#!/usr/bin/env python3
"""
repo_fetch — traer el código de un producto desde su repo privado a un workdir LOCAL, headless.

Xe orquesta los productos donde viven ([[DEC-010]]): no los copia a xe-mind, los CLONA a un workdir
temporal y usa ese path como `CLINICS_REPO` (la ruta local que espera integrations/clinics).

Auth:
  - En la VPS: `GITHUB_PAT` (scope `repo`, solo lectura) por env → se inyecta en la URL SOLO para el
    clone y se BORRA del remote después (no persiste en .git/config). El PAT nunca se imprime (se enmascara).
  - Local/pruebas: sin PAT → usa las credenciales de git/gh ya configuradas (para clonar el privado).

Uso:
  python3 repo_fetch.py dry-run  --repo https://github.com/Sad1mus/agente-clinicas
  python3 repo_fetch.py clone    --repo <url> --dest <dir> [--branch <b>]     # clone real
  python3 repo_fetch.py oracle
"""
import argparse, os, re, subprocess, sys, tempfile, shutil


def masked_url(repo_url: str, has_pat: bool) -> str:
    """URL segura para imprimir: si hay PAT, oculta cualquier credencial."""
    u = re.sub(r"https://[^@/]+@", "https://***@", repo_url)
    return re.sub(r"^https://github\.com", "https://***@github.com" if has_pat else "https://github.com", u) \
        if has_pat and "@" not in repo_url else u


def _clone_url(repo_url: str, pat: str | None) -> str:
    """URL real para el clone (con token si hay PAT). NUNCA imprimir el resultado."""
    if pat and repo_url.startswith("https://github.com/"):
        return repo_url.replace("https://github.com/", f"https://x-access-token:{pat}@github.com/")
    return repo_url


def clone(repo_url: str, dest: str, pat: str | None = None, branch: str | None = None) -> str:
    """Clona --depth 1 a `dest`. Devuelve dest. Borra el token del remote tras clonar."""
    if os.path.exists(dest):
        shutil.rmtree(dest)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd += ["-b", branch]
    cmd += [_clone_url(repo_url, pat), dest]
    # No imprimir cmd (lleva el token). Solo la versión enmascarada:
    print(f"[repo_fetch] git clone --depth 1 {('-b '+branch+' ') if branch else ''}{masked_url(repo_url, bool(pat))} {dest}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        # Sanear stderr por si git ecoa la URL con token
        err = re.sub(r"x-access-token:[^@]+@", "x-access-token:***@", r.stderr)
        raise RuntimeError(f"clone falló ({r.returncode}): {err.strip()[:300]}")
    if pat:
        # el token NO debe persistir en .git/config → dejar el remote limpio
        subprocess.run(["git", "-C", dest, "remote", "set-url", "origin", repo_url], check=False)
    return dest


def dry_run(repo_url: str, dest: str, branch: str | None):
    has_pat = bool(os.environ.get("GITHUB_PAT"))
    print(f"[dry-run] traería el producto a un workdir temporal, SIN ejecutar:")
    print(f"   git clone --depth 1 {('-b '+branch+' ') if branch else ''}{masked_url(repo_url, has_pat)} {dest}")
    print(f"   → ese dir sería CLINICS_REPO (ruta local que espera integrations/clinics)")
    print(f"   auth: {'GITHUB_PAT (enmascarado)' if has_pat else 'credenciales git/gh locales (sin PAT)'}")
    print("[execute] el clone real corre con `clone`; el PAT nunca se imprime ni persiste en .git/config.")


def oracle():
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond: ok = False
        print(f"   [{'ok' if cond else 'FALLA'}] {name}")

    url = "https://github.com/Sad1mus/agente-clinicas"
    # 1. sin PAT, la URL de clone es la limpia
    check("sin PAT → clone url = url limpia", _clone_url(url, None) == url)
    # 2. con PAT, la URL de clone lleva el token...
    withtok = _clone_url(url, "SECRETO123")
    check("con PAT → clone url inyecta el token", "x-access-token:SECRETO123@github.com" in withtok)
    # 3. ...pero la URL enmascarada NUNCA muestra el token
    check("masked_url oculta el token", "SECRETO123" not in masked_url(withtok, True) and "***@" in masked_url(withtok, True))
    # 4. masked_url de una url ya-con-credencial también enmascara
    check("masked_url enmascara credencial embebida", "SECRETO123" not in masked_url("https://x-access-token:SECRETO123@github.com/x", True))
    print("ORACLE:", "PASA" if ok else "FALLA")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run", "clone"])
    ap.add_argument("--repo", help="URL del repo del producto")
    ap.add_argument("--dest", help="workdir destino (temporal; NUNCA dentro de xe-mind)")
    ap.add_argument("--branch")
    a = ap.parse_args()
    pat = os.environ.get("GITHUB_PAT")  # nunca se imprime
    if a.accion == "oracle":
        oracle()
    elif a.accion == "dry-run":
        dry_run(a.repo or "https://github.com/Sad1mus/agente-clinicas",
                a.dest or "/tmp/clinics-checkout", a.branch)
    elif a.accion == "clone":
        if not a.repo or not a.dest:
            print("clone exige --repo y --dest"); sys.exit(1)
        path = clone(a.repo, a.dest, pat, a.branch)
        print(f"[repo_fetch] checkout listo en {path}")
