### Python Reverse Shell

Example of a HTTPS reverse shell made in Python. There is two files. A server file meant to open a server on the attacker machine and a client file meant to be run on the target machine.

### Commands and features

I added one `download` command to the shell as a PoC.
It could be a good base to build a Python reverse shell with multiple commands and features even though Python is not a good choice for the client side payload.

### Windows Defender

There is a short staging function meant to add `C:` to the exclusion path of Windows Defender and then download the malware to put it under a disguise name in the startup folder for persistence. So it is possible to split the code in two different files, a staging payload, and the reverse shell itself.
