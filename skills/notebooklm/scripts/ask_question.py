#!/usr/bin/env python3
"""
Simple NotebookLM Question Interface
Based on MCP server implementation - simplified without sessions

Implements hybrid auth approach:
- Persistent browser profile (user_data_dir) for fingerprint consistency
- Manual cookie injection from state.json for session cookies (Playwright bug workaround)
See: https://github.com/microsoft/playwright/issues/36139
"""

import argparse
import sys
import time
import re
from pathlib import Path

from patchright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from notebook_manager import NotebookLibrary
from config import QUERY_INPUT_SELECTORS, RESPONSE_SELECTORS
from browser_utils import BrowserFactory, StealthUtils


# Follow-up reminder (adapted from MCP server for stateless operation)
# Since we don't have persistent sessions, we encourage comprehensive questions
FOLLOW_UP_REMINDER = (
    "\n\nEXTREMELY IMPORTANT: Is that ALL you need to know? "
    "You can always ask another question! Think about it carefully: "
    "before you reply to the user, review their original request and this answer. "
    "If anything is still unclear or missing, ask me another comprehensive question "
    "that includes all necessary context (since each question opens a new browser session)."
)

# Conservative prompt budget. NotebookLM will not submit an over-length prompt:
# its web UI greys out send past a budget, and a programmatic over-length submit
# then stalls until the answer timeout. These caps are a safe bound for prose
# (the observed UI limit is higher and word/char-coupled). Override with
# --allow-long when the caller has reason to. See references/agent-protocol.md.
MAX_PROMPT_CHARS = 1900
MAX_PROMPT_WORDS = 255


