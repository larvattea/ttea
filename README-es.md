<h1>T-TEA</h1>

<div>
  <img
    src="resources/images/tteahardware.jpg"
    alt="Estructura física del T-TEA"
    width="16%"
    align="left"
  >

  <h3>Consola para Exergames de Suelo Interactivo</h3>

  <p align="justify">
    Software para una consola de Suelo Interactivo desarrollada inicialmente con foco en el público con Trastorno del Espectro Autista (TEA), pero que también permite la creación de juegos serios destinados a otros públicos. El proyecto fue desarrollado por el doctorando André Bonetto Trindade y Gabriel Brunelli Pereira, bajo la orientación del Prof. Marcelo da Silva Hounsell (UDESC). El proyecto Torre para niños con Trastorno del Espectro Autista (T-TEA) tiene como objetivo ayudar en la terapia del procesamiento sensorial a través de una plataforma interactiva, móvil y de bajo costo.
  </p>

  <p align="justify">
    El hardware está compuesto por un proyector de video, cámara web y computadora convencionales. La cámara web es un dispositivo relativamente económico y puede encontrarse con facilidad, lo cual puede verse como un factor positivo para la adopción del juego en instituciones públicas.
  </p>

  <p align="justify">
    Dado que el proyector y la computadora son convencionales, se pueden utilizar los que ya están disponibles en las instituciones. De esta forma, al reutilizar equipos, el costo final de la plataforma T-TEA se reduce significativamente.
  </p>

  <p align="justify">
    Estos equipos se instalan en una estructura física de montaje simple y de fácil portabilidad.
  </p>
</div>

<br clear="all">

<h2>Juegos</h2>

<p align="justify">
  T-TEA cuenta con diferentes juegos serios desarrollados con objetivos terapéuticos y de estímulo de distintas habilidades.
</p>

<div>
  <img
    src="resources/images/simulacao_kartea.png"
    alt="Simulación del juego Kartea"
    width="30%"
    align="left"
  >

  <h3>Kartea</h3>

  <p align="justify">
    Su objetivo es ayudar en el desarrollo de la integración multisensorial, a través de la estimulación de la concentración, atención, coordinación motora y lateralidad del jugador. Su mecánica ambienta al jugador en una carretera con 3 carriles, y lo coloca al control de un auto mediante el movimiento lateral de su cuerpo.
  </p>

  <p align="justify">
    El jugador debe moverse solo lateralmente por la pantalla, capturando objetivos (estrellas) y esquivando obstáculos (barreras) para sumar puntos y avanzar de nivel.
  </p>

</div>

<br clear="all">

## Desarrollo

### Requisitos

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) >= 0.11.32
- Computadora con arquitectura x86-64 o ARM.

### Instalar uv

uv descarga y gestiona automáticamente la versión correcta de Python y las dependencias del proyecto.

macOS:

```bash
brew install uv
```

Windows (PowerShell):

```powershell
winget install --id=astral-sh.uv -e
```

Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Ejecutar

En la raíz del proyecto, en cualquier sistema:

```bash
uv run dev
```

Este comando descarga la versión correcta de Python, crea el `.venv`, sincroniza las dependencias e inicia T-TEA.

### Importante

En el primer uso, permita el acceso a la cámara en la configuración de privacidad del sistema.

<br clear="all">

<h1 align="center">Realización</h1>
<p align="center">
  <a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/cd3acfdc-6d5a-45cf-a2aa-5259c1be0cb7" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/9b388bc5-bc1f-467a-a674-0ee4a239b9d4" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/e4517a7b-de3e-4c8d-baf9-2ea0326aa1e4" /></a>
</p>