"""
Plugin ad-hoc command: Echo & Log.

Accepts a single text parameter, logs it to the backend console,
and returns it back to the caller as confirmation.
"""
import logging
from runtime.apps.sns.a2a_commands.base import AdhocCommand, CommandContext

logger = logging.getLogger(__name__)


class EchoLogCommand(AdhocCommand):
    """Receive a message, log it to console, and echo it back."""

    node = "urn:xmpp:a2a:cmd:echo_log"
    name = "Echo Log"
    description = "Accepts a message parameter, logs it to the backend console, and echoes it back."
    form_fields = [
        {
            "var": "message",
            "type": "text-single",
            "label": "Message to log",
            "default": "",
        },
    ]

    async def handle_execute(self, iq, session, ctx: CommandContext) -> dict:
        """Stage 1: Present form asking for a message."""
        form = ctx.make_form(ftype='form', title=self.name)
        form.addField(
            var='message',
            ftype='text-single',
            label='Message to log',
            value='',
        )
        session['payload'] = form
        session['next'] = None
        session['has_next'] = True
        session['allow_complete'] = True
        return session

    async def handle_submit(self, payload, session, ctx: CommandContext) -> dict:
        """Stage 2: Log the message and return confirmation."""
        # Extract submitted value
        message = ""
        if hasattr(payload, 'get_fields'):
            fields = payload.get_fields()
            fld = fields.get('message')
            if fld:
                message = (fld.get('value', '') or '').strip()
        elif hasattr(payload, 'get_values'):
            values = payload.get_values()
            message = str(values.get('message', '')).strip()

        # ====== Log to backend console ======
        logger.info("[EchoLog] Received message from %s: %s",
                    session.get('from', 'unknown'), message)
        print(f"[EchoLog] >>> {message}")  # Also print to stdout for visibility

        # Build result form
        result_form = ctx.make_form(ftype='result', title='Echo Log Result')
        result_form.addField(
            var='status', ftype='text-single',
            label='Status', value='logged',
        )
        result_form.addField(
            var='echo', ftype='text-single',
            label='Echo', value=message,
        )

        session['payload'] = result_form
        session['next'] = None
        session['has_next'] = False
        return session
