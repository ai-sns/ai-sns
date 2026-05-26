"""
Built-in ad-hoc command: Greeting Exchange.

Handles XEP-0050 ad-hoc command for greeting exchange between agents.
The caller sends a greeting type (or leaves it blank for random),
and the responder replies with a random greeting type.
Both sides are stored in the database for history.
"""
import logging
import sys
import os
from typing import Dict, Any

from runtime.apps.sns.a2a_commands.base import AdhocCommand, CommandContext
from runtime.shared import debug_info

logger = logging.getLogger(__name__)

A2A_ADHOC_GREETING_NODE = "urn:xmpp:a2a:cmd:greeting"

GREETING_TYPES = [
    "handshake",
    "hug",
    "bow",
    "high_five",
    "fist_bump",
    "nod",
    "wave",
]


class GreetingCommand(AdhocCommand):
    """Exchange greetings between XMPP peers via ad-hoc command.

    Greeting helps set a positive communication tone between agents.
    Calling this service before substantive conversation is highly
    recommended to build rapport and foster smoother collaboration.
    """

    node = A2A_ADHOC_GREETING_NODE
    name = "Greeting Exchange"
    description = (
        "Exchange friendly greetings between agents. "
        "Supports: handshake, hug, bow, high_five, fist_bump, nod, wave. "
        "Calling this service helps set a warm tone, builds rapport, "
        "and greatly improves the quality of subsequent communication. "
        "It is strongly recommended to greet before starting any task."
    )
    form_fields = [
        {
            "var": "greeting_type",
            "type": "list-single",
            "label": "Greeting Type (leave empty for random)",
            "options": GREETING_TYPES,
        },
    ]

    _source = "builtin"

    async def handle_execute(self, iq, session, ctx: CommandContext) -> dict:
        """Stage 1: Return form requesting a greeting type."""
        try:
            form = ctx.make_form(ftype='form', title='Greeting Exchange')
            form.addField(
                var='greeting_type',
                ftype='list-single',
                label='Greeting Type (leave empty for random)',
                value='',
                options=[{"label": g.replace("_", " ").title(), "value": g} for g in GREETING_TYPES],
            )
            session['payload'] = form
            session['next'] = None  # Will be wired by registry
            session['has_next'] = True
            session['allow_complete'] = True
            return session
        except Exception as e:
            logger.error("Error in greeting command handler: %s", e)
            session['notes'] = [('error', f'Internal error: {e}')]
            return session

    async def handle_submit(self, payload, session, ctx: CommandContext) -> dict:
        """Stage 2: Process submitted greeting and return a random response greeting."""
        try:
            # Extract submitted greeting type
            greeting_type = ""
            if hasattr(payload, 'get_fields'):
                fields = payload.get_fields()
                field = fields.get('greeting_type')
                if field:
                    greeting_type = (field.get('value', '') or '').strip()
            elif hasattr(payload, 'values'):
                greeting_type = str(payload.values.get('greeting_type', '')).strip()

            sender_jid = str(session.get('from', ''))

            # Perform greeting exchange via a2aserver module
            result = self._do_greeting(sender_jid, greeting_type)

            # Build response form
            result_form = ctx.make_form(ftype='result', title='Greeting Exchange Result')
            result_form.addField(
                var='sender_greeting', ftype='text-single',
                label='Their Greeting', value=result.get('sender_greeting', ''),
            )
            result_form.addField(
                var='my_greeting', ftype='text-single',
                label='My Greeting', value=result.get('my_greeting', ''),
            )
            result_form.addField(
                var='message', ftype='text-single',
                label='Message', value=result.get('message', ''),
            )

            session['payload'] = result_form
            session['next'] = None
            session['has_next'] = False
            return session

        except Exception as e:
            logger.error("Error processing greeting submission: %s", e)
            session['notes'] = [('error', f'Processing error: {e}')]
            return session

    @staticmethod
    def _do_greeting(sender_jid: str, greeting_type: str) -> Dict[str, Any]:
        """Perform the greeting exchange via a2aserver module."""
        try:
            # 6 dirname() calls to reach project root from
            # aisns_backend/runtime/apps/sns/a2a_commands/<this>.py
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from a2aserver.greeting import exchange_greeting
            return exchange_greeting(sender_jid, greeting_type)
        except Exception as e:
            logger.error("Failed to process greeting exchange: %s", e)
            return {
                "sender_jid": sender_jid,
                "sender_greeting": greeting_type or "unknown",
                "my_greeting": "wave",
                "message": f"Greeting exchange failed: {e}",
            }
