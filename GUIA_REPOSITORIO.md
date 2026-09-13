# Guía paso a paso: crear y gestionar el repositorio del Team Challenge

Esta guía asume que **no has usado Git ni GitHub nunca en tu vida**. Vamos a ir despacio y sin dar nada por hecho. Sigue los pasos en orden.

> **Git** es un programa que se instala en tu ordenador y sirve para guardar el historial de cambios de un proyecto.
> **GitHub** es una página web donde se guarda una copia de ese proyecto "en la nube", para que todo el equipo pueda verla, descargarla y subir cambios.

---

## 0. Antes de empezar: ¿quién hace qué?

Solo **una persona del equipo** (normalmente el "Scrum Master" según el reparto de tareas) crea el repositorio. El resto del equipo lo clona (lo descarga) después. No hace falta que todo el mundo lea el paso 1 y 2 con el mismo detalle si no va a crear el repositorio, pero sí que lea a partir del paso 3.

---

## 1. Instalar Git en tu ordenador

Primero comprueba si ya lo tienes instalado. Abre una terminal:

- **Windows**: busca "PowerShell" o "cmd" en el menú de inicio y ábrelo.
- **Mac**: abre la app "Terminal" (está en Aplicaciones → Utilidades).
- **Linux**: seguramente ya sabes abrir una terminal.

Escribe esto y pulsa Enter:

```bash
git --version
```

