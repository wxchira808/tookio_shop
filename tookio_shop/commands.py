"""
Bench commands for Tookio Shop
"""

import click


def get_commands():
    """Return list of commands defined in this module"""
    return [
        tookio_shop,
    ]


@click.group("tookio-shop")
def tookio_shop():
    """Tookio Shop commands"""
    pass


@tookio_shop.command("build-shop-ui")
@click.option("--dev", is_flag=True, help="Build in development mode")
def build_shop_ui(dev):
    """Build the Shop Vue UI"""
    import os
    import subprocess
    from pathlib import Path

    shop_dir = Path(__file__).parent / "Shop"
    if not shop_dir.exists():
        click.echo("Shop directory not found")
        return

    os.chdir(shop_dir)

    # Install dependencies if node_modules doesn't exist
    if not (shop_dir / "node_modules").exists():
        click.echo("Installing dependencies...")
        subprocess.run(["npm", "install"], check=True)

    # Build the app
    click.echo("Building Shop UI...")
    if dev:
        subprocess.run(["npm", "run", "dev"], check=True)
    else:
        subprocess.run(["npm", "run", "build"], check=True)

    click.echo("Shop UI built successfully!")


@tookio_shop.command("setup-shop-ui")
def setup_shop_ui():
    """Setup the Shop Vue UI (install deps and build)"""
    import os
    import subprocess
    from pathlib import Path

    shop_dir = Path(__file__).parent / "Shop"
    if not shop_dir.exists():
        click.echo("Shop directory not found")
        return

    os.chdir(shop_dir)

    click.echo("Setting up Shop UI...")
    subprocess.run(["npm", "install"], check=True)
    subprocess.run(["npm", "run", "build"], check=True)

    click.echo("Shop UI setup complete!")