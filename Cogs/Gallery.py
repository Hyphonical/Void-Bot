# 👾 Discord modules
import discord
from discord.ext import commands
from discord import app_commands

# 🌐 Web modules
import aiohttp

# 🗓️ Date modules
from datetime import datetime

# 📥 Custom modules
from Utils.Logger import Logger

# 🔍 Fuzzy matching
import difflib

# ⚙️ Settings
from Config import FuzzyMatchingThreshold, BotName

GALLERY_URL = "https://gallery.voidtales.win/images.json"
BASE_URL = "https://gallery.voidtales.win"
PER_PAGE = 1  # 🖼️ Changed to 1 image per page for better overview

# 🖼️ Create embeds for gallery images
STAFF_AUTHORS = ["shinsnowly", ".inventory", "hyphonical", "razorbl8de"]  # Add more staff names as needed

def make_gallery_embeds(images, page, per_page, author=None):
    """
    📦 Creates a list of Discord embeds for the images on the current page.
    Each page shows one image with a full-size preview.
    If author is specified, include it in the title to indicate filtered images.
    """
    start = (page - 1) * per_page
    end = start + per_page
    page_images = images[start:end]
    embeds = []

    max_page = (len(images) - 1) // per_page + 1
    # 🏷️ Header embed showing the current page and total pages, with author if filtered
    title = f"🖼️ VoidTales Gallery"
    if author:
        title += f" - Images by {author}"
    title += f" Page {page}/{max_page} 🌌"
    header_embed = discord.Embed(
        title=title,
        description=(
            "🌐 *Browse images on [gallery.voidtales.win](https://gallery.voidtales.win)*\n"
            "📸 *Upload your own in [#breathtaking-screenshots](https://discord.com/channels/1264616683671388252/1264644697155043398)*"
        ),
        color=0xA0D6B4
    )
    embeds.append(header_embed)

    # 🔗 Base URL for delete links (adjust if needed)
    delete_base_url = "https://n8n.hzwd.xyz/webhook/delete-image"

    for img in page_images:  # Only one image per page
        img_id = img.get("id", "")
        # 🌐 Use the full image URL for display
        url = img["imageUrl"] if img["imageUrl"].startswith("http") else BASE_URL + img["imageUrl"]
        # 🔗 Link to the gallery page for this image
        gallery_link = f"{BASE_URL}/#img-{img_id}"
        # 🗑️ Link to delete the image via n8n webhook
        delete_link = f"{delete_base_url}?imageId={img_id}"

        # 🗓️ Format date to human-readable with AM/PM
        date_str = img.get('date', '')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            except Exception:
                formatted_date = 'Unknown'
        else:
            formatted_date = 'Unknown'

        author_name = img.get("author", "Unknown")
        is_staff = img.get("isStaff", False) or author_name.lower() in [a.lower() for a in STAFF_AUTHORS]
        staff_text = "⭐ Staff Image\n" if is_staff else ""

        embed = discord.Embed(
            title=f"Title: {img.get('title', 'Image')}",
            description=(
                f'{staff_text}Author: {author_name}\n'
                f'[🌐 Open in Gallery]({gallery_link}) — [🗑️ Delete this image]({delete_link})'
            ),
            color=0xA0D6B4,
        )
        # 📝 Add caption if available
        if img.get("caption"):
            embed.add_field(name="Caption", value=img["caption"], inline=False)
        # 🖼️ Set the full-size image
        embed.set_image(url=url)
        # 🏷️ Add ID, date, and bot name to footer
        embed.set_footer(text=f"ID: {img_id} — Date: {formatted_date} — {BotName}")
        embeds.append(embed)
    return embeds

