from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hashear_contrasena(contrasena: str) -> str:
    return password_hash.hash(contrasena)


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    return password_hash.verify(contrasena, hash_guardado)
