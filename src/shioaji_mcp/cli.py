"""Interactive CLI for Shioaji MCP - User-friendly command line interface."""

from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from .utils.auth import auth_manager

app = typer.Typer(
    name="shioaji-cli",
    help="Shioaji Trading CLI - User-friendly command line interface",
    add_completion=False,
)
console = Console()


def check_connection() -> bool:
    """Check if connected to Shioaji API."""
    if not auth_manager.is_connected():
        console.print("[red]❌ Not connected to Shioaji API[/red]")
        console.print(
            "[yellow]Please set SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY environment variables[/yellow]"
        )
        return False
    return True


@app.command()
def account() -> None:
    """Show account information."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()
        accounts = api.list_accounts()

        # Create table
        table = Table(
            title="Account Information", show_header=True, header_style="bold magenta"
        )
        table.add_column("Account ID", style="cyan")
        table.add_column("Broker ID", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Signed", style="blue")

        for account in accounts:
            # Determine account type
            acc_type = "unknown"
            if hasattr(account, "account_type"):
                acc_type_str = str(account.account_type).upper()
                if "STOCK" in acc_type_str or acc_type_str == "S":
                    acc_type = "Stock 證券"
                elif "FUTURE" in acc_type_str or acc_type_str == "F":
                    acc_type = "Futures 期貨"
                elif acc_type_str == "H" or "HONG" in acc_type_str:
                    acc_type = "HK Stock 港股"

            signed_status = "✅ Yes" if account.signed else "❌ No"

            table.add_row(
                account.account_id,
                account.broker_id,
                acc_type,
                signed_status,
            )

        console.print(table)

        # Check if any unsigned accounts
        unsigned_count = sum(1 for acc in accounts if not acc.signed)
        if unsigned_count > 0:
            console.print(
                f"\n[yellow]⚠️  You have {unsigned_count} unsigned account(s). "
                "Please sign service terms using: shioaji-cli terms sign[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def quote(
    symbol: str = typer.Argument(..., help="Stock symbol (e.g., 2330 for TSMC)"),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed information"
    ),
) -> None:
    """Get real-time quote for a stock."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()

        # Search for contract
        contract = api.Contracts.Stocks.get(symbol)
        if not contract:
            console.print(f"[red]❌ Contract {symbol} not found[/red]")
            raise typer.Exit(1)

        # Get snapshot
        snapshot = api.snapshots([contract])[0]

        # Display basic info
        console.print(
            Panel(
                f"[bold cyan]{contract.name}[/bold cyan] ({symbol})\n\n"
                f"[bold]Price:[/bold] [green]{snapshot.close:,.2f}[/green]\n"
                f"[bold]Change:[/bold] {snapshot.close - snapshot.open:+,.2f} "
                f"({(snapshot.close - snapshot.open) / snapshot.open * 100:+.2f}%)\n"
                f"[bold]Volume:[/bold] {snapshot.volume:,}",
                title="📊 Real-time Quote",
                border_style="blue",
            )
        )

        if detailed:
            # Create detailed table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="yellow")

            table.add_row("Open", f"{snapshot.open:,.2f}")
            table.add_row("High", f"{snapshot.high:,.2f}")
            table.add_row("Low", f"{snapshot.low:,.2f}")
            table.add_row("Close", f"{snapshot.close:,.2f}")
            table.add_row("Volume", f"{snapshot.volume:,}")
            table.add_row(
                "Bid Price", f"{snapshot.bid_price[0] if snapshot.bid_price else 'N/A'}"
            )
            table.add_row(
                "Ask Price", f"{snapshot.ask_price[0] if snapshot.ask_price else 'N/A'}"
            )

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Search keyword"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to show"),
) -> None:
    """Search for contracts."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()

        # Search in stocks
        results = []
        for symbol, contract in api.Contracts.Stocks.items():
            if keyword.upper() in symbol.upper() or keyword in contract.name:
                results.append(
                    {
                        "code": symbol,
                        "name": contract.name,
                        "exchange": contract.exchange,
                        "category": contract.category,
                    }
                )
                if len(results) >= limit:
                    break

        if not results:
            console.print(f"[yellow]No contracts found for '{keyword}'[/yellow]")
            return

        # Create table
        table = Table(
            title=f"Search Results for '{keyword}'",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Code", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Exchange", style="yellow")
        table.add_column("Category", style="blue")

        for result in results:
            table.add_row(
                result["code"], result["name"], result["exchange"], result["category"]
            )

        console.print(table)
        console.print(
            f"\n[dim]Showing {len(results)} results (use --limit to show more)[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def positions(
    account_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Account type: all, stock, futures",
    ),
) -> None:
    """Show current positions."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()

        # Get positions based on account type
        stock_positions = []
        futures_positions = []

        if account_type in ["all", "stock"]:
            try:
                stock_list = api.list_positions(api.stock_account)
                stock_positions = stock_list if stock_list else []
            except Exception as e:
                console.print(
                    f"[yellow]⚠️  Could not fetch stock positions: {e}[/yellow]"
                )

        if account_type in ["all", "futures"]:
            try:
                futures_list = api.list_positions(api.futopt_account)
                futures_positions = futures_list if futures_list else []
            except Exception as e:
                console.print(
                    f"[yellow]⚠️  Could not fetch futures positions: {e}[/yellow]"
                )

        # Display stock positions
        if stock_positions:
            table = Table(
                title="📈 Stock Positions",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Code", style="cyan")
            table.add_column("Quantity", style="yellow", justify="right")
            table.add_column("Avg Cost", style="green", justify="right")
            table.add_column("P&L", style="blue", justify="right")

            for pos in stock_positions:
                table.add_row(
                    pos.code,
                    f"{pos.quantity:,}",
                    f"{pos.price:,.2f}",
                    f"{pos.pnl:+,.2f}",
                )

            console.print(table)
        elif account_type in ["all", "stock"]:
            console.print("[dim]No stock positions[/dim]")

        # Display futures positions
        if futures_positions:
            table = Table(
                title="📊 Futures Positions",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Code", style="cyan")
            table.add_column("Quantity", style="yellow", justify="right")
            table.add_column("Avg Cost", style="green", justify="right")
            table.add_column("P&L", style="blue", justify="right")

            for pos in futures_positions:
                table.add_row(
                    pos.code,
                    f"{pos.quantity:,}",
                    f"{pos.price:,.2f}",
                    f"{pos.pnl:+,.2f}",
                )

            console.print(table)
        elif account_type in ["all", "futures"]:
            console.print("[dim]No futures positions[/dim]")

        if not stock_positions and not futures_positions:
            console.print("[yellow]No positions found[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def balance(
    account_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Account type: all, stock, futures",
    ),
) -> None:
    """Show account balance."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()

        # Get stock account balance
        if account_type in ["all", "stock"]:
            try:
                stock_balance = api.account_balance()

                console.print(
                    Panel(
                        f"[bold]Available:[/bold] [green]${stock_balance.acc_balance:,.2f}[/green]\n"
                        f"[bold]Buying Power:[/bold] ${stock_balance.available_balance:,.2f}\n"
                        f"[bold]Stock Value:[/bold] ${stock_balance.stock_value:,.2f}\n"
                        f"[bold]Total:[/bold] ${stock_balance.total:,.2f}",
                        title="💰 Stock Account Balance",
                        border_style="green",
                    )
                )
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not fetch stock balance: {e}[/yellow]")

        # Get futures account balance
        if account_type in ["all", "futures"]:
            try:
                futures_balance = api.futopt_account_balance()

                console.print(
                    Panel(
                        f"[bold]Available:[/bold] [green]${futures_balance.available_balance:,.2f}[/green]\n"
                        f"[bold]Margin Used:[/bold] ${futures_balance.margin_used:,.2f}\n"
                        f"[bold]Initial Margin:[/bold] ${futures_balance.initial_margin:,.2f}\n"
                        f"[bold]Maintenance Margin:[/bold] ${futures_balance.maintenance_margin:,.2f}",
                        title="💰 Futures Account Balance",
                        border_style="blue",
                    )
                )
            except Exception as e:
                console.print(
                    f"[yellow]⚠️  Could not fetch futures balance: {e}[/yellow]"
                )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def history(
    symbol: str = typer.Argument(..., help="Stock symbol"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to fetch"),
) -> None:
    """Get historical K-bar data."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()

        # Get contract
        contract = api.Contracts.Stocks.get(symbol)
        if not contract:
            console.print(f"[red]❌ Contract {symbol} not found[/red]")
            raise typer.Exit(1)

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get K-bars
        kbars = api.kbars(
            contract=contract,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            timeout=30000,
        )

        if not kbars:
            console.print("[yellow]No historical data available[/yellow]")
            return

        # Create table
        table = Table(
            title=f"📊 Historical Data for {contract.name} ({symbol})",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Date", style="cyan")
        table.add_column("Open", style="yellow", justify="right")
        table.add_column("High", style="green", justify="right")
        table.add_column("Low", style="red", justify="right")
        table.add_column("Close", style="blue", justify="right")
        table.add_column("Volume", style="white", justify="right")

        # Show last 10 entries
        for kbar in kbars[-10:]:
            table.add_row(
                kbar.ts.strftime("%Y-%m-%d"),
                f"{kbar.Open:,.2f}",
                f"{kbar.High:,.2f}",
                f"{kbar.Low:,.2f}",
                f"{kbar.Close:,.2f}",
                f"{kbar.Volume:,}",
            )

        console.print(table)
        console.print(f"\n[dim]Showing last 10 of {len(kbars)} K-bars[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


# Terms management commands
terms_app = typer.Typer(help="Manage service terms and API testing")
app.add_typer(terms_app, name="terms")


@terms_app.command("status")
def terms_status() -> None:
    """Check service terms signing status."""
    if not check_connection():
        raise typer.Exit(1)

    try:
        api = auth_manager.get_api()
        accounts = api.list_accounts()

        # Create table
        table = Table(
            title="Service Terms Status", show_header=True, header_style="bold magenta"
        )
        table.add_column("Account ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Signed", style="blue")
        table.add_column("Status", style="green")

        all_signed = True
        for account in accounts:
            # Determine account type
            acc_type = str(account.account_type).upper()
            if "STOCK" in acc_type or acc_type == "S":
                acc_type = "Stock"
            elif "FUTURE" in acc_type or acc_type == "F":
                acc_type = "Futures"

            signed_status = "✅" if account.signed else "❌"
            status_text = "Ready" if account.signed else "Need to sign"

            if not account.signed:
                all_signed = False

            table.add_row(account.account_id, acc_type, signed_status, status_text)

        console.print(table)

        if all_signed:
            console.print(
                "\n[green]✅ All accounts are signed and ready to use[/green]"
            )
        else:
            console.print(
                "\n[yellow]⚠️  Some accounts need to sign service terms. "
                "Use 'shioaji-cli terms sign' to sign.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@terms_app.command("sign")
def terms_sign() -> None:
    """Sign service terms (interactive)."""
    if not check_connection():
        raise typer.Exit(1)

    console.print(
        Panel(
            "[bold yellow]⚠️  Service Terms Signing[/bold yellow]\n\n"
            "This will open your browser to sign the service terms.\n"
            "Please follow the instructions on the website.",
            border_style="yellow",
        )
    )

    if not Confirm.ask("Do you want to continue?"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        auth_manager.get_api()

        # This would need to implement the actual signing process
        # For now, we'll just show instructions
        console.print(
            "\n[cyan]Please visit the Sinopac Securities website to sign service terms:[/cyan]"
        )
        console.print("[link]https://www.sinotrade.com.tw/[/link]")
        console.print(
            "\n[dim]After signing, run 'shioaji-cli terms status' to verify[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def interactive() -> None:
    """Start interactive mode with menu."""
    console.print(
        Panel(
            "[bold cyan]Welcome to Shioaji Trading CLI[/bold cyan]\n\n"
            "Interactive mode - Coming soon!",
            border_style="cyan",
        )
    )
    # This would launch a full interactive TUI
    console.print(
        "[yellow]Interactive mode will be implemented with the TUI interface[/yellow]"
    )


@app.command()
def version() -> None:
    """Show version information."""
    console.print(
        Panel(
            "[bold]Shioaji MCP Server[/bold]\n"
            "[cyan]Version:[/cyan] 0.1.0\n"
            "[cyan]Python:[/cyan] 3.10+\n"
            "[cyan]Shioaji:[/cyan] 1.2.5",
            title="ℹ️  Version Info",
            border_style="blue",
        )
    )


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
