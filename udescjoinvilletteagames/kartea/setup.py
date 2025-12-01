from cx_Freeze import Executable, setup

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "include_files": [
        "Assets/",
        "Jogadores/",
        "calibracao.csv",
        "Kartea Fases/",
    ],
    "packages": [],
}

setup(
    name="T-TEA",
    version="2.0",
    description="T-TEA",
    download_url="https://udescmove2learn.wordpress.com/2023/06/26/t-tea/",
    options={"build_exe": build_exe_options},
    executables=[Executable("TTEA_menu.py")],
)