- Si te sale algo como `git version 2.43.0`, ya lo tienes instalado. Salta al paso 2.
- Si te sale un error tipo "comando no encontrado", tienes que instalarlo:
  - **Windows**: descarga el instalador desde [git-scm.com/download/win](https://git-scm.com/download/win), ejecútalo y deja todas las opciones por defecto (dale a "Next" en todo). Al terminar, cierra y vuelve a abrir la terminal.
  - **Mac**: escribe `git --version` en la terminal; si no lo tienes, macOS te ofrecerá instalar las "Herramientas de línea de comandos" automáticamente. Acepta.
  - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install git`

Comprueba de nuevo con `git --version` que ya funciona.

### Configura tu nombre y email en Git (solo la primera vez)

Git necesita saber quién eres para firmar tus commits:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

Usa el mismo email que vayas a usar en GitHub.

---

## 2. Crear una cuenta en GitHub

Si no tienes cuenta:

1. Ve a [github.com](https://github.com).
2. Haz clic en "Sign up" (arriba a la derecha).
3. Rellena email, contraseña y nombre de usuario. Sigue los pasos que te pide (verificación de email, etc.).
4. Ya tienes cuenta. El plan gratuito es más que suficiente para este proyecto.

---

## 3. Crear el repositorio (solo lo hace una persona del equipo)

1. Entra en [github.com](https://github.com) con tu cuenta.
2. Arriba a la derecha, haz clic en el icono **"+"** y luego en **"New repository"**.
3. Rellena el formulario:
   - **Repository name**: por ejemplo `toolbox_ml` (sin espacios, con guiones bajos o guiones si hace falta).
   - **Description**: algo breve, por ejemplo "Team Challenge: toolbox de EDA en Python".
   - **Public / Private**: elige **Public** (el enunciado pide que el repositorio sea público).
   - **Add a README file**: puedes dejarlo **desmarcado**, porque vamos a subir nuestro propio README ya preparado.
   - **.gitignore** y **License**: déjalos en "None", ya llevamos nuestro propio `.gitignore`.
4. Haz clic en **"Create repository"**.

GitHub te llevará a una página con instrucciones ("...or push an existing repository from the command line"). Vamos a usar exactamente esa opción, porque ya tenemos el proyecto hecho en local.

### Añadir a tus compañeros como colaboradores

1. Dentro del repositorio, ve a **Settings** (pestaña de arriba, con el icono de un engranaje).
2. En el menú de la izquierda, haz clic en **Collaborators**.
3. Haz clic en **Add people**.
4. Escribe el nombre de usuario de GitHub (o el email) de cada compañero y confírmalo.
5. Cada compañero recibirá una invitación por email o una notificación en GitHub que debe aceptar.

### Proteger la rama `main`

Esto obliga a que los cambios pasen por una Pull Request revisada antes de entrar en `main`, en vez de subirse directamente:

1. Dentro del repositorio, ve a **Settings → Branches**.
2. En "Branch protection rules", haz clic en **Add branch protection rule** (o "Add rule").
3. En "Branch name pattern" escribe: `main`
4. Marca la casilla **"Require a pull request before merging"**.
5. Dentro de esa opción, marca también **"Require approvals"** y pon el número de aprobaciones a **1**.
6. Baja del todo y haz clic en **Create** (o "Save changes").

A partir de ahora, nadie (ni siquiera quien creó el repo) podrá subir cambios directamente a `main`: todo tiene que pasar por una Pull Request con al menos 1 aprobación.

---

## 4. Subir el proyecto ya preparado al repositorio (solo la primera vez)

Tienes en tu ordenador una carpeta con todo el proyecto ya montado (el paquete `toolbox_ml`, los tests, el notebook, el README, etc.). Vamos a subirla al repositorio vacío que acabas de crear en GitHub.

1. Abre una terminal y navega hasta la carpeta del proyecto. Por ejemplo:
   ```bash
   cd ruta/donde/descomprimiste/el/proyecto
   ```
2. Inicializa Git dentro de esa carpeta:
   ```bash
   git init
   ```
3. Añade todos los archivos al "área de preparación" (staging):
   ```bash
   git add .
   ```
4. Haz tu primer commit (una "foto" del estado actual del proyecto):
   ```bash
   git commit -m "feat: estructura inicial del paquete toolbox_ml"
   ```
5. Cambia el nombre de la rama principal a `main` (por si tu Git usa `master` por defecto):
   ```bash
   git branch -M main
   ```
6. Conecta tu carpeta local con el repositorio vacío de GitHub. Sustituye la URL por la de tu propio repositorio (la encuentras en la página del repo, botón verde **"Code"**):
   ```bash
   git remote add origin https://github.com/vuestro-usuario/toolbox_ml.git
   ```
7. Sube el proyecto:
   ```bash
   git push -u origin main
   ```

Te pedirá que inicies sesión en GitHub (la primera vez, es normal que se abra una ventana del navegador para autenticarte, o que te pida un "token" en vez de contraseña — sigue las instrucciones que te aparezcan en pantalla).

Recarga la página del repositorio en GitHub: deberías ver ya todos los archivos.

---

## 5. Clonar el repositorio (lo hace cada miembro del equipo)

Cada compañero, en su propio ordenador, debe descargarse una copia del repositorio:

1. En la página del repositorio en GitHub, haz clic en el botón verde **"Code"** y copia la URL (HTTPS).
2. En tu terminal, ve a la carpeta donde quieras guardar el proyecto y ejecuta:
   ```bash
   git clone https://github.com/vuestro-grupo/toolbox_ml.git
   cd toolbox_ml
   ```
3. Crea y activa un entorno virtual (recomendado, para no mezclar librerías con otros proyectos):
   ```bash
   python -m venv venv
   source venv/bin/activate       # Mac/Linux
   venv\Scripts\activate          # Windows (cmd)
   venv\Scripts\Activate.ps1      # Windows (PowerShell)
   ```
   Sabrás que está activado porque verás `(venv)` al principio de la línea de tu terminal.
4. Instala las dependencias y el paquete en modo editable:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
5. Comprueba que todo funciona ejecutando los tests:
   ```bash
   pytest tests/ -v
   ```
   Si ves todos los tests en verde (`PASSED`), ¡ya tienes el entorno listo para trabajar!

---

## 6. Flujo de trabajo diario: ramas, commits y Pull Requests

**Nunca trabajéis directamente sobre `main`.** El flujo es siempre: crear una rama → hacer cambios → subir la rama → abrir una Pull Request → que alguien la revise y apruebe → fusionarla ("mergear") en `main`.

### 6.1. Antes de empezar a trabajar cada día: actualiza tu `main` local

```bash
git checkout main
git pull origin main
```

Esto trae a tu ordenador los últimos cambios que haya subido el resto del equipo.

### 6.2. Crea tu rama de feature

Cada función/tarea tiene su propia rama, con el prefijo `feature/`. Por ejemplo, si vas a implementar `describe_df`:

```bash
git checkout -b feature/describe-df
```

Esto crea la rama y te cambia a ella automáticamente. Nombres de rama sugeridos según el reparto de tareas:
- `feature/describe-df`
- `feature/tipifica-variables`
- `feature/num-regression`
- `feature/cat-regression`
- `feature/bonus`

### 6.3. Trabaja y haz commits

Edita los archivos que necesites (por ejemplo, `toolbox_ml/eda/core.py` y `tests/test_core.py`). Cuando quieras guardar un avance:

```bash
git add .
git commit -m "feat: implementa describe_df con sus tests"
```

Usamos el formato **Conventional Commits**: el mensaje empieza por `feat:` (nueva funcionalidad), `fix:` (corrección de un error), `docs:` (cambios en documentación) o `test:` (cambios solo en tests). Puedes hacer varios commits pequeños mientras trabajas, no hace falta uno solo gigante al final.

### 6.4. Sube tu rama a GitHub

```bash
git push -u origin feature/describe-df
```

La primera vez que subes una rama nueva necesitas `-u origin nombre-de-la-rama`; las siguientes veces basta con `git push`.

### 6.5. Abre una Pull Request (PR)

1. Ve a la página del repositorio en GitHub. Normalmente te aparecerá un aviso amarillo "Compare & pull request" nada más subir la rama — haz clic ahí.
2. Si no te aparece, ve a la pestaña **"Pull requests"** → **"New pull request"**, elige tu rama como origen (`compare`) y `main` como destino (`base`).
3. Escribe un título y una breve descripción de lo que hace tu PR.
4. Haz clic en **"Create pull request"**.

### 6.6. Revisión (Code Review)

Pide a un compañero que revise tu PR:

1. En la pestaña **"Files changed"** de la PR puede leer el código y dejar comentarios línea a línea.
2. Si todo está bien, hace clic en **"Review changes" → "Approve"**.
3. Si hay algo que corregir, elige **"Request changes"** y explica qué falta. Tú corriges, haces `git push` de nuevo a la misma rama, y la PR se actualiza sola.

### 6.7. Fusionar (merge) la PR

Cuando la PR tiene al menos 1 aprobación:

1. En la propia página de la PR, haz clic en el botón **"Squash and merge"** (así todos los commits de la rama se juntan en uno solo y limpio dentro de `main`).
2. Confirma con **"Confirm squash and merge"**.
3. Te ofrecerá borrar la rama (`Delete branch`) — puedes hacerlo, ya no la necesitas.

### 6.8. Sincroniza tu `main` local

Vuelve a tu terminal y actualiza tu copia local:

```bash
git checkout main
git pull origin main
```

Y ya puedes crear tu siguiente rama de feature repitiendo el proceso desde el paso 6.2.

---

## 7. Comandos que vas a usar todo el rato (chuleta rápida)

| Comando | Para qué sirve |
|---|---|
| `git status` | Ver qué archivos has cambiado y en qué rama estás |
| `git checkout main` | Cambiar a la rama `main` |
| `git pull origin main` | Traer los últimos cambios de GitHub a tu ordenador |
| `git checkout -b feature/lo-que-sea` | Crear una rama nueva y cambiarte a ella |
| `git add .` | Marcar todos los archivos cambiados para el próximo commit |
| `git commit -m "mensaje"` | Guardar una "foto" de los cambios marcados |
| `git push` | Subir tus commits a GitHub |
| `git log --oneline` | Ver el historial de commits de forma resumida |

---

## 8. Problemas típicos y cómo resolverlos

**"error: failed to push some refs"** → alguien subió cambios a esa rama antes que tú. Ejecuta `git pull` y vuelve a intentar el `git push`.

**"Please tell me who you are"** → no has configurado tu nombre/email de Git. Repite los comandos `git config --global user.name` y `git config --global user.email` del paso 1.

**Se te olvidó en qué rama estabas** → ejecuta `git status`, te lo dice en la primera línea (`On branch ...`).

**Quieres deshacer cambios que aún no has subido (commit)** → `git checkout -- nombre_del_archivo` descarta los cambios de ese archivo desde el último commit.

**No sabes si `main` está protegido correctamente** → intenta hacer `git push origin main` directamente (sin PR); si está bien configurado, GitHub debería rechazarlo.

---

Con esto deberíais tener todo lo necesario para crear el repositorio, repartiros el trabajo en ramas, e ir fusionando el código del equipo de forma ordenada hasta la entrega.
