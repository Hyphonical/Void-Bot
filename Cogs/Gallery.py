import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime

GALLERY_URL = "https://gallery.voidtales.win/images.json"
BASE_URL = "https://gallery.voidtales.win"
PER_PAGE = 3  # Number of images displayed per page

def make_gallery_embeds(images, page, per_page):
    """
    Creates a list of Discord embeds for the images on the current page.
    Each image gets its own embed with a thumbnail and a link to the gallery.
    """
    start = (page - 1) * per_page
    end = start + per_page
    page_images = images[start:end]
    embeds = []

    max_page = (len(images) - 1) // per_page + 1
    # Header embed showing the current page and total pages
    header_embed = discord.Embed(
        title=f"🖼️ VoidTales Gallery Page {page}/{max_page}",
        color=0xA0D6B4
    )
    embeds.append(header_embed)

    for img in page_images:
        img_id = img.get("id", "")
        # Construct the thumbnail URL based on the image ID
        thumb_url = f"{BASE_URL}/images/thumbs/{img_id}-200.webp"
        # Link to the gallery page for this image
        gallery_link = f"{BASE_URL}/#img-{img_id}"
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

    async def get_images(self):
        """
        Fetches the images from the gallery API.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(GALLERY_URL) as resp:
                return await resp.json()

    async def get_authors(self):
        """
        Returns a sorted list of unique authors from the gallery images.
        """
        images = await self.get_images()
        return sorted(set(img.get("author", "Unknown") for img in images if img.get("author")))

    @commands.hybrid_command(
        name="gallery",
        description="Shows images from the Void Tales Gallery",
        aliases=["images"]
    )
    @app_commands.describe(
        page_or_author="Page number or author name (optional)",
        author="Filter images by author name (optional, for slash command only)"
    )
    async def gallery(self, ctx: commands.Context, page_or_author: str = None, author: str = None):
        """
        Usage:
        !gallery                   -> first page, all authors
        !gallery 2                 -> page 2, all authors
        !gallery hyphonical        -> first page, only author 'hyphonical'
        !gallery 2 hyphonical      -> page 2, only author 'hyphonical'
        !gallery hyphonical 2      -> page 2, only author 'hyphonical'
        """
        images = await self.get_images()

        # Sort images by ISO date string, newest first
        def parse_date(img):
            try:
                return datetime.fromisoformat(img.get("date", ""))
            except Exception:
                return datetime.min

        images.sort(key=parse_date, reverse=True)

        # --- Robust argument parsing for both prefix and slash commands ---
        page = 1
        author_arg = None

        # Gather all provided arguments
        args = []
        if page_or_author:
            args.append(str(page_or_author))
        if author:
            args.append(str(author))

        # Parse arguments: first non-digit as author, any digit as page (order independent)
        for arg in args:
            if author_arg is None and not arg.isdigit():
                author_arg = arg
            elif arg.isdigit():
                try:
                    page = int(arg)
                except Exception:
                    page = 1

        if author_arg:
            author = author_arg

        # Filter by author if provided (case-insensitive)
        if author:
            images = [img for img in images if author.lower() in img.get("author", "").lower()]

        # Calculate max_page after filtering
        max_page = (len(images) - 1) // PER_PAGE + 1

        if not images:
            await ctx.send("No images found for this filter.", ephemeral=True)
            return

        # Clamp page to valid range to avoid errors
        page = max(1, min(page, max_page))

        embeds = make_gallery_embeds(images, page, PER_PAGE)
        view = GalleryView(images, page, PER_PAGE)

        if isinstance(ctx, commands.Context):
            await ctx.send(embeds=embeds, view=view)
        else:
            await ctx.response.send_message(embeds=embeds, view=view)

    @gallery.autocomplete("author")
    async def author_autocomplete(self, interaction: discord.Interaction, current: str):
        """
        Provides autocomplete suggestions for the author argument in the slash command.
        """
        authors = await self.get_authors()
        return [
            app_commands.Choice(name=a, value=a)
            for a in authors if current.lower() in a.lower()
        ][:25]

async def setup(Bot: commands.Bot):
    """
    Async setup function for this cog.
    """
    await Bot.add_cog(Gallery(Bot))