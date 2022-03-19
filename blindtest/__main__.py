"""
Entry point for blind test 
```
python -m blindtest sum 1 3
"""
import typer

app = typer.Typer(help="blindtest")


@app.command("pow")
def pow(x: int):
    typer.echo(f"Pow of {x} is {x**2}")


@app.command("sum")
def sum(
    a: int = typer.Argument(..., help="First interger to sum"),
    b: int = typer.Argument(..., help="Second interger to sum"),
):
    typer.echo(f"Sum of {a} and {b} is {a+b}")


if __name__ == "__main__":
    app()
