import asyncio
import httpx
import sys
import io
from pathlib import Path
from typing import Optional

import click
from openai import AsyncOpenAI

from processor.separate_processors.summarizer import AsyncTextSummarizer
from processor.separate_processors.test_maker import AsyncTestMaker
from processor.separate_processors.asr import AsyncAudioTranscriber
from processor.schemas import ProcessorResponseModel
import base64

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ProcessorTester:
    def __init__(self):
        self.client = AsyncOpenAI(
            http_client=httpx.AsyncClient(
                trust_env=False,
            ),
        )
        self.summarizer = AsyncTextSummarizer(self.client)
        self.test_maker = AsyncTestMaker(self.client)
        self.asr = AsyncAudioTranscriber(self.client)

    async def test_summarizer(self, text: str):
        click.echo(click.style("Testing AsyncTextSummarizer...", fg="blue", bold=True))
        try:
            result = await self.summarizer(text)
            click.echo(click.style("\n[+] Summarizer Result:", fg="green", bold=True))
            click.echo(f"\nTitle: {result.ai_response.title}")
            click.echo(f"\nSummary:\n{result.ai_response.text}")
            return result
        except Exception as e:
            click.echo(click.style(f"[-] Error: {str(e)}", fg="red"), err=True)
            return None

    async def test_test_maker(self, text: str):
        click.echo(click.style("\nTesting AsyncTestMaker...", fg="blue", bold=True))
        try:
            result = await self.test_maker(text)
            click.echo(click.style("\n[+] Test Maker Result:", fg="green", bold=True))
            if result.test_samples:
                for idx, sample in enumerate(result.test_samples, 1):
                    click.echo(f"\nQuestion {idx}: {sample.question}")
                    click.echo(f"Answer: {sample.answer}")
            else:
                click.echo("No test samples generated")
            return result
        except Exception as e:
            click.echo(click.style(f"[-] Error: {str(e)}", fg="red"), err=True)
            return None

    async def test_asr(self, audio_file: str):
        click.echo(click.style("Testing AsyncAudioTranscriber...", fg="blue", bold=True))
        try:
            path = Path(audio_file)
            if not path.exists():
                click.echo(click.style(f"[-] Audio file not found: {audio_file}", fg="red"), err=True)
                return None

            with open(audio_file, "rb") as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode()

            result = await self.asr(audio_base64=audio_base64)
            click.echo(click.style("\n[+] ASR Result:", fg="green", bold=True))
            click.echo(f"\nTranscription:\n{result}")
            return result
        except Exception as e:
            click.echo(click.style(f"[-] Error: {str(e)}", fg="red"), err=True)
            return None

    async def test_all(self, text: str) -> Optional[ProcessorResponseModel]:
        summarizer_result = await self.test_summarizer(text)
        test_maker_result = await self.test_test_maker(text)

        if summarizer_result and test_maker_result:
            response = ProcessorResponseModel(
                summarizer_response=summarizer_result,
                test_maker_response=test_maker_result,
            )
            click.echo(click.style("\n✓ All tests completed successfully!", fg="green", bold=True))
            return response
        return None


def read_input(prompt: str) -> str:
    click.echo(prompt)
    click.echo("(Press Ctrl+D or Ctrl+Z then Enter to finish)")
    lines = []
    try:
        while True:
            line = click.prompt("", prompt_suffix="", default="")
            if line or lines:
                lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def read_file(file_path: str) -> Optional[str]:
    try:
        path = Path(file_path)
        if not path.exists():
            click.echo(click.style(f"✗ File not found: {file_path}", fg="red"), err=True)
            return None
        return path.read_text(encoding="utf-8")
    except Exception as e:
        click.echo(click.style(f"✗ Error reading file: {str(e)}", fg="red"), err=True)
        return None


@click.group()
def cli():
    pass