# 📄 Modal for jumping to a specific page
class GoToPageModal(discord.ui.Modal):
    """
    📄 Modal for entering a page number to jump to.
    """
    def __init__(self, view: 'GalleryView'):
        super().__init__(title="Go to Page")
        self.view = view
        self.page_input = discord.ui.TextInput(
            label="Enter page number",
            placeholder=f"1 to {view.max_page}",
            required=True,
            max_length=10
        )
        self.add_item(self.page_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            page = int(self.page_input.value)
            if 1 <= page <= self.view.max_page:
                self.view.page = page
                self.view.update_buttons()
                embeds = make_gallery_embeds(self.view.images, self.view.page, self.view.per_page, self.view.author)
                await interaction.response.edit_message(embeds=embeds, view=self.view)
            else:
                await interaction.response.send_message(f"Invalid page number. Please enter a number between 1 and {self.view.max_page}.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

# 🎛️ Gallery navigation view with buttons
class GalleryView(discord.ui.View):
    """
    🎛️ Discord UI View for gallery navigation.
    Provides Previous, Next, Switch View, Go to Page, and Reload buttons.
    """
    def __init__(self, images, page=1, per_page=PER_PAGE, author=None, ctx=None):
        super().__init__(timeout=10800)  # ⏳ Set timeout to 3 hours (3*60*60 seconds)
        self.images = images
        self.page = page
        self.per_page = per_page
        self.author = author  # Store author for title updates
        self.max_page = (len(images) - 1) // per_page + 1
        self.ctx = ctx  # Store context for reload
        self.update_buttons()

    def update_buttons(self):
        prev_button: discord.ui.Button = self.children[0]
        next_button: discord.ui.Button = self.children[1]
        prev_button.style = discord.ButtonStyle.primary
        next_button.style = discord.ButtonStyle.primary
        prev_button.disabled = False
        next_button.disabled = False

    @discord.ui.button(label="⏮️ Previous", style=discord.ButtonStyle.primary, row=0)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
        else:
            self.page = self.max_page
        self.update_buttons()
        embeds = make_gallery_embeds(self.images, self.page, self.per_page, self.author)
        await interaction.response.edit_message(embeds=embeds, view=self)

    @discord.ui.button(label="Next ⏭️", style=discord.ButtonStyle.primary, row=0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
        else:
            self.page = 1
        self.update_buttons()
        embeds = make_gallery_embeds(self.images, self.page, self.per_page, self.author)
        await interaction.response.edit_message(embeds=embeds, view=self)

    @discord.ui.button(label="🔄 Switch View", style=discord.ButtonStyle.secondary, row=0)
    async def switch_view(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.per_page = 3 if self.per_page == 1 else 1
        self.max_page = (len(self.images) - 1) // self.per_page + 1
        self.page = max(1, min(self.page, self.max_page))
        self.update_buttons()
        embeds = make_gallery_embeds(self.images, self.page, self.per_page, self.author)
        await interaction.response.edit_message(embeds=embeds, view=self)

    @discord.ui.button(label="📄 Go to Page", style=discord.ButtonStyle.secondary, row=0)
    async def go_to_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GoToPageModal(self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔃 Reload", style=discord.ButtonStyle.secondary, row=0)
    async def reload(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        🔃 Reload images.json and update the gallery view.
        """
        cog = interaction.client.get_cog("Gallery")
        if cog:
            images = await cog.get_images()
            # 🗓️ Sort images by ISO date string, newest first (same as in command)
            def parse_date(img):
                try:
                    return datetime.fromisoformat(img.get("date", ""))
                except Exception:
                    return datetime.min
            images.sort(key=parse_date, reverse=True)
            # Filter by author if needed
            if self.author:
                images = [img for img in images if self.author.lower() in img.get("author", "").lower()]
            self.images = images
            self.max_page = (len(images) - 1) // self.per_page + 1
            self.page = max(1, min(self.page, self.max_page))
            self.update_buttons()
            embeds = make_gallery_embeds(self.images, self.page, self.per_page, self.author)
            await interaction.response.edit_message(embeds=embeds, view=self)
        else:
            await interaction.response.send_message("Could not reload images.", ephemeral=True)

# 🧩 Gallery Cog
class Gallery(commands.Cog):
    """
    🧩 Discord Cog for the gallery command.
    Fetches images from the gallery API, sorts them by date, and displays them with pagination.
    """
    def __init__(self, Bot: commands.Bot):
        self.Bot = Bot

    async def get_images(self):
        """
        🌐 Fetches the images from the gallery API.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(GALLERY_URL) as resp:
                return await resp.json()

    async def get_authors(self):
        """
        🏷️ Returns a sorted list of unique authors from the gallery images.
        """
        images = await self.get_images()
        return sorted(set(img.get("author", "Unknown") for img in images if img.get("author")))

    @commands.hybrid_command(
        name="gallery",
        description="Shows images from the Void Tales Gallery",
        aliases=["images", "gallery-test"]  # 🧪 Added "gallery-test" alias for testing
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
        !gallery-test              -> same as !gallery
        """
        # 💖 Log the usage with [Gallery] for highlighting
        Logger.info('[Gallery] command used by %s (ID: %s) with args: page_or_author=%s, author=%s', ctx.author, ctx.author.id, page_or_author, author)

        images = await self.get_images()

        # 🗓️ Sort images by ISO date string, newest first
        def parse_date(img):
            try:
                return datetime.fromisoformat(img.get("date", ""))
            except Exception:
                return datetime.min

        images.sort(key=parse_date, reverse=True)

        # 🧮 Robust argument parsing for both prefix and slash commands
        page = 1
        author_arg = None

        # 🗃️ Gather all provided arguments
        args = []
        if page_or_author:
            args.append(str(page_or_author))
        if author:
            args.append(str(author))

        # 🔍 Parse arguments: first non-digit as author, any digit as page (order independent)
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

        # 🏷️ Filter by author if provided (case-insensitive)
        if author:
            images = [img for img in images if author.lower() in img.get("author", "").lower()]

        # 🧮 Calculate max_page after filtering
        max_page = (len(images) - 1) // PER_PAGE + 1

        # 🚫 No images found
        if not images:
            await ctx.send("No images found for this filter.", ephemeral=True)
            return

        # 🔢 Clamp page to valid range to avoid errors
        page = max(1, min(page, max_page))

        embeds = make_gallery_embeds(images, page, PER_PAGE, author)
        view = GalleryView(images, page, PER_PAGE, author, ctx)

        # 💬 Send embeds and view
        if isinstance(ctx, commands.Context):
            await ctx.send(embeds=embeds, view=view)
        else:
            await ctx.response.send_message(embeds=embeds, view=view)

    @gallery.autocomplete("author")
    async def author_autocomplete(self, interaction: discord.Interaction, current: str):
        """
        💡 Provides autocomplete suggestions for the author argument in the slash command.
        Uses fuzzy matching to tolerate typos and suggest similar author names.
        """
        authors = await self.get_authors()
        # 🔍 Use fuzzy matching to find close matches, tolerating typos
        matches = difflib.get_close_matches(current, authors, n=25, cutoff=FuzzyMatchingThreshold)
        return [
            app_commands.Choice(name=a, value=a)
            for a in matches
        ]

# ⚙️ Async setup function for this cog
async def setup(Bot: commands.Bot):
    await Bot.add_cog(Gallery(Bot))