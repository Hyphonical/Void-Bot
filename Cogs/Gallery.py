import discord
from discord.ext import commands
import aiohttp
from datetime import datetime

GALLERY_URL = "https://gallery.voidtales.win/images.json"
BASE_URL = "https://gallery.voidtales.win"
PER_PAGE = 3  # Number of images per page

def make_gallery_embeds(images, page, per_page):
    """
    Creates a list of Discord embeds for the images on the current page.
    Each image gets its own embed with a thumbnail and a link to the gallery.
    """
    start = (page - 1) * per_page
    end = start + per_page
    page_images = images[start:end]
    embeds = []
    for img in page_images:
        img_id = img.get("id", "")
        # Construct the thumbnail URL based on the image ID
        thumb_url = f"{BASE_URL}/images/thumbs/{img_id}-200.webp"
        # Link to the gallery page for this image
        gallery_link = f"https://gallery.voidtales.win/#img-{img_id}"
        embed = discord.Embed(
            title=img.get("title", "Image"),
            description=f'by {img.get("author", "Unknown")}\n[Open in Gallery]({gallery_link})',
            color=0xA0D6B4,
        )
        # Add caption if available
        if img.get("caption"):
            embed.add_field(name="Caption", value=img["caption"], inline=False)
        # Set the thumbnail image
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=f"ID: {img_id}")
        embeds.append(embed)
    return embeds

class GalleryView(discord.ui.View):
    """
    Discord UI View for gallery navigation.
    Provides Previous and Next buttons to paginate through images.
    """
    def __init__(self, images, page=1, per_page=PER_PAGE):
        super().__init__(timeout=60)
        self.images = images
        self.page = page
        self.per_page = per_page
        self.max_page = (len(images) - 1) // per_page + 1
        self.update_buttons()

    def update_buttons(self):
        """
        Enable or disable navigation buttons depending on the current page.
        """
        self.children[0].disabled = self.page <= 1
        self.children[1].disabled = self.page >= self.max_page

    @discord.ui.button(label="⏮️ Previous", style=discord.ButtonStyle.primary, row=0)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Go to the previous page when the Previous button is clicked.
        """
        if self.page > 1:
            self.page -= 1
            self.update_buttons()
            embeds = make_gallery_embeds(self.images, self.page, self.per_page)
            await interaction.response.edit_message(embeds=embeds, view=self)

    @discord.ui.button(label="Next ⏭️", style=discord.ButtonStyle.primary, row=0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Go to the next page when the Next button is clicked.
        """
        if self.page < self.max_page:
            self.page += 1
            self.update_buttons()
            embeds = make_gallery_embeds(self.images, self.page, self.per_page)
            await interaction.response.edit_message(embeds=embeds, view=self)

class Gallery(commands.Cog):
    """
    Discord Cog for the gallery command.
    Fetches images from the gallery API, sorts them by date, and displays them with pagination.
    """
    def __init__(self, Bot: commands.Bot):
        self.Bot = Bot

    @commands.hybrid_command(
        name='gallery',
        description='Shows the latest images from the Void Tales Gallery',
        aliases=['images'],
    )
    async def gallery(self, ctx: commands.Context):
        """
        Command to show the latest images from the gallery.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(GALLERY_URL) as resp:
                images = await resp.json()
        # Sort images by ISO date string, newest first
        def parse_date(img):
            try:
                return datetime.fromisoformat(img.get("date", ""))
            except Exception:
                return datetime.min
        images.sort(key=parse_date, reverse=True)
        embeds = make_gallery_embeds(images, 1, PER_PAGE)
        view = GalleryView(images, 1, PER_PAGE)
        await ctx.send(embeds=embeds, view=view)

async def setup(Bot: commands.Bot):
    """
    Async setup function for this cog.
    """
    await Bot.add_cog(Gallery(Bot))