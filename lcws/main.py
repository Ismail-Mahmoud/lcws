import rich_click as click
from click import Choice, Context, Parameter, prompt, style
from rich.console import Console

from lcws.github import upload_to_github
from lcws.problem import Problem
from lcws.scraper import Scraper
from lcws.url_utils import parse_url, validate_url


def url_callback(ctx: Context, param: Parameter, url: str):
    """Parse and validate url"""
    with Console().status("[bold green]Parsing and validating url..."):
        url += "/" if url[-1] != "/" else ""
        problem_url, submission_url = parse_url(url)
        validate_url(problem_url)

        ctx.params["problem_url"] = problem_url
        ctx.params["submission_url"] = submission_url

        return url


@click.command()
@click.argument("url", type=str, required=True, callback=url_callback)
@click.option("--browser", type=Choice(["firefox", "chrome"]), default="firefox", show_default=True,
              help="Web browser to be used.")
@click.option("--show", is_flag=True, default=False,
              help="Show browser window and actions taken by the web driver.")
@click.option("--timeout", type=int, default=15, show_default=True,
              help="Number of seconds to wait for a web element to load before timing out.")
def cli(url, browser, show, timeout, problem_url, submission_url):
    """
    Fetch a LeetCode submission and upload it to GitHub.

    URL is the URL of a LeetCode problem or submission.

    If problem URL is provided, the last accepted submission will be fetched.
    """
    STATUS_STYLE = "[bold green]"

    console = Console()
    problem = Problem(url=problem_url)

    with console.status(f"{STATUS_STYLE}Initializing the web driver...") as s:
        scraper = Scraper(browser=browser, headless=not show, timeout=timeout,
                          problem_url=problem_url, submission_url=submission_url, console=console)

    with console.status(f"{STATUS_STYLE}Logging into LeetCode account...") as s:
        scraper.login()
        console.log("[green]Logged in successfully")

    with console.status(f"{STATUS_STYLE}Fetching problem title...") as s:
        problem.title = scraper.fetch_problem_title()
        console.log("[bold cyan]Problem Title:",
                    problem.title, highlight=False)

    with console.status(f"{STATUS_STYLE}Fetching solution details...") as s:
        problem.solution_code, problem.solution_language = scraper.fetch_solution_details()
        console.log("[bold cyan]Solution Language:",
                    problem.solution_language)
        console.log(problem.solution_code, markup=False)

    solution_filename = prompt(
        style("Solution file name:", fg="yellow"),
        default=problem.solution_filename, prompt_suffix="? ")
    commit_message = prompt(
        style("Commit message:", fg="yellow"),
        default=f"add LeetCode {problem._id} (by lcws)", prompt_suffix="? ")

    with console.status(f"{STATUS_STYLE}Uploading solution to Github...") as s:
        commit_url = upload_to_github(
            problem.solution_code, solution_filename, commit_message)
        console.log("[green]Successfully uploaded to Gitub:", commit_url)


if __name__ == "__main__":
    cli()
