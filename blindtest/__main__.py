"""
Entry point for blind test
```
python -m blindtest sum 1 3
"""
from pathlib import Path

import typer

from .scrap_data.formate_scraped_data import transform_scrapped_singers_to_csv
from .scrap_data.spiders.scrap_singers import crawl_singer

app = typer.Typer(name="blindtest")


@app.command("pow")
def pow(x: int):
    typer.echo(f"Pow of {x} is {x**2}")


@app.command("sum")
def sum(
    a: int = typer.Argument(..., help="First interger to sum"),
    b: int = typer.Argument(..., help="Second interger to sum"),
):
    typer.echo(f"Sum of {a} and {b} is {a+b}")


@app.command("get-singers")
def get_singers(
    singer_file: Path = typer.Argument(
        Path("./data/singers.csv"), help="Path for singers file"
    ),
):
    scrapped_path = Path(singer_file).with_suffix(".json")
    crawl_singer(dest_path=scrapped_path)
    transform_scrapped_singers_to_csv(
        scrapped_singer_path=scrapped_path, output_csv=singer_file
    )
    scrapped_path.unlink(missing_ok=True)


if __name__ == "__main__":
    app()
