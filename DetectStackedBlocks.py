from pygbx import Gbx, GbxType
from tqdm import tqdm
import json
import os
import re


default_config = {
	"checkName": True,
	"checkRot": True,
	"checkFlags": True,
	"convertFlags": 2,
	"minimumStack": 2,
	"filterEnabled": True,

	"filterBlocks": [
		"StadiumWaterClip",
		"StadiumGrassClip",
		"StadiumDirtClip",
		"StadiumDirt",
		"StadiumDirtHill",
		"StadiumDirtBorder",
		"StadiumGrass",
		"StadiumPool",
		"StadiumWater"
	]
}


def create_config():
	with open(configName, 'w') as file:
		json.dump(default_config, file, indent=0)

def load_config():
	global checkName, checkRot, checkFlags, convertFlags, minimumStack, filterEnabled, filterBlocks, configInfo
	print(f"\033c{version} | {date} | By SuperKulPerson\n")
	
	if not os.path.exists(configName):
		print(f"\033[91mNo {configName} was found.")
		create_config()
		print("\033[92mCreated a new config.json file where this program was opened from.\033[0m\n")
	
	with open(configName, 'r') as file:
		config = json.load(file)
	
	checkName = config.get('checkName', True)
	checkRot = config.get('checkRot', True)
	checkFlags = config.get('checkFlags', True)
	convertFlags = config.get('convertFlags', 2)
	minimumStack = config.get('minimumStack', 2)
	
	filterEnabled = config.get('filterEnabled', True)
	filterBlocks = config.get('filterBlocks', [])
	
	configMinLen = 21 # Raise this number if a config is too long and it no longer aligns.
	
	configInfo = f"""\033[96m#-Config-#\033[0m
{align(f'checkName = {checkName}', configMinLen)} | Checks if the block names are equal. Does NOT ignore names from \"filterBlocks\" if false.
{align(f'checkRot = {checkRot}', configMinLen)} | Checks if the rotation of the blocks are equal.
{align(f'checkFlags = {checkFlags}', configMinLen)} | Checks if the flags are equal.
{align(f'convertFlags = {convertFlags}', configMinLen)} | 0 = Hex. 1 = TrackStudio vars. 2 = 2.0 Editor vars. Tries to show NO MOBIL / invis blocks.
{align(f'minimumStack = {minimumStack}', configMinLen)} | The minimum allowed size for a stack.
{align(f'filterEnabled = {filterEnabled}', configMinLen)} | Will use the filter if true.
\nfilterBlocks | Block names on this list will be skipped."""

	print(configInfo)
	
	if filterBlocks:
		for name in filterBlocks:
			print(f"- {name}")
	else:
		print("- None")
	
	print(f"""\n\n\033[96m#-Commands-#\033[0m
reload  | Reloads config.json.
default | Sets config.json to default and reloads it.
""")


def condition(curName, Name, curPos, Pos, curRot, Rot, curFlags, Flags):
	if curPos != Pos:
		return False
	if checkName and curName != Name:
		return False
	if checkRot and curRot != Rot:
		return False
	if checkFlags and curFlags != Flags:
		return False
	if filterEnabled:
		for ignore in filterBlocks:
			if ignore == curName:
				return False
	return True


