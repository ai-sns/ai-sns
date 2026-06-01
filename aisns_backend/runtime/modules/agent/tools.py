from datetime import datetime
from typing import Annotated, Literal
from runtime.shared import debug_info


def read_skill(skill_key: str) -> str:
    """Read the full Markdown content of a DocSkill (SKILL.md) by its key.

    A DocSkill is a piece of documented knowledge / instructions registered
    in this system. Each skill is identified by a unique `skill_key` (for
    example "weather.report" or "sns.publish"). This tool returns the raw
    Markdown body of that skill so you, the assistant, can read its
    instructions before answering or before deciding whether to actually
    execute it via `run_doc_skill`.

    When to use:
        - The user requests something that matches an enabled DocSkill and
          you need to learn how that skill should be performed.
        - You want to inspect the skill's description, inputs, or steps
          before calling `run_doc_skill`.

    Behavior notes:
        - If the skill is not found (or not enabled for the current agent),
          a short error string starting with "Error:" is returned. Do not
          try to "guess" the content in that case — tell the user the
          skill is unavailable.
        - If the skill declares an executable runner, the returned text
          will include a trailing hint instructing you to follow up with
          `run_doc_skill(skill_key=...)` once you have understood it.

    Parameters:
        skill_key (str): The unique DocSkill key to load. Must match
            exactly an existing skill registered in the system.

    Returns:
        str: The Markdown content of the skill, optionally with a
        runner-hint appended; or an "Error: ..." string when not found.
    """
    md = None
    try:
        from runtime.modules.skills_registry.service import get_docskills_service

        service = get_docskills_service()
        md = service.read_skill_markdown(skill_key)
    except Exception:
        md = None

    if md is None:
        return f"Error: skill not found: {skill_key}"

    try:
        from runtime.modules.skills_registry.service import get_docskills_service

        info = get_docskills_service().get_skill(skill_key)
        runner = (info or {}).get('runner') if isinstance(info, dict) else None
        if isinstance(runner, dict) and runner.get('kind'):
            md = (
                (md or "")
                + "\n\n---\n\n"
                + "If this skill should be executed, call run_doc_skill with this skill_key and then answer the user based on the execution result."
            )
    except Exception:
        pass

    return md