@cli.command()
@click.option("--text", "-t", help="Text to process")
@click.option("--file", "-f", type=click.Path(exists=False), help="File path to read text from")
@click.option("--audio", "-a", type=click.Path(exists=False), help="Audio file path for ASR")
@click.option(
    "--processor",
    "-p",
    type=click.Choice(["summarizer", "test-maker", "asr", "all"], case_sensitive=False),
    default="all",
    help="Which processor to test",
)
def test(text: Optional[str], file: Optional[str], audio: Optional[str], processor: str):
    tester = ProcessorTester()

    try:
        if processor.lower() == "summarizer":
            if text:
                input_text = text
            elif file:
                input_text = read_file(file)
                if not input_text:
                    sys.exit(1)
            else:
                input_text = read_input("Enter text to process:")
                if not input_text.strip():
                    click.echo(click.style("✗ No input provided", fg="red"), err=True)
                    sys.exit(1)
            asyncio.run(tester.test_summarizer(input_text))

        elif processor.lower() == "test-maker":
            if text:
                input_text = text
            elif file:
                input_text = read_file(file)
                if not input_text:
                    sys.exit(1)
            else:
                input_text = read_input("Enter text to process:")
                if not input_text.strip():
                    click.echo(click.style("✗ No input provided", fg="red"), err=True)
                    sys.exit(1)
            asyncio.run(tester.test_test_maker(input_text))

        elif processor.lower() == "asr":
            audio_file = audio or click.prompt("Enter audio file path")
            asyncio.run(tester.test_asr(audio_file))

        else:
            if text:
                input_text = text
            elif file:
                input_text = read_file(file)
                if not input_text:
                    sys.exit(1)
            else:
                input_text = read_input("Enter text to process:")
                if not input_text.strip():
                    click.echo(click.style("✗ No input provided", fg="red"), err=True)
                    sys.exit(1)
            asyncio.run(tester.test_all(input_text))

    except KeyboardInterrupt:
        click.echo(click.style("\n✗ Interrupted by user", fg="yellow"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Unexpected error: {str(e)}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
def interactive():
    tester = ProcessorTester()

    while True:
        click.echo("\n" + click.style("Options:", fg="cyan", bold=True))
        click.echo("1. Test Summarizer")
        click.echo("2. Test Test Maker")
        click.echo("3. Test ASR")
        click.echo("4. Test All (text-based)")
        click.echo("5. Exit")

        choice = click.prompt("Select option", type=click.Choice(["1", "2", "3", "4", "5"]))

        try:
            if choice == "1":
                input_method = click.prompt("Input method", type=click.Choice(["text", "file"]))
                if input_method == "text":
                    input_text = read_input("Enter text to process:")
                else:
                    file_path = click.prompt("Enter file path")
                    input_text = read_file(file_path)
                    if not input_text:
                        continue
                if input_text.strip():
                    asyncio.run(tester.test_summarizer(input_text))
                else:
                    click.echo(click.style("✗ No text provided", fg="red"), err=True)

            elif choice == "2":
                input_method = click.prompt("Input method", type=click.Choice(["text", "file"]))
                if input_method == "text":
                    input_text = read_input("Enter text to process:")
                else:
                    file_path = click.prompt("Enter file path")
                    input_text = read_file(file_path)
                    if not input_text:
                        continue
                if input_text.strip():
                    asyncio.run(tester.test_test_maker(input_text))
                else:
                    click.echo(click.style("✗ No text provided", fg="red"), err=True)

            elif choice == "3":
                audio_path = click.prompt("Enter audio file path")
                asyncio.run(tester.test_asr(audio_path))

            elif choice == "4":
                input_method = click.prompt("Input method", type=click.Choice(["text", "file"]))
                if input_method == "text":
                    input_text = read_input("Enter text to process:")
                else:
                    file_path = click.prompt("Enter file path")
                    input_text = read_file(file_path)
                    if not input_text:
                        continue
                if input_text.strip():
                    asyncio.run(tester.test_all(input_text))
                else:
                    click.echo(click.style("✗ No text provided", fg="red"), err=True)

            elif choice == "5":
                click.echo(click.style("Goodbye!", fg="green"))
                break

        except KeyboardInterrupt:
            click.echo(click.style("\n✗ Interrupted by user", fg="yellow"), err=True)
            break
        except Exception as e:
            click.echo(click.style(f"✗ Error: {str(e)}", fg="red"), err=True)


def main():
    cli()


if __name__ == "__main__":
    main()