def ask_notebooklm(question: str, notebook_url: str, headless: bool = True) -> str:
    """
    Ask a question to NotebookLM

    Args:
        question: Question to ask
        notebook_url: NotebookLM notebook URL
        headless: Run browser in headless mode

    Returns:
        Answer text from NotebookLM
    """
    auth = AuthManager()

    if not auth.is_authenticated():
        print("⚠️ Not authenticated. Run: python auth_manager.py setup")
        return None

    print(f"💬 Asking: {question}")
    print(f"📚 Notebook: {notebook_url}")

    playwright = None
    context = None

    try:
        # Start playwright
        playwright = sync_playwright().start()

        # Launch persistent browser context using factory
        context = BrowserFactory.launch_persistent_context(
            playwright,
            headless=headless
        )

        # Navigate to notebook
        page = context.new_page()
        print("  🌐 Opening notebook...")
        page.goto(notebook_url, wait_until="domcontentloaded")

        # Wait for NotebookLM
        page.wait_for_url(re.compile(r"^https://notebooklm\.google\.com/"), timeout=10000)

        # Wait for query input (MCP approach)
        print("  ⏳ Waiting for query input...")
        query_element = None

        for selector in QUERY_INPUT_SELECTORS:
            try:
                query_element = page.wait_for_selector(
                    selector,
                    timeout=10000,
                    state="visible"  # Only check visibility, not disabled!
                )
                if query_element:
                    print(f"  ✓ Found input: {selector}")
                    break
            except:
                continue

        if not query_element:
            print("  ❌ Could not find query input")
            return None

        # Wait for chat panel to hydrate: poll until chat-message-pair count is
        # stable for 3 consecutive polls (~1.5s). Without this wait, the page
        # may still be loading historical chat messages when we mark the
        # baseline, causing late-arriving historical pairs to be mis-identified
        # as our new answer.
        print("  ⏳ Waiting for chat panel to hydrate...")
        prev_count = -1
        stable_baseline = 0
        hydrate_deadline = time.time() + 20
        while time.time() < hydrate_deadline:
            try:
                cur_count = page.evaluate(
                    "() => document.querySelectorAll('div.chat-message-pair').length"
                )
            except Exception:
                cur_count = 0
            if cur_count == prev_count:
                stable_baseline += 1
                if stable_baseline >= 3:
                    break
            else:
                stable_baseline = 0
                prev_count = cur_count
            time.sleep(0.5)
        print(f"  📊 Chat panel hydrated: {prev_count} pre-existing pair(s)")

        # Mark every existing chat-message-pair so we can identify the new pair
        # added in response to our submission. Identity-based selection is
        # robust to NotebookLM's non-chronological chat ordering, Studio
        # sidebar re-renders, lazy-loading, and any future DOM reshuffles —
        # `elements[-1]` was brittle for all of these because it relied on
        # document order, which NotebookLM does not guarantee maps to recency.
        marked_count = page.evaluate(
            "() => {\n"
            "  const pairs = document.querySelectorAll('div.chat-message-pair');\n"
            "  pairs.forEach(p => p.setAttribute('data-pre-submit', '1'));\n"
            "  return pairs.length;\n"
            "}"
        )
        print(f"  📊 Marked {marked_count} pre-existing chat-message-pair(s)")

        # Type question (human-like, fast)
        print("  ⏳ Typing question...")

        # Use primary selector for typing
        input_selector = QUERY_INPUT_SELECTORS[0]
        StealthUtils.human_type(page, input_selector, question)

        # Defensive: confirm the full prompt actually landed before submitting.
        # If the input enforces a maxlength, an over-length prompt is silently
        # shortened; submitting it would answer a truncated question. Fail loudly
        # instead of silently asking the wrong thing.
        try:
            typed_len = page.evaluate(
                "(sel) => { const el = document.querySelector(sel);"
                " return el ? (el.value != null ? el.value.length : el.innerText.length) : -1; }",
                input_selector,
            )
        except Exception:
            typed_len = -1
        if typed_len >= 0 and typed_len < len(question) - 2:
            print(f"  ❌ Prompt not fully entered: input holds {typed_len} of "
                  f"{len(question)} chars — likely over NotebookLM's input limit. "
                  f"Aborting before submit; shorten to ≤{MAX_PROMPT_CHARS} chars "
                  f"/ ≤{MAX_PROMPT_WORDS} words and retry.")
            return None

        # Submit
        print("  📤 Submitting...")
        page.keyboard.press("Enter")

        # Small pause
        StealthUtils.random_delay(500, 1500)

        # Wait for response: find the NEW (unmarked) chat-message-pair, then
        # poll its bot answer for text stability (3 consecutive identical polls).
        print("  ⏳ Waiting for answer...")

        answer = None
        stable_count = 0
        last_text = None
        deadline = time.time() + 120  # 2 minutes timeout
        warned_multi = False

        while time.time() < deadline:
            # Skip while NotebookLM is thinking (most reliable activity indicator)
            try:
                thinking_element = page.query_selector('div.thinking-message')
                if thinking_element and thinking_element.is_visible():
                    time.sleep(0.5)
                    continue
            except Exception:
                pass

            # Look for the new (unmarked) chat-message-pair and extract its bot answer.
            try:
                result = page.evaluate(
                    "() => {\n"
                    "  const newPairs = document.querySelectorAll('div.chat-message-pair:not([data-pre-submit])');\n"
                    "  return {\n"
                    "    count: newPairs.length,\n"
                    "    texts: Array.from(newPairs).map(p => {\n"
                    "      const bot = p.querySelector('.to-user-container .message-text-content');\n"
                    "      return bot ? bot.innerText.trim() : '';\n"
                    "    })\n"
                    "  };\n"
                    "}"
                )
            except Exception:
                result = {"count": 0, "texts": []}

            new_count = result.get("count", 0)
            new_texts = result.get("texts", [])

            if new_count == 0:
                time.sleep(0.5)
                continue
            if new_count > 1 and not warned_multi:
                print(f"  ⚠️ Multiple unmarked pairs ({new_count}); taking the first")
                warned_multi = True

            text = new_texts[0] if new_texts else ""
            if not text:
                # New pair exists but bot answer hasn't started streaming yet.
                time.sleep(0.5)
                continue

            if text == last_text:
                stable_count += 1
                # 6 consecutive identical polls × 0.5s = 3s of no change.
                # Empirically, 3 polls (1.5s) is too short — NotebookLM's
                # streaming has natural pauses (especially around verbatim-quote
                # boundaries where math equations render) that can be longer
                # than 1.5s, leading to premature capture mid-sentence. 3s of
                # stability is a robust threshold; failure mode would be NLM
                # pausing >3s mid-answer, which is rare in practice. NLM has
                # no DOM-side streaming-completion indicator we can detect
                # (verified empirically: no visible stop/generating buttons or
                # streaming-class elements at completion time).
                if stable_count >= 6:
                    answer = text
                    print(f"  📊 SETTLED  text_len={len(text)}  head={text[:100].replace(chr(10), ' ')!r}")
                    print(f"  📊 SETTLED  tail={text[-100:].replace(chr(10), ' ')!r}")
                    break
            else:
                stable_count = 0
                last_text = text

            time.sleep(0.5)

        if not answer:
            print("  ❌ Timeout waiting for answer")
            return None

        print("  ✅ Got answer!")
        # Add follow-up reminder to encourage Claude to ask more questions
        return answer + FOLLOW_UP_REMINDER

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        # Always clean up
        if context:
            try:
                context.close()
            except:
                pass

        if playwright:
            try:
                playwright.stop()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='Ask NotebookLM a question')

    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--notebook-url', help='NotebookLM notebook URL')
    parser.add_argument('--notebook-id', help='Notebook ID from library')
    parser.add_argument('--show-browser', action='store_true', help='Show browser')
    parser.add_argument('--allow-long', action='store_true',
                        help='Bypass the prompt-length guard (send an over-budget prompt anyway)')

    args = parser.parse_args()

    # Pre-flight prompt-budget guard: a predictable, fast failure instead of a
    # silent multi-message split or a 120s answer timeout on an over-length
    # prompt. --allow-long downgrades to a warning so the caller can negotiate.
    q_chars = len(args.question)
    q_words = len(args.question.split())
    if q_chars > MAX_PROMPT_CHARS or q_words > MAX_PROMPT_WORDS:
        over = f"{q_chars} chars / {q_words} words (cap ≤{MAX_PROMPT_CHARS} chars / ≤{MAX_PROMPT_WORDS} words)"
        if args.allow_long:
            print(f"⚠️  Prompt over budget: {over}; sending anyway (--allow-long). "
                  f"NotebookLM may refuse to submit it.")
        else:
            print(f"❌ Prompt over budget: {over}. NotebookLM will not submit an "
                  f"over-length prompt — shorten it or split into focused questions "
                  f"and retry. (override: --allow-long)")
            return 1

    # Resolve notebook URL
    notebook_url = args.notebook_url

    if not notebook_url and args.notebook_id:
        library = NotebookLibrary()
        notebook = library.get_notebook(args.notebook_id)
        if notebook:
            notebook_url = notebook['url']
        else:
            print(f"❌ Notebook '{args.notebook_id}' not found")
            return 1

    if not notebook_url:
        # Check for active notebook first
        library = NotebookLibrary()
        active = library.get_active_notebook()
        if active:
            notebook_url = active['url']
            print(f"📚 Using active notebook: {active['name']}")
        else:
            # Show available notebooks
            notebooks = library.list_notebooks()
            if notebooks:
                print("\n📚 Available notebooks:")
                for nb in notebooks:
                    mark = " [ACTIVE]" if nb.get('id') == library.active_notebook_id else ""
                    print(f"  {nb['id']}: {nb['name']}{mark}")
                print("\nSpecify with --notebook-id or set active:")
                print("python scripts/run.py notebook_manager.py activate --id ID")
            else:
                print("❌ No notebooks in library. Add one first:")
                print("python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS")
            return 1

    # Ask the question
    answer = ask_notebooklm(
        question=args.question,
        notebook_url=notebook_url,
        headless=not args.show_browser
    )

    if answer:
        print("\n" + "=" * 60)
        print(f"Question: {args.question}")
        print("=" * 60)
        print()
        print(answer)
        print()
        print("=" * 60)
        return 0
    else:
        print("\n❌ Failed to get answer")
        return 1


if __name__ == "__main__":
    sys.exit(main())
