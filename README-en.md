<h1>T-TEA</h1>

<div>
  <img
    src="resources/images/tteahardware.jpg"
    alt="T-TEA physical structure"
    width="16%"
    align="left"
  >

  <h3>Interactive Floor Console for Exergames</h3>

  <p align="justify">
    Software for an Interactive Floor console developed initially with a focus on people with Autism Spectrum Disorder (ASD), but which also allows the creation of serious games for other audiences. The project was developed by PhD candidate André Bonetto Trindade and Gabriel Brunelli Pereira, under the supervision of Prof. Marcelo da Silva Hounsell (UDESC). The T-TEA project (Torre para crianças com Transtorno do Espectro Autista / Tower for children with Autism Spectrum Disorder) aims to assist sensory processing therapy through an interactive, mobile, and low-cost platform.
  </p>

  <p align="justify">
    The hardware consists of a conventional video projector, webcam, and computer. The webcam is a relatively inexpensive device and can be easily found, which can be seen as a positive factor for the adoption of the game in public institutions.
  </p>

  <p align="justify">
    Since the projector and computer are conventional equipment, institutions can use devices they already have available. In this way, by reusing equipment, the final cost of the T-TEA platform is significantly reduced.
  </p>

  <p align="justify">
    This equipment is installed on a physical structure that is simple to assemble and easy to transport.
  </p>
</div>

<br clear="all">

<h2>Games</h2>

<p align="justify">
  T-TEA features different serious games developed with therapeutic goals and aimed at stimulating different skills.
</p>

<div>
  <img
    src="resources/images/simulacao_kartea.png"
    alt="Kartea game simulation"
    width="30%"
    align="left"
  >

  <h3>Kartea</h3>

  <p align="justify">
    Its goal is to help develop multisensory integration by stimulating the player's concentration, attention, motor coordination, and laterality. Its mechanics place the player on a 3-lane road, putting them in control of a car through the lateral movement of their body.
  </p>

  <p align="justify">
    The player must move only laterally across the screen, capturing targets (stars) and avoiding obstacles (barriers) to score points and advance levels.
  </p>

</div>

<br clear="all">

## Development

### Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) >= 0.11.32
- Computer with x86-64 or ARM architecture.

### Installing uv

uv automatically downloads and manages the correct Python version and the project's dependencies.

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

### Running

From the project root, on any system:

```bash
uv run dev
```

This command downloads the correct Python version, creates the `.venv`, syncs dependencies, and starts T-TEA.

### Important

On first use, allow camera access in your system's privacy settings.

<br clear="all">

<h1 align="center">Credits</h1>
<p align="center">
  <a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/cd3acfdc-6d5a-45cf-a2aa-5259c1be0cb7" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/9b388bc5-bc1f-467a-a674-0ee4a239b9d4" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/e4517a7b-de3e-4c8d-baf9-2ea0326aa1e4" /></a>
</p>