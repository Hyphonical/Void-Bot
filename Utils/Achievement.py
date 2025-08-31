# 📦 Built-in modules
from pathlib import Path
import glob
import difflib

# 📥 Custom modules
from PIL.Image import Resampling
from PIL import ImageDraw, ImageFont, Image

# ⚙️ Settings
from Config import FuzzyMatchingThreshold


# 🌱 Function to generate Minecraft-style achievement image
def MakeAchievement(
	BaseImgPath: Path,
	IconName: str | None,
	Achievement: str,
	Description: str,
	Colors: list[tuple[int, int, int]],
	OutputPath: Path,
) -> None:
	"""Generate a Minecraft-style achievement image."""
	# 📏 Check if length exceeds limits
	if len(Achievement) > 20 or len(Description) > 20:
		raise ValueError('Achievement or Description is too long.')

	# 📂 Load the base achievement image
	Base = Image.open(BaseImgPath).convert('RGBA')

	# 📂 Load the icon and resize it to fit
	if IconName:
		IconDir = Path('Utils/Icons')
		IconFiles = glob.glob(str(IconDir / '*.png'))
		IconNames = [Path(f).stem for f in IconFiles]
		if IconName in IconNames:
			IconPath = IconDir / f'{IconName.capitalize()}.png'
			Icon = Image.open(IconPath).convert('RGBA')
			Icon = Icon.resize((29, 31), resample=Resampling.LANCZOS)
			Base.paste(Icon, (18, 16), Icon)  # Place icon with transparency
		else:
			# 🔍 Fuzzy search for closest match
			Closest = difflib.get_close_matches(
				IconName, IconNames, n=1, cutoff=FuzzyMatchingThreshold
			)
			if Closest:
				IconName = Closest[0]
				IconPath = IconDir / f'{IconName.capitalize()}.png'
				Icon = Image.open(IconPath).convert('RGBA')
				Icon = Icon.resize((29, 31), resample=Resampling.LANCZOS)
				Base.paste(Icon, (18, 16), Icon)  # Place icon with transparency
			else:
				raise ValueError(
					f'Invalid icon name: {IconName}. Available: {", ".join(IconNames)}'
				)

	# 📝 Load a Minecraft-style font
	Font = ImageFont.truetype('Utils/Minecraftia-Regular.ttf', 16)

	# ✏️ Draw text
	Draw = ImageDraw.Draw(Base)
	Draw.text((60, 10), Achievement, font=Font, fill=Colors[0])
	Draw.text((60, 32), Description, font=Font, fill=Colors[1])

	# 💾 Save result
	Base.save(OutputPath, 'PNG')
