# DetectStackedBlocks
A python script that checks the position of every block against every other block to detect if they are stacked.

![example](https://github.com/user-attachments/assets/048d10ac-52a1-430b-9fb3-a9d4ba83f96e)

Only tested on TMNF maps, but I don't see why it wouldn't work on TMUF maps as well.

## Usage
Just drop a Challenge.Gbx file into the console and press enter.<br>
A list of all the stacked blocks will be printed into the console and written to a file.

## Dependencies
- [Python](https://www.python.org/) 3.7-3.11 (Should work on 3.12 if python-lzo installs for pygbx)
- [pygbx](https://github.com/donadigo/pygbx)
- [tqdm](https://github.com/tqdm/tqdm)
