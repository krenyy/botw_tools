# botw_tools

### A set of CLI tools for Breath of the Wild modding

* `yaz0`: De/compress a file with Yaz-0
* `aamp`: Convert between AAMP and YML
* `byml`: Convert between BYML and YML
* `sarc`: Manipulate SARC archives
* `actorinfo`: Manipulate ActorInfo file

All commands can read from stdin and write to stdout, either automatically or by explicitly using the pipe (`-`) character instead of file path.

To see how to use these commands, please refer either to `command --help` (ex. `aamp --help`) or the examples below.

###Examples:
**AAMP:**
```shell script
# View a AAMP file
aamp DgnObj_EntranceElevatorSP.bphysics

# Save as YML
aamp DgnObj_EntranceElevatorSP.bphysics \!!  # Saves as 'DgnObj_EntranceElevatorSP.physics.yml'
# or
aamp DgnObj_EntranceElevatorSP.bphysics test.yml
```
**Yaz0 and BYML:**
```shell script
# View a BYML file

# First variant
yaz0 ActorInfo.product.sbyml | byml

# Second variant
yaz0 ActorInfo.product.sbyml ActorInfo.product.byml
byml ActorInfo.product.byml


# Save as YML

# First variant
yaz0 ActorInfo.product.sbyml | byml - ActorInfo.product.yml

# Second variant
yaz0 ActorInfo.product.sbyml ActorInfo.product.byml
byml ActorInfo.product.byml \!!  # Saves as 'ActorInfo.product.yml'
# or
byml ActorInfo.product.byml actorinfo.yml
```
**Yaz0 and SARC:**

Decompress and extract a SARC archive `DgnObj_EntranceElevatorSP.sbactorpack` to `elevator` folder:
```shell script
# First variant
yaz0 DgnObj_EntranceElevatorSP.sbactorpack | sarc e(x)tract - elevator

# Second variant
yaz0 DgnObj_EntranceElevatorSP.sbactorpack \!!
sarc x DgnObj_EntranceElevatorSP.bactorpack elevator
```
Remove all files inside SARC:
```shell script
# First variant
yaz0 DgnObj_EntranceElevatorSP.sbactorpack | sarc (r)emove - \* | yaz0 - Empty.sbactorpack

# Second variant
yaz0 DgnObj_EntranceElevatorSP.sbactorpack DgnObj_EntranceElevatorSP.bactorpack
sarc r DgnObj_EntranceElevatorSP.bactorpack \*
yaz0 DgnObj_EntranceElevatorSP.bactorpack Empty.sbactorpack
```

**ActorInfo:**
```shell script
# Get an entry
actorinfo ActorInfo.product.(s)byml (g)et DgnObj_EntranceElevatorSP

# Duplicate an entry
actorinfo ActorInfo.product.(s)byml (d)uplicate DgnObj_EntranceElevatorSP MyCustomEntranceElevator

# Change entry keys
actorinfo ActorInfo.product.(s)byml (e)dit MyCustomEntranceElevator bfres MyCustomEntranceElevatorBfres

# Get the new entry
actorinfo ActorInfo.product.(s)byml g MyCustomEntranceElevator
```
