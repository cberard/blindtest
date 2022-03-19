"""
Entry point for blind test
```
python -m blindtest sum 1 3
"""
import typer

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
    dest_path: str = typer.Argument(
        "./data/singers.json", help="Path for singers file"
    ),
):
    crawl_singer(dest_path=dest_path)


if __name__ == "__main__":
    app()