def flag_to_var(flags): 
	if convertFlags == 2: # 2.0 Editor. Could use some work from someone who knows how to detect NO MOBIL blocks better. Otherwise, this needs a list of all the blocks and what vars they can be.
		variant = (flags % 0x40) + 1 			# 1-14 Are variants. 15-64 = NO MOBIL. 64 is what 2.0 uses when placing NO MOBIL.
		variation = (flags // 0x40 % 0x40) + 1 	# 1-6 Are variations. 7-63 = NO MOBIL. 64 = Clip.
		ground = "Ground" if (flags // 0x1000 % 0x2) else "Air"
		clip = " Clip" if (flags // 0x2000 % 0x2) else ""
		pillar = " Pillar" if (flags // 0x4000 % 0x2) else ""
		
		noMobil = ""
		if variant > 14 or 63 >= variation > 6 or (variation == 64 and not clip) or (clip and pillar):
			noMobil = f", \033[95mNO MOBIL\033[0m ({hex(flags).upper()})"
		
		return f"Variant: {variant}, Variation: {variation}, Type: {ground}{clip}{pillar}{noMobil}"
	
	elif convertFlags == 1: # TrackStudio vars
		return f"Vars: ({flags % 0x100}, {flags // 0x100 % 0x100}, {flags // 0x10000 % 0x100}, {flags // 0x1000000})"
	
	else: # Hex flags
		return f"Flags: {hex(flags).upper()}"


def find_stacked(challenge):
	i = 0
	output = []
	checkedBlocks = [] 	 # Keeps track of the stacked blocks to avoid repeating stacks
	stackAmountTotal = 0 # How many stacked blocks
	stackGroups = 0 	 # How many groups of stacks
	alignAmount = 7 + len(str(len(challenge.blocks)))
	with tqdm(total=len(challenge.blocks), colour="#00FF00", ascii=" ▌█", bar_format=("{desc}Blocks: {n}/{total} | {rate_fmt} | {percentage:1.0f}% |{bar}| {elapsed}"), desc=f"Stacked Blocks: {stackAmountTotal} | Groups: {stackGroups} | ") as pbar:
		while i < len(challenge.blocks):
			curBlock = challenge.blocks[i]
			curName = curBlock.name
			curPos = curBlock.position
			curtRot = curBlock.rotation
			curFlags = curBlock.flags
			stacks = []
			checkedBlocks = [block for block in checkedBlocks if block >= i] # Removes blocks from the list that are less than i.
			for index, block in enumerate(challenge.blocks):
				if i < index and i not in checkedBlocks: # Make sure i never searches for numbers under index.
					if condition(curName, block.name, curPos, block.position, curtRot, block.rotation, curFlags, block.flags):
						pos = block.position
						checkedBlocks.append(index)
						
						if not stacks:
							stacks.append(f"\n{align(f'Block {i}', alignAmount)}| Pos: {curPos.x, curPos.y, curPos.z} | Rot: {curtRot} | {flag_to_var(int(curFlags))} | Name: {curName}")
						
						stacks.append(f"{align(f'Block {index}', alignAmount)}| Pos: {pos.x, pos.y, pos.z} | Rot: {block.rotation} | {flag_to_var(int(block.flags))} | Name: {block.name}")
			stackAmount = len(stacks)
			if stacks and stackAmount >= minimumStack:
				stackGroups += 1
				stackAmountTotal += stackAmount
				for stack in stacks:
					output.append(stack)
				output.append(f"\033[90mSize: {stackAmount}\033[00m")
			i += 1
			pbar.set_description_str(f"Stacked Blocks: {stackAmountTotal} | Groups: {stackGroups} | ")
			pbar.update(1)
	return output, stackAmountTotal, stackGroups


def start():
	mapFile = input("\033[97mDrag and drop a \033[92mChallenge.Gbx\033[97m into this window and press enter:\033[0m ")
	if mapFile:
		if mapFile == "default":
			create_config()
			load_config()
			print("\033[92mSet config.json to default.\033[0m\n")
			start()
		elif mapFile == "reload":
			load_config()
			print("\033[92mReloaded config.json.\033[0m\n")
			start()
		for prefix, suffix in patterns:
			if mapFile.startswith(prefix) and mapFile.endswith(suffix): # Removes any symbols from file path.
				mapFile = mapFile[len(prefix):-len(suffix)]
		if os.path.exists(mapFile):
			try:
				challenge = Gbx(mapFile).get_class_by_id(GbxType.CHALLENGE)
				if not challenge:
					print("\033[91mNot a Challenge.Gbx file. Example of a correct file: \033[92mA01-Race.Challenge.Gbx\033[0m")
					start()
				print(f"Map Name: {challenge.map_name}\nFile: {mapFile}")
				
				stackedBlocks, stackAmountTotal, stackGroups = find_stacked(challenge)
				
				if stackedBlocks:
					for block in stackedBlocks:
						print(block)
					
					mapFileName = os.path.splitext(os.path.basename(mapFile))[0].split('.')[0]
					
					with open(f"{mapFileName}.txt", 'w') as file:
						try:
							file.write(f"Map Name: {challenge.map_name}\nMap File: {mapFile}\nBlocks Searched: ({len(challenge.blocks)})\n")
						except UnicodeEncodeError as e:
							file.write(f"Invalid character(s) in file/map name :( (UnicodeEncodeError: {e})\nBlocks Searched: ({len(challenge.blocks)})\n")
						for block in stackedBlocks:
							file.write(ansi_filter(f"{block}\n"))
						file.write(f"\nStacked Blocks: ({stackAmountTotal})\nStacked Groups: ({stackGroups})\n\n{ansi_filter(f'{configInfo}')}")
						if filterBlocks and filterEnabled:
							for name in filterBlocks:
								file.write(f"\n- {name}")
						else:
							file.write("\n- None")
					print(f"\nOutput file written to: {os.getcwd()}\\{mapFileName}.txt\n")
				else:
					print("No stacked blocks were found.")
				start()
			except Exception as e:
				print(f"\033[91mError processing file: {e}\033[0m")
				start()
		else:
			print(f"\033[91mFile ({mapFile}) not found. Please try again.\033[0m")
			start()
	else:
		start()


def ansi_filter(text): # Removes ANSI codes
	return re.compile(r'\033[c]|'r'\033\[[0-9;]*m').sub('', text)


def align(text, minLen): # Adds spaces to align text
	return text + (" " * (minLen - len(text)))


if __name__ == "__main__":
	
	version = "v1.0.1"
	date = "01.08.2024"
	
	configName = "config.json"
	
	load_config()
	
	patterns = [ # Symbols to remove from input
		("& '", "'"),	# For VSCode Console
		('"', '"'),		# For Powershell
		("'", "'")		# Just in case
	]
	
	start()
