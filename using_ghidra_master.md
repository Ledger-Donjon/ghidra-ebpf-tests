<!--
SPDX-FileCopyrightText: 2025 LEDGER SAS

SPDX-License-Identifier: MIT
-->

# Using Ghidra's master branch

It is useful to use the current `master` branch of Ghidra, for example to test some bug fixes in the way eBPF is supported.

To do so, here are some instructions.

1. Download the git repository:

```sh
git clone https://github.com/NationalSecurityAgency/ghidra
```

2. Install the build dependencies.
  For example in a container using [`docker.io/library/debian:13-slim`](https://hub.docker.com/_/debian):

```sh
apt-get update
apt-get install --no-install-recommends --no-install-suggests -y \
    ca-certificates \
    curl \
    file \
    gcc \
    git \
    g++ \
    make \
    patch \
    python3 \
    python3-pip \
    python3-venv \
    python3-wheel \
    unzip \
    libfontconfig1 \
    libfreetype6 \
    libgtk-3-0 \
    libx11-6 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    openjdk-25-jdk

(cd /opt && \
    curl -sSL --output gradle.zip https://services.gradle.org/distributions/gradle-9.4.1-bin.zip && \
    echo '2ab2958f2a1e51120c326cad6f385153bb11ee93b3c216c5fccebfdfbb7ec6cb  gradle.zip' | sha256sum -c && \
    unzip gradle.zip && \
    rm gradle.zip ) && \
    export PATH="/opt/gradle-9.4.1/bin:$PATH"

# Ensure Gradle runs with an UTF-8 locale (select one from "locale -a")
# If Gradle failed to unzip a jar file with unicode characters, define the local and stop the Gradle server: gradle --stop
export LANG=C.utf8

gradle -I gradle/support/fetchDependencies.gradle
```

3. Build Ghidra using Gradle:

```sh
gradle assembleAll

# Or to build the full package:
gradle buildGhidra
```

4. Run Ghidra:

```sh
# Replace 12.1_DEV with the right version which was built
./build/dist/ghidra_12.1_DEV/support/launch.sh fg jdk Ghidra 2G "" ghidra.GhidraRun
```

5. Install PyGhidra and run it:

```sh
export GHIDRA_INSTALL_DIR="$(pwd)/build/dist/ghidra_12.1_DEV"
echo y | "${GHIDRA_INSTALL_DIR}/support/pyghidraRun"

~/.config/ghidra/ghidra_12.1_DEV/venv/bin/python3 -m pyghidra
```
